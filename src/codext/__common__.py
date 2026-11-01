# -*- coding: UTF-8 -*-
"""Codecs registry - adding, looking up, searching and listing the codecs.

This module holds the registry of codext (``add``, ``add_map``, ``add_macro``, ``lookup``, ``register``,
 ``search``, ``list_encodings``, ...) and hooks it into the ``codecs`` module. The helpers it relies on live in
 ``utils`` (conversions, error handling, platform constants), ``text`` (text rating) and ``regex`` (generation of
 strings from a pattern) ; they are re-exported here for the codecs, which import everything from this module.
"""
import _codecs
import builtins
import codecs
import hashlib
import json
import os
import random
import re
import warnings
from encodings.aliases import aliases as ALIASES
from functools import reduce, update_wrapper
from importlib import import_module
from inspect import currentframe
from io import BytesIO
from random import randint
from types import FunctionType

# the helpers and constants moved to dedicated modules are re-exported, so that the codecs (through the star import of
#  this module) and the other modules can still import them from here
from .regex import generate_string_from_regex, generate_strings_from_regex
from .text import *
from .text import _textness
from .utils import *
from .utils import _human_keys, _input, _set_exc, _stripl


__all__ = ["add", "add_macro", "add_map", "b", "clear", "codecs", "decode", "encode", "ensure_str", "examples",
           "isb", "generate_strings_from_regex", "get_alphabet_from_mask", "handle_error", "hashlib", "i2s",
           "is_native", "list_categories", "list_encodings", "list_macros", "lookup", "maketrans", "os", "re",
           "register", "remove", "reset", "s2i", "search", "BytesIO", "_input", "_stripl", "CodecMacro",
           "DARWIN", "LANG", "LINUX", "MASKS", "UNIX", "WINDOWS"]
CODECS_REGISTRY = None
CODECS_OVERWRITTEN = []
CODECS_CATEGORIES = ["native", "custom"]
# categories that were renamed or split, with the current categories of their codecs (still accepted, with a warning)
DEPRECATED_CATEGORIES = {'crypto': ["cipher", "obfuscation"]}
CODECS_CACHE = {}

__codecs_registry = []
# caches depending on the state of the registry (cleared whenever it changes)
__guess_lists = {}
__names_table = []
__lookup_cache = {}

MACROS = {}
PERS_MACROS = {}
PERS_MACROS_FILE = os.path.expanduser("~/.codext-macros.json")


class CodecMacro(tuple):
    """Macro details when looking up the codec registry. """
    def __new__(cls, name):
        self = tuple.__new__(cls)
        self.name = name
        # get from personal macros first
        try:
            self.codecs = PERS_MACROS[name]
        except KeyError:
            try:
                self.codecs = MACROS[name]
            except KeyError:
                raise LookupError(f"unknown macro: {name}")
        if not isinstance(self.codecs, (tuple, list)):
            raise ValueError(f"bad macro list: {self.codecs}")
        self.codecs = [lookup(e, False) for e in self.codecs]  # lookup(e, False)
        self.parameters = {'name': name, 'category': "macro"}  #             ^  means that macros won't be nestable
        # test examples to check that the chain of encodings works
        for action, examples in (self.codecs[0].parameters.get('examples', {}) or {'enc-dec(': ["T3st str!"]}).items():
            if re.match(r"enc(-dec)?\(", action):
                for e in (examples.keys() if action.startswith("enc(") else examples or []):
                    rd = re.match(r"\@(i?)random(?:\{(\d+(?:,(\d+))*?)\})?$", e)
                    if rd:
                        for n in (rd.group(2) or "512").split(","):
                            s = "".join(chr(randint(0, 255)) for i in range(int(n)))
                            self.encode(s.lower() if rd.group(1) else s)
                        continue
                    self.encode(e)
        
        class Codec:
            decode = self.decode
            encode = self.encode
        
        class IncrementalEncoder(codecs.IncrementalEncoder):
            def encode(self, input, final=False):
                return b(self.encode(input, self.errors)[0])
        self.incrementalencoder = IncrementalEncoder
        
        class IncrementalDecoder(codecs.IncrementalDecoder):
            def decode(self, input, final=False):
                return ensure_str(self.decode(input, self.errors)[0])
        self.incrementaldecoder = IncrementalDecoder
        
        class StreamWriter(Codec, codecs.StreamWriter):
            charbuffertype = bytes
        self.streamwriter = StreamWriter
        
        class StreamReader(Codec, codecs.StreamReader):
            charbuffertype = bytes
        self.streamreader = StreamReader
        
        return self
    
    def decode(self, input, error="strict"):
        """ Decode with each codec in reverse order. """
        for ci in self.codecs[::-1]:
            input, l = ci.decode(input, error)
        return input, l
    
    def encode(self, input, error="strict"):
        """ Encode with each codec. """
        for ci in self.codecs:
            input, l = ci.encode(input, error)
        return input, l
    
    def __repr__(self):
        return f"<codext.CodecMacro object for encoding {self.name} at {id(self):#x}>"


# inspired from: https://stackoverflow.com/questions/10875442/possible-to-change-a-functions-repr-in-python
class Repr(object):
    def __init__(self, name, func):
        self.__name = name
        self.__func = func
        update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)
    
    def __repr__(self):
        return f"<search-function {self.__name} at {id(self):#x}>"


def _with_repr(name):
    def _wrapper(f):
        return Repr(name, f)
    return _wrapper


def add(ename, encode=None, decode=None, pattern=None, text=True, add_to_codecs=False, **kwargs):
    """ This adds a new codec to the codecs module setting its encode and/or decode functions, eventually dynamically
         naming the encoding with a pattern and with file handling.
    
    :param ename:         encoding name
    :param encode:        encoding function or None
    :param decode:        decoding function or None
    :param pattern:       pattern for dynamically naming the encoding
    :param text:          specify whether the codec is a text encoding
    :param add_to_codecs: also add the search function to the native registry
                           NB: this will make the codec available in the built-in open(...) but will make it impossible
                                to remove the codec later
    """
    remove(ename)
    if encode:
        if not isinstance(encode, FunctionType):
            raise ValueError("Bad 'encode' function")
        _set_exc(f"{exc_name(ename)}EncodeError")  # create the custom encode exception as a builtin
    if decode:
        if not isinstance(decode, FunctionType):
            raise ValueError("Bad 'decode' function")
        _set_exc(f"{exc_name(ename)}DecodeError")  # create the custom decode exception as a builtin
    if not encode and not decode:
        raise ValueError("At least one en/decoding function must be defined")
    for exc in kwargs.get('extra_exceptions', []):
        _set_exc(exc)  # create additional custom exceptions as builtins
    glob = currentframe().f_back.f_globals
    # the pattern is compiled once, as it is matched against every encoding name looked up
    rx = re.compile(pattern) if pattern else None
    # category of the codec, from the folder of the module adding it
    cat = glob.get('__file__', os.path.join("custom", "_")).split(os.path.sep)[-2].rstrip("s")
    category = kwargs.get('category', cat)
    for c in [cat, category]:
        if c not in CODECS_CATEGORIES:
            CODECS_CATEGORIES.append(c)
    # search function for the new encoding
    @_with_repr(ename)
    def getregentry(encoding):
        if encoding != ename and not (rx and rx.match(encoding)):
            return
        fenc, fdec, name = encode, decode, encoding
        # prepare CodecInfo input arguments
        if pattern:
            m, args, i = rx.match(encoding), [], 1
            try:
                while True:
                    try:
                        g = m.group(i) or ""
                        if g.isdigit() and not g.startswith("0") and (re.match(r"10+", g) or "".join(set(g)) != "01"):
                            g = int(g)
                        args += [g]
                        i += 1
                    except AttributeError:
                        # this occurs when m is None or there is an error in fenc(g) or fdec(g), meaning no match
                        if m is not None:
                            raise
                        return
            except IndexError:
                # this occurs while m is not None, but possibly no capture group that gives at least 1 group index ;
                #  in this case, if fenc/fdec is a decorated function, execute it with no arg
                if len(args) == 0:
                    from inspect import getfullargspec
                    if fenc and len(getfullargspec(fenc).args) == 1:
                        fenc = fenc()
                    if fdec and len(getfullargspec(fdec).args) == 1:
                        fdec = fdec()
                else:
                    fenc = fenc(*args) if fenc else fenc
                    fdec = fdec(*args) if fdec else fdec
        if fenc:
            fenc = fix_inout_formats(fenc)
        if fdec:
            sl, sc = getattr(fdec, '__strip__', (False, False))
            fdec = fix_inout_formats(fdec)
            if sl or sc:
                def _striplines(f):
                    def __wrapper(input, *a, **kw):
                        return f(_stripl(input, sl, sc), *a, **kw)
                    return __wrapper
                # this fixes issues with wrapped encoded inputs
                fdec = _striplines(fdec)
        
        class Codec(codecs.Codec):
            def encode(self, input, errors="strict"):
                if fenc is None:
                    raise NotImplementedError
                return fenc(input, errors)
            
            def decode(self, input, errors="strict"):
                if fdec is None:
                    raise NotImplementedError
                return fdec(input, errors)
        
        class IncrementalEncoder(codecs.IncrementalEncoder):
            def encode(self, input, final=False):
                if fenc is None:
                    raise NotImplementedError
                return b(fenc(input, self.errors)[0])
        
        class IncrementalDecoder(codecs.IncrementalDecoder):
            def decode(self, input, final=False):
                if fdec is None:
                    raise NotImplementedError
                return ensure_str(fdec(input, self.errors)[0])
        
        class StreamWriter(Codec, codecs.StreamWriter):
            charbuffertype = bytes
        
        class StreamReader(Codec, codecs.StreamReader):
            charbuffertype = bytes
        
        ci = codecs.CodecInfo(
            name=name,
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamwriter=StreamWriter,
            streamreader=StreamReader,
            _is_text_encoding=text,
        )
        ci.parameters = kwargs
        ci.parameters['name'] = ename
        ci.parameters['add_to_codecs'] = add_to_codecs
        ci.parameters['pattern'] = pattern
        ci.parameters['text'] = text
        ci.parameters['category'] = category
        ci.parameters['examples'] = kwargs.get('examples', glob.get('__examples__'))
        ci.parameters['guess'] = kwargs.get('guess', glob.get('__guess__', [ename])) or []
        ci.parameters['module'] = kwargs.get('module', glob.get('__name__'))
        ci.parameters.setdefault("scoring", {})
        for attr in ["bonus_func", "entropy", "expansion_factor", "len_charset", "len_multiple", "penalty",
                     "printables_rate", "padding_char", "transitive"]:
            a = kwargs.pop(attr, None)
            if a is not None:
                ci.parameters['scoring'][attr] = a
        return ci
    
    getregentry.__name__ = re.sub(r"[\s\-]", "_", ename)
    if kwargs.get('aliases'):
        getregentry.__aliases__ = list(map(lambda n: re.sub(r"[\s\-]", "_", n), kwargs['aliases']))
    getregentry.__pattern__ = pattern
    getregentry.__category__ = category
    register(getregentry, add_to_codecs)
    return getregentry


def add_macro(mname, *encodings):
    """ This allows to define a macro, chaining multiple codecs one after the other. This relies on a default set of
         macros from a YAML file embedded in the package and a local YAML file from the home folder that takes
         precedence for defining personal macros.
    
    :param mname:     macro name
    :param encodings: encoding names of the encodings to be chained with the macro
    """
    global PERS_MACROS  # noqa: F824
    # check for name clash with alreday existing macros and codecs
    if mname in MACROS or mname in PERS_MACROS:
        raise ValueError("Macro name already exists")
    try:
        ci = lookup(mname, False)
        raise ValueError(f"Macro name clashes with codec '{ci.name}'")
    except LookupError:
        pass
    try:
        PERS_MACROS[mname] = encodings
        CodecMacro(mname)
        with open(PERS_MACROS_FILE, 'w') as f:
            json.dump(PERS_MACROS, f, indent=2)
    except ValueError:
        del PERS_MACROS[mname]
        raise
codecs.add_macro = add_macro


def add_map(ename, encmap, repl_char="?", sep="", ignore_case=None, no_error=False, intype=None, outype=None, **kwargs):
    """ This adds a new mapping codec (that is, declarable with a simple character mapping dictionary) to the codecs
         module dynamically setting its encode and/or decode functions, eventually dynamically naming the encoding with
         a pattern and with file handling (if text is True).
    
    :param ename:         encoding name
    :param encmap:        characters encoding map ; can be a dictionary of encoding maps (for use with the first capture
                           group of the regex pattern) or a function building the encoding map
    :param repl_char:     replacement char (used when errors handling is set to "replace")
    :param sep:           string of possible character separators (hence, only single-char separators are considered) ;
                           - while encoding, the first separator is used
                           - while decoding, separators can be mixed in the input text
    :param ignore_case:   ignore text case while encoding and/or decoding
    :param no_error:      this encoding triggers no error (hence, always in "leave" errors handling)
    :param intype:        specify the input type for pre-transforming the input text
    :param outype:        specify the output type for post-transforming the output text
    :param pattern:       pattern for dynamically naming the encoding
    :param text:          specify whether the codec is a text encoding
    :param add_to_codecs: also add the search function to the native registry
                           NB: this will make the codec available in the built-in open(...) but will make it impossible
                                to remove the codec later
    """
    outype = outype or intype
    if ignore_case not in [None, "encode", "decode", "both"]:
        raise ValueError("Bad ignore_case parameter while creating encoding map")
    if intype not in [None, "str", "bin", "ord"]:
        raise ValueError("Bad input type parameter while creating encoding map")
    if outype not in [None, "str", "bin", "ord"]:
        raise ValueError("Bad output type parameter while creating encoding map")
    
    def __generic_code(decode=False):
        def _wrapper(param):
            """ The parameter for wrapping comes from the encoding regex pattern ; e.g.
                 [no pattern]           => param will be None everytime
                 r"barbie[-_]?([1-4])$" => param could be int 1, 2, 3 or 4
                 r"^morse(|[-_]?.{3})$" => param could be None, "-ABC" (for mapping to ".-/")
            
            In order of precedence:
            1. when param is a key in mapdict or mapdict is a list of encoding maps (hence in the case of "barbie...",
                param MUST be an int, otherwise for the first case it could clash with a character of the encoding map)
            2. otherwise handle it as a new encoding character map "ABC" translates to ".-/" for morse
            """
            p = param
            if isinstance(encmap, FunctionType):
                mapdict = encmap(p)
                p = None
            else:
                mapdict = encmap
            if isinstance(mapdict, dict):
                smapdict = {k: v for k, v in mapdict.items()}
            elif isinstance(mapdict, list) and isinstance(mapdict[0], dict):
                smapdict = {k: v for k, v in mapdict[0].items()}
            else:
                raise ValueError("Bad mapping dictionary or list of mapping dictionaries")
            if p is not None:
                # case 1: param is empty string
                if p == "":
                    if isinstance(mapdict, list):
                        smapdict = {k: v for k, v in mapdict[0].items()}
                    elif isinstance(mapdict, dict):
                        if '' in mapdict.keys() and isinstance(mapdict[''], dict):
                            smapdict = {k: v for k, v in mapdict[''].items()}
                        else:
                            smapdict = {k: v for k, v in mapdict.items()}
                    # no 'else' handling a LookupError here ; this case is covered by the first if/elif/else block
                # case 2: list or dictionary or dictionary of numbered encodings
                elif isinstance(p, int):
                    # if mapdict is a list, we shall align the parameter (starting from 1) as an index (starting from 0)
                    if isinstance(mapdict, list):
                        p -= 1
                    if isinstance(mapdict, list) and 0 <= p < len(mapdict) or \
                       isinstance(mapdict, dict) and p in mapdict.keys():
                        smapdict = {k: v for k, v in mapdict[p].items()}
                    else:
                        raise LookupError(f"Bad parameter for encoding '{ename}': '{p}'")
                # case 3: dictionary of regex-selected encoding mappings
                elif isinstance(mapdict, dict) and isinstance(list(mapdict.values())[0], dict):
                    tmp = None
                    for r, d in mapdict.items():
                        if r == '':   # this is already handled in case 1 ; anyway, an empty regex always matches, hence
                            continue  #  it must be excluded
                        if re.match(r, p):
                            tmp = d
                            break
                    if tmp is None:
                        raise LookupError(f"Bad parameter for encoding '{ename}': '{p}'")
                    smapdict = tmp
                # case 4: encoding characters translation
                else:
                    # collect base tokens in order of appearance in the mapping dictionary
                    base_tokens = ""
                    for _, c in sorted(mapdict.items()):
                        for t in c:
                            for st in t:
                                if st not in base_tokens:
                                    base_tokens += st
                    if " " not in sep:
                        base_tokens = base_tokens.replace(" ", "")
                    if len(p) > 0 and p[0] in "-_" and len(p[1:]) == len(set(p[1:])) == len(base_tokens):
                        p = p[1:]
                    if len(p) == len(set(p)) == len(base_tokens):
                        t = maketrans(base_tokens, p)
                        for k, v in smapdict.items():
                            smapdict[k] = [x.translate(t) for x in v] if isinstance(v, list) else v.translate(t)
                    else:
                        raise LookupError(f"Bad parameter for encoding '{ename}': '{p}'")
            if ignore_case is not None:
                cases = ["upper", "lower"]
                case_d = cases[any(c in str(list(smapdict.values())) for c in "abcdefghijklmnopqrstuvwxyz")]
                case_e = cases[any(c in str(list(smapdict.keys())) for c in "abcdefghijklmnopqrstuvwxyz")]
                i = ignore_case
                smapdict = {getattr(k, case_e)() if i in ["both", "encode"] else k: \
                            ([getattr(x, case_d)() for x in v] if isinstance(v, list) else getattr(v, case_d)()) \
                                if i in ["both", "decode"] else v for k, v in smapdict.items()}
            strip = (False, False)
            if decode:
                tmp = {}
                # this has a meaning for encoding maps that could have clashes in encoded chars (e.g. Bacon's cipher ;
                #  I => abaaa but also J => abaaa, with the following, we keep I instead of letting J overwrite it)
                for k, v in sorted(smapdict.items()):
                    if not isinstance(v, list):
                        v = [v]
                    for x in v:
                        if x not in tmp.keys():
                            tmp[x] = k
                smapdict, cs = tmp, reduce(lambda acc, x: acc + x, tmp.keys())
                # line breaks that are not in the decoding map are stripped from the input (wrapped encoded text),
                #  except for codecs triggering no error, as they keep the unknown characters (thus, the lines)
                if not no_error:
                    strip = ("\n" not in set(cs), "\r\n" not in cs)
            # this allows to avoid an error with Python2 in the "for i, c in enumerate(parts)" loop
            if '' not in smapdict.keys():
                smapdict[''] = ""
            # determine token and result lengths
            tmaxlen = max(map(len, smapdict.keys()))
            tminlen = max(1, min(map(len, set(smapdict.keys()) - {''})))
            l = []
            for x in smapdict.values():
                getattr(l, ["append", "extend"][isinstance(x, list)])(x)
            rminlen = max(1, min(map(len, set(l) - {''})))
            # case handling, separator and kind of token do not depend on the text, hence they are determined once
            icase = ignore_case in ["both", "decode" if decode else "encode"]
            case = getattr(str, case_d if decode else case_e) if icase else None
            lsep = "" if decode else sep if len(sep) <= 1 else sep[0]
            kind = ["character", "token"][tmaxlen > 1]
            
            # generic encoding/decoding function for map encodings
            def code(text, errors="strict"):
                if no_error:
                    errors = "leave"
                text = ensure_str(text)
                if not decode:
                    if intype == "bin":
                        text = "".join(f"{bin(ord(c))[2:]:0>8}" for c in text)
                    elif intype == "ord":
                        text = "".join(str(ord(c)).zfill(3) for c in text)
                r = []
                error_func = handle_error(ename, errors, lsep, repl_char, rminlen, decode, kind)
                
                # get the value from the mapping dictionary, trying the token with its inverted case if relevant
                def __get_value(token, position, case_changed=False):
                    try:
                        result = smapdict[token]
                    except KeyError:
                        if icase and not case_changed:
                            return __get_value(case(token), position, True)
                        return error_func(token, position)
                    if isinstance(result, list):
                        result = result[0]
                    return result + lsep
                
                # if a separator is defined, rely on it by splitting the input text
                if decode and len(sep) > 0:
                    for i, c in enumerate(re.split("[" + sep + "]", text)):
                        r.append(__get_value(c, i))
                # otherwise, move through the text using a cursor for tokenizing it ; this allows defining more complex
                #  encodings with variable token lengths
                else:
                    cursor, bad = 0, ""
                    while cursor < len(text):
                        token = text[cursor:cursor+1]
                        for l in range(tminlen, tmaxlen + 1):
                            token = text[cursor:cursor+l]
                            if token in smapdict or icase and case(token) in smapdict:
                                r.append(__get_value(token, cursor))
                                cursor += l
                                break
                        else:
                            # collect bad chars and only move the cursor one char to the right
                            bad += text[cursor]
                            cursor += 1
                            # if the number of bad chars is the minimum token length, consume it and start a new buffer
                            if len(bad) == tminlen or errors == "leave":
                                posn = cursor - len(bad)
                                r.append(error_func(bad, posn))
                                bad = ""
                r = "".join(r)
                if decode:
                    if outype in ["bin", "ord"]:
                        tmp, r = [], r.replace(lsep, "")
                        step = [3, 8][outype == "bin"]
                        for i in range(0, len(r), step):
                            s = r[i:i+step]
                            try:
                                tmp.append(chr(int(s, 2) if outype == "bin" else int(s)))
                            except ValueError:
                                if len(s) > 0:
                                    tmp.append("[" + s + "]")
                        r = "".join(tmp) + lsep
                return r[:len(r)-len(lsep)], len(b(text))
            # the stripping flags are carried by the function, as it is built for each looked up encoding name
            code.__strip__ = strip
            return code
        if re.search(r"\([^(?:)]", kwargs.get('pattern', "")) is None:
            # in this case, there is no capturing group for parametrization
            return _wrapper(None)
        return _wrapper

    glob = currentframe().f_back.f_globals
    kwargs['category'] = glob['__file__'].split(os.path.sep)[-2].rstrip("s")
    kwargs['examples'] = kwargs.get('examples', glob.get('__examples__'))
    kwargs['encmap'] = encmap
    kwargs['repl_char'] = repl_char
    kwargs['sep'] = sep
    kwargs['ignore_case'] = ignore_case
    kwargs['no_error'] = no_error
    kwargs['intype'] = intype
    kwargs['outype'] = outype
    kwargs['module'] = glob.get('__name__')
    try:
        if isinstance(encmap, dict):
            smapdict = {k: v for k, v in encmap.items()}
        elif isinstance(encmap, list) and isinstance(encmap[0], dict):
            smapdict = {k: v for k, v in encmap[0].items()}
        kwargs['repl_minlen'] = i = max(1, min(map(len, set(smapdict.values()) - {''})))
        kwargs['repl_minlen_b'] = max(1, min(map(len, map(b, set(smapdict.values()) - {''}))))
    except:
        pass
    return add(ename, __generic_code(), __generic_code(True), **kwargs)
codecs.add_map = add_map


def clear():
    """ Clear codext's local registry of search functions. """
    global __codecs_registry, MACROS, PERS_MACROS  # noqa: F824
    __codecs_registry, MACROS, PERS_MACROS = [], {}, {}
    __registry_changed()
codecs.clear = clear


def examples(encoding, number=10):
    """ Use the search function to get the matching encodings and provide examples of valid encoding names. """
    e = []
    for name in search(encoding):
        for search_function in __codecs_registry:
            n = search_function.__name__
            if name in [n, n.replace("_", "-")]:
                temp = []
                for s in generate_strings_from_regex(search_function.__pattern__, yield_max=16*number):
                    temp.append(s)
                random.shuffle(temp)
                i = 0
                while i < min(number, len(temp)):
                    if not temp[i].isdigit():
                        try:
                            lookup(temp[i], False)
                            e.append(temp[i])
                        except LookupError:
                            pass
                    i += 1
        for alias, codec in ALIASES.items():
            if name == codec:
                if codec not in e:
                    e.append(codec)
                if not alias.isdigit():
                    e.append(alias)
    random.shuffle(e)
    return sorted([e[i] for i in range(min(number, len(e)))], key=_human_keys)
codecs.examples = examples


def is_native(encoding):
    """ Determine if a given encoding is native or not. """
    return lookup(encoding, False).parameters['category'] == "native"


def list_categories():
    """ Get a list of all codec categories. """
    root = os.path.dirname(__file__)
    # categories from the folders of the codecs, plus a particular category, hardcoded from base/_base.py
    for c in [d.rstrip("s") for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and
              not d.startswith("__")] + ["base-generic"]:
        if c not in CODECS_CATEGORIES:
            CODECS_CATEGORIES.append(c)
    return CODECS_CATEGORIES[:]
list_categories()


def _categories(names):
    """ Replace the deprecated categories (possibly negated with "~") by the current categories of their codecs. """
    r = []
    for name in names:
        neg = "~" if isinstance(name, str) and name.startswith("~") else ""
        new = DEPRECATED_CATEGORIES.get(name[len(neg):]) if isinstance(name, str) else None
        if new is None:
            r.append(name)
            continue
        warnings.warn(f"Category '{name[len(neg):]}' is deprecated, use {' and '.join(map(repr, new))} instead",
                      DeprecationWarning, stacklevel=3)
        r.extend(neg + c for c in new if neg + c not in r)
    return r


def list_encodings(*categories):
    """ Get a list of all codecs. """
    # if "non-native" is in the input list, extend the list with the whole categories but "native"
    categories, exclude = _categories(categories), []
    for c in categories[:]:
        if c == "non-native":
            for c in CODECS_CATEGORIES:
                if c == "native" or c in categories:
                    continue
                categories.append(c)
            categories.remove("non-native")
        if c.startswith("~"):
            exclude.append(c[1:])
            categories.remove(c)
            try:
                categories.remove(c[1:])
            except ValueError:
                pass
    # now, filter codecs according to the input list of categories
    enc = []
    if (len(categories) == 0 or "native" in categories) and "native" not in exclude:
        for a in set(ALIASES.values()):
            try:
                ci = __orig_lookup(a)
            except LookupError:
                continue
            if lookup(a) is ci:
                enc.append(ci.name)
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        name = search_function.__name__.replace("_", "-")
        c = getattr(search_function, "__category__", None)
        if c is None:
            p = getattr(search_function, "__pattern__", None)
            ci = search_function(name) if p is None else search_function(_sample_name(search_function))
            c = "other" if ci is None else ci.parameters['category']
        if (len(categories) == 0 or c in categories) and c not in exclude:
            enc.append(name)
    for category in categories:
        if category not in CODECS_CATEGORIES:
            raise ValueError(f"Category '{category}' does not exist")
    return sorted(list(set(enc)), key=_human_keys)


def list_macros():
    """ Get a list of all macros, with the precedence on personal ones. """
    return sorted(list(set(list(MACROS.keys()) + list(PERS_MACROS.keys()))))


def remove(name):
    """ Remove all search functions matching the input encoding name from codext's local registry or any macro with the
         given name. """
    global __codecs_registry, MACROS, PERS_MACROS  # noqa: F824
    tbr = []
    for search_function in __codecs_registry:
        if search_function(name) is not None:
            tbr.append(search_function)
    for search_function in tbr:
        __codecs_registry.remove(search_function)
    __registry_changed()
    try:
        del MACROS[name]
    except KeyError:
        pass
    try:
        del PERS_MACROS[name]
        with open(PERS_MACROS_FILE, 'w') as f:
            json.dump(PERS_MACROS, f, indent=2)
    except KeyError:
        pass
    try:
        del CODECS_CACHE[name]
    except KeyError:
        pass
    for s in ["En", "De"]:
        try:
            delattr(builtins, f"{name.capitalize()}{s}codeError")
        except AttributeError:
            pass
codecs.remove = remove


def reset():
    """ Reset codext's local registry of search functions and macros. """
    from importlib import reload
    global __codecs_registry, CODECS_REGISTRY, MACROS, PERS_MACROS  # noqa: F824
    clear()
    d = os.path.dirname(__file__)
    for pkg in sorted(os.listdir(d)):
        if pkg.startswith("_") or not os.path.isdir(os.path.join(d, pkg)):
            continue
        reload(import_module("codext." + pkg))
    # backup codext's registry
    if CODECS_REGISTRY is None:
        CODECS_REGISTRY = __codecs_registry[:]
    # restore codext's registry
    else:
        __codecs_registry = CODECS_REGISTRY[:]
    __registry_changed()
    # restore codext's embedded set of macros
    with open(os.path.join(os.path.dirname(__file__), "macros.json")) as f:
        MACROS = json.load(f)
    # reload personal set of macros
    PERS_MACROS = {}
    if os.path.exists(PERS_MACROS_FILE):
        with open(PERS_MACROS_FILE) as f:
            PERS_MACROS = json.load(f)
codecs.reset = reset


# codecs module hooks
__orig_lookup   = _codecs.lookup
__orig_register = _codecs.register


def __add(ename, encode=None, decode=None, pattern=None, text=True, **kwargs):
    kwargs.pop('add_to_codecs', None)
    return add(ename, encode, decode, pattern, text, True, **kwargs)
__add.__doc__ = add.__doc__
codecs.add = __add


def decode(obj, encoding='utf-8', errors='strict'):
    """ Custom decode function relying on the hooked lookup function. """
    return lookup(encoding).decode(obj, errors)[0]
codecs.decode = decode


_REPEAT = re.compile(r"\[(\d+)\]$")


def encode(obj, encoding='utf-8', errors='strict'):
    """ Custom encode function relying on the hooked lookup function. """
    n, m = 1, _REPEAT.search(encoding)
    if m:
        n = int(m.group(1))
        encoding = encoding[:m.start()]
    ci = lookup(encoding)
    for i in range(n):
        try:
            obj = ci.encode(obj, errors)[0]
        except (AttributeError, TypeError) as e:  # occurs for encodings that require str as input while 'obj' is bytes
            if str(e) not in ["'bytes' object has no attribute 'encode'",
                              "ord() expected string of length 1, but int found"] or \
               encoding in ["latin-1", "utf-8"]:  # encodings considered when using b(...)
                raise
            obj = ci.encode(ensure_str(obj), errors)[0]
    return obj
codecs.encode = encode


def lookup(encoding, macro=True):
    """ Hooked lookup function for searching first for codecs in the local registry of this module. """
    # the results are cached per encoding name, as searching through the registry is costly ; a macro is only returned
    #  when allowed, and failures are not cached (a codec or a macro may be added afterwards)
    try:
        ci = __lookup_cache[encoding]
        if macro or not isinstance(ci, CodecMacro):
            return ci
    except (KeyError, TypeError):
        pass
    ci = __lookup(encoding, macro)
    try:
        __lookup_cache[encoding] = ci
    except TypeError:
        pass
    return ci
codecs.lookup = lookup


def __lookup(encoding, macro=True):
    """ Search for the given encoding, first in the local registry of this module, then with the original lookup
         function and finally among the macros. """
    # first, try to match the given encoding with codecs' search functions
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        codecinfo = search_function(encoding)
        if codecinfo is not None:
            return codecinfo
    # then, if a codec name was given, generate an encoding name from its pattern and get the CodecInfo
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        if search_function.__name__.replace("_", "-") == encoding or \
           encoding in getattr(search_function, "__aliases__", []):
            codecinfo = search_function(_sample_name(search_function))
            if codecinfo is not None:
                return codecinfo
    # finally, get a CodecInfo with the original lookup function and refine it with a dictionary of parameters
    try:
        ci = __orig_lookup(encoding)
        ci.parameters = {'category': "native", 'module': "codecs", 'name': ALIASES.get(ci.name, ci.name)}
        return ci
    except LookupError:
        if not macro:
            raise
    try:
        return CodecMacro(encoding)
    except LookupError:
        e = LookupError(f"unknown encoding: {encoding}")
        e.__cause__ = e  # stop exception chaining
        raise e


def register(search_function, add_to_codecs=False):
    """ Register function for registering new codecs in the local registry of this module and, if required, in the
         native codecs registry (for use with the built-in 'open' function).
    
    :param search_function: search function for the codecs registry
    :param add_to_codecs:   also add the search function to the native registry
                            NB: this will make the codec available in the built-in open(...) but will make it impossible
                                 to remove the codec later
    """
    if search_function not in __codecs_registry:
        try:
            __orig_lookup(search_function.__name__)
            l = CODECS_OVERWRITTEN
        except LookupError:
            l = __codecs_registry
        l.append(search_function)
        __registry_changed()
    if add_to_codecs:
        __orig_register(search_function)


def __register(search_function):
    """ Same as register(...), but with add_to_codecs set by default to True. """
    register(search_function, True)
codecs.register = __register


def __names():
    """ Get the table of names used for searching encodings, as tuples (names to be matched, resulting name, search
         function), built once per state of the registry. """
    if len(__names_table) == 0:
        for search_function in CODECS_OVERWRITTEN + __codecs_registry:
            n = search_function.__name__
            __names_table.append(((n, n.replace("_", "-")), n.replace("_", "-"), search_function))
        for alias, name in ALIASES.items():
            __names_table.append(((alias, name), name, None))
    return __names_table


def __registry_changed():
    """ Clear the caches depending on the state of the registry. """
    __guess_lists.clear()
    __lookup_cache.clear()
    __names_table.clear()


def _sample_name(search_function):
    """ Get the encoding name generated from the pattern of the given search function (used when looking up a codec by
         its name) ; it is cached on the search function, as generating strings from a regex is costly. """
    try:
        return search_function.__sample__
    except AttributeError:
        search_function.__sample__ = s = generate_string_from_regex(getattr(search_function, "__pattern__", None))
        return s


def _sample_rounds(search_function):
    """ Get 5 sets of encoding names generated from the pattern of the given search function, for the extended search ;
         they are cached on the search function, as generating strings from a regex is costly. """
    try:
        return search_function.__samples__
    except AttributeError:
        p = getattr(search_function, "__pattern__", None)
        search_function.__samples__ = r = [list(generate_strings_from_regex(p)) for _ in range(5)]
        return r


def search(encoding_regex, extended=True):
    """ Function similar to lookup but allows to search for an encoding based on a regex instead. It searches this way
         into the local registry but also tries a simple lookup with the original lookup function. """
    matches, rx = [], re.compile(encoding_regex)
    for names, name, search_function in __names():
        if any(rx.search(n) for n in names):
            matches.append(name)
        if extended and search_function is not None:
            # in some cases, encoding_regex can match a generated string that uses a particular portion of its
            #  generating pattern ; e.g. we expect encoding_regex="uu_" to find "uu" and "uu_codec" while it can also
            #  find "morse" or "atbash" very rarely because of their dynamic patterns and the limited number of randomly
            #  generated strings
            # so, we can use a qualified majority voting to ensure we do not get a "junk" encoding in the list of
            #  matches ; using 5 sets of generated strings for a given codec but adding the codec to the list of
            #  matches only if we get at least 3 matches ensures that we consider up to 2 failures that could be
            #  stochastic, therefore drastically decreasing the probability to get a "junk" encoding in the matches list
            c = 0
            for strings in _sample_rounds(search_function):
                if any(rx.search(s) for s in strings):
                    c += 1
                    if c >= 3:
                        matches.append(search_function.__name__)
                        break
    return sorted(list(set(matches)), key=_human_keys)
codecs.search = search
