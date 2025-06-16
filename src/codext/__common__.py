# -*- coding: UTF-8 -*-
import _codecs
import codecs
import hashlib
import json
import os
import random
import re
import sre_parse
import sys
from encodings.aliases import aliases as ALIASES
from functools import reduce, update_wrapper, wraps
from importlib import import_module
from inspect import currentframe
from io import BytesIO
from itertools import chain, product
from locale import getlocale
from math import log
from pkgutil import iter_modules
from platform import system
from random import randint
from string import *
from types import FunctionType, ModuleType
try:  # Python2
    import __builtin__ as builtins
except ImportError:
    import builtins
try:  # Python2
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
try:  # Python2
    from string import maketrans
except ImportError:
    maketrans = str.maketrans
try:  # Python3
    from importlib import reload
except ImportError:
    pass

# from Python 3.11, it seems that 'sre_parse' is not bound to 're' anymore
re.sre_parse = sre_parse


__all__ = ["add", "add_macro", "add_map", "b", "clear", "codecs", "decode", "encode", "ensure_str", "examples", "guess",
           "isb", "generate_strings_from_regex", "get_alphabet_from_mask", "handle_error", "hashlib", "i2s",
           "is_native", "list_categories", "list_encodings", "list_macros", "lookup", "maketrans", "os", "rank", "re",
           "register", "remove", "reset", "s2i", "search", "stopfunc", "BytesIO", "_input", "_stripl", "CodecMacro",
           "DARWIN", "LANG", "LINUX", "MASKS", "UNIX", "WINDOWS"]
CODECS_REGISTRY = None
CODECS_OVERWRITTEN = []
CODECS_CATEGORIES = ["native", "custom"]
CODECS_CACHE = {}
LANG = getlocale()
if LANG:
    LANG = (LANG[0] or "")[:2].lower()
MASKS = {
    'a': printable,
    'b': "".join(chr(i) for i in range(256)),
    'd': digits,
    'h': digits + "abcdef",
    'H': digits + "ABCDEF",
    'l': ascii_lowercase,
    'p': punctuation,
    's': " ",
    'u': ascii_uppercase,
}

__codecs_registry = []

MACROS = {}
PERS_MACROS = {}
PERS_MACROS_FILE = os.path.expanduser("~/.codext-macros.json")

DARWIN = system() == "Darwin"
LINUX = system() == "Linux"
UNIX = DARWIN or LINUX
WINDOWS = system() == "Windows"

entropy = lambda s: -sum([p * log(p, 2) for p in [float(s.count(c)) / len(s) for c in set(s)]])

isb = lambda s: isinstance(s, bytes)
iss = lambda s: isinstance(s, str)
fix = lambda x, ref: b(x) if isb(ref) else ensure_str(x) if iss(ref) else x

s2i = lambda s: int(codecs.encode(s, "base16"), 16)
exc_name = lambda e: "".join(t.capitalize() for t in re.split(r"[-_+]", e))


def i2s(input):
    h = hex(input)[2:].rstrip("eL")
    return codecs.decode(h.zfill(len(h) + len(h) % 2), "hex")


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


def __stdin_pipe():
    """ Stdin pipe read function. """
    try:
        with open(0, 'rb') as f:
            for l in f:
                yield l
    except TypeError:
        for l in sys.stdin:
            yield l


def _input(infile):
    # handle input file or stdin
    c = b("")
    if infile:
        with open(infile, 'rb') as f:
            c = f.read()
    else:
        for line in __stdin_pipe():
            c += line
    return c


def _set_exc(name, etype="ValueError"):
    if not hasattr(builtins, name):
        ns = {}
        exec(f"class {name}({etype}): __module__ = 'builtins'", {}, ns)
        setattr(builtins, name, ns[name])
_set_exc("InputSizeLimitError")
_set_exc("ParameterError")


def _stripl(s, st_lines, st_crlf):
    if st_crlf:
        s = s.replace(b"\r\n", b"") if isb(s) else s.replace("\r\n", "")
    if st_lines:
        s = s.replace(b"\n", b"") if isb(s) else s.replace("\n", "")
    return s


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
    # search function for the new encoding
    @_with_repr(ename)
    def getregentry(encoding):
        if encoding != ename and not (pattern and re.match(pattern, encoding)):
            return
        fenc, fdec, name = encode, decode, encoding
        # prepare CodecInfo input arguments
        if pattern:
            m, args, i = re.match(pattern, encoding), [], 1
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
            fdec = fix_inout_formats(fdec)
            sl, sc = kwargs.pop('strip_lines', False), kwargs.pop('strip_crlf', False)
            if sl or sc:
                def _striplines(f):
                    def __wrapper(input, *a, **kw):
                        return f(_stripl(input, sc, sl), *a, **kw)
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
        f = glob.get('__file__', os.path.join("custom", "_"))
        cat = f.split(os.path.sep)[-2].rstrip("s")
        if cat not in CODECS_CATEGORIES:
            CODECS_CATEGORIES.append(cat)
        ci.parameters['category'] = kwargs.get('category', cat)
        ci.parameters['examples'] = kwargs.get('examples', glob.get('__examples__'))
        ci.parameters['guess'] = kwargs.get('guess', glob.get('__guess__', [ename])) or []
        ci.parameters['module'] = kwargs.get('module', glob.get('__name__'))
        ci.parameters.setdefault("scoring", {})
        for attr in ["bonus_func", "entropy", "expansion_factor", "len_charset", "penalty", "printables_rate",
                     "padding_char", "transitive"]:
            a = kwargs.pop(attr, None)
            if a is not None:
                ci.parameters['scoring'][attr] = a
        return ci
    
    getregentry.__name__ = re.sub(r"[\s\-]", "_", ename)
    if kwargs.get('aliases'):
        getregentry.__aliases__ = list(map(lambda n: re.sub(r"[\s\-]", "_", n), kwargs['aliases']))
    getregentry.__pattern__ = pattern
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
                kwargs['strip_lines'], kwargs['strip_crlf'] = "\n" not in set(cs), "\r\n" not in cs
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
            
            # generic encoding/decoding function for map encodings
            def code(text, errors="strict"):
                icase = ignore_case == "both" or \
                        decode and ignore_case == "decode" or \
                        not decode and ignore_case == "encode"
                if icase:
                    case = case_d if decode else case_e
                if no_error:
                    errors = "leave"
                text = ensure_str(text)
                if not decode:
                    if intype == "bin":
                        text = "".join(f"{bin(ord(c))[2:]:0>8}" for c in text)
                    elif intype == "ord":
                        text = "".join(str(ord(c)).zfill(3) for c in text)
                r = ""
                lsep = "" if decode else sep if len(sep) <= 1 else sep[0]
                kind = ["character", "token"][tmaxlen > 1]
                error_func = handle_error(ename, errors, lsep, repl_char, rminlen, decode, kind)
                
                # get the value from the mapping dictionary, trying the token with its inverted case if relevant
                def __get_value(token, position, case_changed=False):
                    try:
                        result = smapdict[token]
                    except KeyError:
                        if icase and not case_changed:
                            token_inv_case = getattr(token, case)()
                            return __get_value(token_inv_case, position, True)
                        return error_func(token, position)
                    if isinstance(result, list):
                        result = result[0]
                    return result + lsep
                
                # if a separator is defined, rely on it by splitting the input text
                if decode and len(sep) > 0:
                    for i, c in enumerate(re.split("[" + sep + "]", text)):
                        r += __get_value(c, i)
                # otherwise, move through the text using a cursor for tokenizing it ; this allows defining more complex
                #  encodings with variable token lengths
                else:
                    cursor, bad = 0, ""
                    while cursor < len(text):
                        token = text[cursor:cursor+1]
                        for l in range(tminlen, tmaxlen + 1):
                            token = text[cursor:cursor+l]
                            if token in smapdict.keys() or icase and getattr(token, case)() in smapdict.keys():
                                r += __get_value(token, cursor)
                                cursor += l
                                break
                        else:
                            # collect bad chars and only move the cursor one char to the right
                            bad += text[cursor]
                            cursor += 1
                            # if the number of bad chars is the minimum token length, consume it and start a new buffer
                            if len(bad) == tminlen or errors == "leave":
                                posn = cursor - len(bad)
                                r += error_func(bad, posn)
                                bad = ""
                if decode:
                    if outype in ["bin", "ord"]:
                        tmp, r = "", r.replace(lsep, "")
                        step = [3, 8][outype == "bin"]
                        for i in range(0, len(r), step):
                            s = r[i:i+step]
                            try:
                                tmp += chr(int(s, 2) if outype == "bin" else int(s))
                            except ValueError:
                                if len(s) > 0:
                                    tmp += "[" + s + "]"
                        r = tmp + lsep
                return r[:len(r)-len(lsep)], len(b(text))
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
    c = CODECS_CATEGORIES
    root = os.path.dirname(__file__)
    for d in os.listdir(root):
        if os.path.isdir(os.path.join(root, d)) and not d.startswith("__"):
            c.append(d.rstrip("s"))
    # particular category, hardcoded from base/_base.py
    c += ["base-generic"]
    return c
list_categories()


def list_encodings(*categories):
    """ Get a list of all codecs. """
    # if "non-native" is in the input list, extend the list with the whole categories but "native"
    categories, exclude = list(categories), []
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
        p = search_function.__pattern__
        ci = search_function(name) if p is None else search_function(generate_string_from_regex(p))
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
    # restore codext's embedded set of macros
    with open(os.path.join(os.path.dirname(__file__), "macros.json")) as f:
        MACROS = json.load(f)
    # reload personal set of macros
    PERS_MACROS = {}
    if os.path.exists(PERS_MACROS_FILE):
        with open(PERS_MACROS_FILE) as f:
            PERS_MACROS = json.load(f)
codecs.reset = reset


# conversion functions
def b(s):
    """ Non-crashing bytes conversion function. """
    try:
        return s.encode("latin-1")
    except:
        pass
    try:
        return s.encode("utf-8")
    except:
        pass
    return s


def ensure_str(s, encoding="utf-8", errors='strict'):
    """ Dummy str conversion function. """
    if isinstance(s, bytes):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    return s


# make conversion functions compatible with input/output strings/bytes
def fix_inout_formats(f):
    """ This decorator ensures that the first output of f will have the same text format as the first input (str or
         bytes). """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        a0 = args[0]
        a0_isb = isb(a0)
        a0 = ensure_str(a0) if iss(a0) or a0_isb else a0
        r = f(a0, *args[1:], **kwargs)
        # special case: input is in bytes ; ensure that the returned length is this of the bytes, not this processed by
        #                the decode/encode function
        if isinstance(r, (tuple, list)) and isinstance(r[1], int) and a0_isb:
            r = tuple([list(r)[0]] + [len(args[0])] + list(r)[2:])
        return (fix(r[0], args[0]), ) + r[1:] if isinstance(r, (tuple, list)) else fix(r, args[0])
    return _wrapper


# alphabet generation function from a given mask
def get_alphabet_from_mask(mask):
    """ This function generates an alphabet from the given mask. The style used is similar to Hashcat ; group keys are
         marked with a heading "?". """
    i, alphabet = 0, ""
    while i < len(mask):
        c = mask[i]
        if c == "?" and i < len(mask) - 1 and mask[i+1] in MASKS.keys():
            for c in MASKS[mask[i+1]]:
                if c not in alphabet:
                    alphabet += c
            i += 1
        elif c not in alphabet:
            alphabet += c
        i += 1
    return alphabet


# generic error handling function
def handle_error(ename, errors, sep="", repl_char="?", repl_minlen=1, decode=False, kind="character", item="position"):
    """ This shortcut function allows to handle error modes given some tuning parameters.
    
    :param ename:       encoding name
    :param errors:      error handling mode
    :param sep:         token separator
    :param repl_char:   replacement character (for use when errors="replace")
    :param repl_minlen: repeat number for the replacement character
    :param decode:      whether we are encoding or decoding
    :param item:        position item description (for describing the error ; e.g. "group" or "token")
    """
    exc = f"{exc_name(ename)}{['En','De'][decode]}codeError"
     
    def _handle_error(token, position, output="", eename=None):
        """ This handles an encoding/decoding error according to the selected handling mode.
        
        :param token:    input token to be encoded/decoded
        :param position: token position index
        :param output:   output, as decoded up to the position of the error
        """
        if errors == "strict":
            msg = "'%s' codec can't %scode %s '%s' in %s %d"
            token = ensure_str(token)
            token = token[:7] + "..." if len(token) > 10 else token
            err = getattr(builtins, exc)(msg % (eename or ename, ["en", "de"][decode], kind, token, item, position))
            err.output = output
            err.__cause__ = err
            raise err
        elif errors == "leave":
            return token + sep
        elif errors == "replace":
            return repl_char * repl_minlen + sep
        elif errors == "ignore":
            return ""
        else:
            raise ValueError(f"Unsupported error handling '{errors}'")
    return _handle_error


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


def encode(obj, encoding='utf-8', errors='strict'):
    """ Custom encode function relying on the hooked lookup function. """
    n, m = 1, re.search(r"\[(\d+)\]$", encoding)
    if m:
        n = int(m.group(1))
        encoding = re.sub(r"\[(\d+)\]$", "", encoding)
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
    # first, try to match the given encoding with codecs' search functions
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        codecinfo = search_function(encoding)
        if codecinfo is not None:
            return codecinfo
    # then, if a codec name was given, generate an encoding name from its pattern and get the CodecInfo
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        if search_function.__name__.replace("_", "-") == encoding or \
           encoding in getattr(search_function, "__aliases__", []):
            codecinfo = search_function(generate_string_from_regex(search_function.__pattern__))
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
codecs.lookup = lookup


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
    if add_to_codecs:
        __orig_register(search_function)


def __register(search_function):
    """ Same as register(...), but with add_to_codecs set by default to True. """
    register(search_function, True)
codecs.register = __register


def search(encoding_regex, extended=True):
    """ Function similar to lookup but allows to search for an encoding based on a regex instead. It searches this way
         into the local registry but also tries a simple lookup with the original lookup function. """
    matches = []
    for search_function in CODECS_OVERWRITTEN + __codecs_registry:
        n = search_function.__name__
        for name in [n, n.replace("_", "-")]:
            if re.search(encoding_regex, name):
                matches.append(n.replace("_", "-"))
                continue
        if extended:
            # in some cases, encoding_regex can match a generated string that uses a particular portion of its
            #  generating pattern ; e.g. we expect encoding_regex="uu_" to find "uu" and "uu_codec" while it can also
            #  find "morse" or "atbash" very rarely because of their dynamic patterns and the limited number of randomly
            #  generated strings
            # so, we can use a qualified majority voting to ensure we do not get a "junk" encoding in the list of
            #  matches ; executing 5 times the string generation for a given codec but adding the codec to the list of
            #  matches only if we get at least 3 matches ensures that we consider up to 2 failures that could be
            #  stochastic, therefore drastically decreasing the probability to get a "junk" encoding in the matches list
            c = 0
            for i in range(5):
                for s in generate_strings_from_regex(search_function.__pattern__):
                    if re.search(encoding_regex, s):
                        c += 1
                        break
                if c >= 3:
                    matches.append(n)
                    break
    for s, n in ALIASES.items():
        if re.search(encoding_regex, s) or re.search(encoding_regex, n):
            matches.append(n)
    return sorted(list(set(matches)), key=_human_keys)
codecs.search = search


# utility function for the search feature
CATEGORIES = {
    'digit':     digits,
    'not_digit': reduce(lambda x, c: x.replace(c, ""), digits, printable),
    'space':     whitespace,
    'not_space': reduce(lambda x, c: x.replace(c, ""), whitespace, printable),
    'word':      ascii_letters + digits + '_',
    'not_word':  reduce(lambda x, c: x.replace(c, ""), ascii_letters + digits + '_', printable),
}
REPEAT_MAX    = 10
STAR_PLUS_MAX = 10
YIELD_MAX     = 100


def __gen_str_from_re(regex, star_plus_max, repeat_max, yield_max, parsed=False):
    """ Recursive function to generate strings from a regex pattern. """
    if regex is None:
        return
    __groups = {}
    tokens = []
    negate, last_rand = False, None
    for state in (regex if parsed else re.sre_parse.parse(b(getattr(regex, "pattern", regex)))):
        code = getattr(state[0], "name", state[0]).lower()
        value = getattr(state[1], "name", state[1])
        value = value.lower() if isinstance(value, str) else value
        if code in ["assert_not", "at"]:
            continue
        elif code == "any":
            charset = list(printable.replace("\n", ""))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)  # should be ord(x) with x belongs to [0, 256[
        elif code == "assert":
            tokens.append(list(__gen_str_from_re(value[1], star_plus_max, repeat_max, yield_max, True)))
        elif code == "branch":
            result = []
            for r in value[1]:
                result += list(__gen_str_from_re(r, star_plus_max, repeat_max, yield_max, True)) or [""]
            tokens.append(result)
        elif code == "category":
            charset = list(CATEGORIES[value[9:]])
            if negate:
                negate = False
                charset = list(set(printable).difference(charset))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)
        elif code == "groupref":
            tokens.extend(__groups[value])
        elif code == "in":
            subtokens = list(__gen_str_from_re(value, star_plus_max, repeat_max, yield_max, True))
            subtokens = [x for l in subtokens for x in l]
            tokens.append(subtokens)
        elif code == "literal":
            tokens.append(chr(value))
        elif code in ["max_repeat", "min_repeat"]:
            start, end = value[:2]
            end = min(end, star_plus_max)
            start = min(start, end)
            charset = list(__gen_str_from_re(value[-1], star_plus_max, repeat_max, yield_max, True))
            subtokens = []
            if start == 0 and end == 1:
                subtokens.append("")
                subtokens.extend(charset)
            elif len(charset) ** end > repeat_max:
                for i in range(min(repeat_max, 10 * len(charset))):
                    n = random.randint(start, end + 1)
                    token = "" if n == 0 else "".join(random.choice(charset) for i in range(n))
                    if token not in subtokens:
                        subtokens.append(token)
                    else:
                        i -= 1
            else:
                for n in range(start, end + 1):
                    for c in product(charset, repeat=n):
                        subtokens.append("".join(c))
            tokens.append(subtokens)
        elif code == "negate":
            negate = True
        elif code == "not_literal":
            charset = list(printable.replace(chr(value), ""))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)
        elif code == "range":
            tokens.append("".join(chr(i) for i in range(value[0], value[1] + 1)))
        elif code == "subpattern":
            result = list(__gen_str_from_re(value[-1], star_plus_max, repeat_max, yield_max, True))
            if value[0]:
                __groups[value[0]] = result
            tokens.append(result)
        else:
            raise NotImplementedError(f"Unhandled code '{code}'")
    if len(tokens) == 0:
        tokens = [""]
    i = 0
    for result in product(*tokens):
        yield "".join(result)
        i += 1
        if i >= yield_max:
            break


def _human_keys(text):
    """ Sorting function for considering strings with numbers (e.g. base2, base10, base100) """
    tokens = []
    for s in re.split(r"(\d+|\D+)", text):
        tokens.append(int(s) if s.isdigit() else s)
    return tokens


def generate_string_from_regex(regex):
    """ Utility function to generate a single string from a regex pattern. """
    if regex:
        return list(generate_strings_from_regex(regex, yield_max=1))[0]


def generate_strings_from_regex(regex, star_plus_max=STAR_PLUS_MAX, repeat_max=REPEAT_MAX, yield_max=YIELD_MAX):
    """ Utility function to generate strings from a regex pattern. """
    i = 0
    for result in __gen_str_from_re(regex, star_plus_max, repeat_max, yield_max):
        yield result


# guess feature objects
__module_exists = lambda n: n in [x[1] for x in iter_modules()]
stopfunc = ModuleType("stopfunc", """
    Predefined stop functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This submodule contains stop functions for the guess feature of codext.
    
    - `flag`:       searches for the pattern "[Ff][Ll1][Aa4@][Gg9]" (either UTF-8 or UTF-16)
    - `lang_**`:    checks if the given lang (any from the PROFILES_DIRECTORY of the langdetect module) is detected
    - `printables`: checks that every output character is in the set of printables
    - `regex`:      takes one argument, the regular expression, for checking a string against the given pattern
    - `text`:       checks for printables and an entropy less than 4.6 (empirically determined)
""")
stopfunc.printables = lambda s: all(c in printable for c in ensure_str(s))
stopfunc.printables.__name__ = stopfunc.printables.__qualname__ = "printables"
stopfunc.regex = lambda p: lambda s: re.search(p, ensure_str(s)) is not None
stopfunc.regex.__name__ = stopfunc.regex.__qualname__ = "regex"
stopfunc.text = lambda s: stopfunc.printables(s) and entropy(s) < 4.6
stopfunc.text.__name__ = stopfunc.text.__qualname__ = "text"
stopfunc.flag = lambda x: re.search(r"[Ff][Ll1][Aa4@][Gg96]", ensure_str(x)) is not None
stopfunc.flag.__name__ = stopfunc.flag.__qualname__ = "flag"
stopfunc.default = stopfunc.text

stopfunc.LANG_BACKEND = None
stopfunc.LANG_BACKENDS = [n for n in ["pycld2", "langdetect", "langid", "cld3", "textblob"] if __module_exists(n)]
if len(stopfunc.LANG_BACKENDS) > 0:
    stopfunc.LANG_BACKEND = stopfunc.LANG_BACKENDS[0]
if "cld3" in stopfunc.LANG_BACKENDS:
    stopfunc.CLD3_LANGUAGES = "af|am|ar|bg|bn|bs|ca|ce|co|cs|cy|da|de|el|en|eo|es|et|eu|fa|fi|fr|fy|ga|gd|gl|gu|ha|" \
                              "hi|hm|hr|ht|hu|hy|id|ig|is|it|iw|ja|jv|ka|kk|km|kn|ko|ku|ky|la|lb|lo|lt|lv|mg|mi|mk|" \
                              "ml|mn|mr|ms|mt|my|ne|nl|no|ny|pa|pl|ps|pt|ro|ru|sd|si|sk|sl|sm|sn|so|sq|sr|st|su|sv|" \
                              "sw|ta|te|tg|th|tr|uk|ur|uz|vi|xh|yi|yo|zh|zu".split("|")
if "textblob" in stopfunc.LANG_BACKENDS:
    stopfunc.TEXTBLOB_LANGUAGES = "af|ar|az|be|bg|bn|ca|cs|cy|da|de|el|en|eo|es|et|eu|fa|fi|fr|ga|gl|gu|hi|hr|ht|hu|" \
                                  "id|is|it|iw|ja|ka|kn|ko|la|lt|lv|mk|ms|mt|nl|no|pl|pt|ro|ru|sk|sl|sq|sr|sv|sw|ta|" \
                                  "te|th|tl|tr|uk|ur|vi|yi|zh".split("|")


def _detect(text):
    _lb, t = stopfunc.LANG_BACKEND, ensure_str(text)
    if _lb is None:
        raise ValueError("No language backend %s" % ["selected", "installed"][len(stopfunc.LANG_BACKENDS) == 0])
    return langid.classify(t)[0] if _lb == "langid" else \
           langdetect.detect(t) if _lb == "langdetect" else \
           pycld2.detect(t)[2][0][1] if _lb == "pycld2" else \
           cld3.get_language(t).language[:2] if _lb == "cld3" else \
           textblob.TextBlob(t).detect_language()[:2]


def _lang(lang):
    def _test(s):
        if not stopfunc.text(s):
            return False
        try:
            return _detect(ensure_str(s))[:2] == lang
        except:
            return False
    return _test


def _load_lang_backend(backend=None):
    # import the requested backend library if not imported yet
    if backend is None or backend in stopfunc.LANG_BACKENDS:
        stopfunc.LANG_BACKEND = backend
        if backend:
            globals()[backend] = __import__(backend)
    else:
        raise ValueError("Unsupported language detection backend")
    # remove language-related stop functions
    for attr in dir(stopfunc):
        if attr.startswith("_") or not isinstance(getattr(stopfunc, attr), FunctionType):
            continue
        if re.match(r"lang_[a-z]{2}$", attr):
            delattr(stopfunc, attr)
    # rebind applicable language-related stop functions
    if stopfunc.LANG_BACKEND:
        _lb = stopfunc.LANG_BACKEND
        if _lb == "langid":
            langid.langid.load_model()
        for lang in (
            langid.langid.identifier.nb_classes if _lb == "langid" else \
            list(set(p[:2] for p in os.listdir(langdetect.PROFILES_DIRECTORY))) if _lb == "langdetect" else \
            list(set(x[1][:2] for x in pycld2.LANGUAGES if x[0] in pycld2.DETECTED_LANGUAGES)) if _lb == "pycld2" else \
            stopfunc.CLD3_LANGUAGES if _lb == "cld3" else \
            stopfunc.TEXTBLOB_LANGUAGES if _lb == "textblob" else \
            []):
            n = f"lang_{lang}"
            setattr(stopfunc, n, _lang(lang))
            getattr(stopfunc, n).__name__ = getattr(stopfunc, n).__qualname__ = n
        if LANG:
            flng = f"lang_{LANG}"
            if getattr(stopfunc, flng, None):
                stopfunc.default = getattr(stopfunc, flng)        
stopfunc._reload_lang = _load_lang_backend


def _validate(stop_function, lang_backend="none"):
    s, lb = stop_function, lang_backend
    if isinstance(s, str):
        if re.match(r"lang_[a-z]{2}$", s) and lb != "none" and \
           all(re.match(r"lang_[a-z]{2}$", x) is None for x in dir(stopfunc)):
            stopfunc._reload_lang(lb)
        f = getattr(stopfunc, s, None)
        if f:
            return f
    elif not isinstance(s, FunctionType):
        raise ValueError("Bad stop function")
    return s
stopfunc._validate = _validate


def __guess(prev_input, input, stop_func, depth, max_depth, min_depth, encodings, result, found=(),
            stop=True, show=False, scoring_heuristic=False, extended=False, debug=False):
    """ Perform a breadth-first tree search using a ranking logic to select and prune the list of codecs. """
    if depth > min_depth and stop_func(input):
        if not stop and (show or debug) and found not in result:
            s = repr(input)
            s = s[2:-1] if s.startswith("b'") and s.endswith("'") else s
            s = "[+] {', '.join(found)}: {s}"
            print(s if len(s) <= 80 else s[:77] + "...")
        result[found] = input
    if depth >= max_depth or len(result) > 0 and stop:
        return
    prev_enc = found[-1] if len(found) > 0 else ""
    e = encodings.get(depth, encodings.get(-1, []))
    for new_input, encoding in __rank(prev_input, input, prev_enc, e, scoring_heuristic, extended):
        if len(result) > 0 and stop:
            return
        if debug:
            print(f"[*] Depth %0{len(str(max_depth))}d/%d: {encoding}" % (depth+1, max_depth))
        __guess(input, new_input, stop_func, depth+1, max_depth, min_depth, encodings, result, found + (encoding, ),
                stop, show, scoring_heuristic, extended, debug)


def __make_encodings_dict(include, exclude):
    """ Process encodings inclusion and exclusion lists, listing categories and developping codecs' lists of possible
         encoding names. It also creates a cache with the CodecInfo objects for improving performance. """
    def _develop(d, keep=True):
        d = d or {}
        for k, v in d.items():
            l, cc, sc = [], [e for e in v if e in CODECS_CATEGORIES], [e for e in v if e not in CODECS_CATEGORIES]
            # list from in-scope categories and then everything that is not a category
            for enc in ((list_encodings(*cc) if (len(cc) > 0 or keep) and len(sc) == 0 else []) + sc):
                g = []
                for e in (search(enc, False) or [enc]):
                    try:
                        ci = lookup(e, False)
                        g.extend(ci.parameters['guess'])
                    except:
                        pass
                if enc in g:  # e.g. "rot-1" => ["rot-1", "rot-2", ...] ; only "rot-1" is to be selected
                    l.append(enc)
                else:         # e.g. "rot"   => ["rot-1", "rot-2", ...] ; all the "rot-N" shall be selected
                    l.extend(g)
            d[k] = list(set(l))
        return d
    _excl, _incl = _develop(exclude, False), _develop(include)
    return {k: [x for x in v if x not in _excl.get(k, [])] for k, v in _incl.items()}


def __rank(prev_input, input, prev_encoding, encodings, heuristic=False, extended=False, yield_score=False):
    """ Filter valid encodings and rank them by relevance. """
    ranking = {}
    for e in encodings:
        try:
            codec = CODECS_CACHE[e]
        except KeyError:
            try:
                CODECS_CACHE[e] = codec = lookup(e, False)
            except LookupError:
                continue
        t = __score(prev_input, input, prev_encoding, e, codec, heuristic, extended)
        if t:
            ranking[e] = t
    for encoding, result in sorted(ranking.items(), key=lambda x: (-x[1][0], x[0])):
        yield result if yield_score else result[1], encoding


class _Text(object):
    __slots__ = ["entropy", "lcharset", "len", "padding", "printables", "text"]
    
    def __init__(self, text, pad_char=None):
        self.text = ensure_str(text)
        c = self.text[-1]
        pad_char, last_char = (chr(pad_char), chr(c)) if isinstance(c, int) else (pad_char, c)
        self.padding = pad_char is not None and last_char == pad_char
        if self.padding:
            text = text.rstrip(b(pad_char) if isinstance(text, bytes) else pad_char)
        self.len = len(self.text)
        self.lcharset = len(set(self.text))
        self.printables = float(len([c for c in self.text if c in printable])) / self.len
        self.entropy = entropy(self.text)


def __score(prev_input, input, prev_encoding, encoding, codec, heuristic=False, extended=False):
    """ Score relevant encodings given an input. """
    obj = None
    sc = codec.parameters.get('scoring', {})
    no_error, transitive = codec.parameters.get('no_error', False), sc.get('transitive', False)
    # ignore encodings that fail to decode with their default errors handling value
    try:
        new_input = codec.decode(input)[0]
    except:
        return
    # ignore encodings that give an output identical to the input (identity transformation) or to the previous input
    if len(new_input) == 0 or prev_input is not None and b(input) == b(new_input) or b(prev_input) == b(new_input):
        return
    # ignore encodings that transitively give the same output (identity transformation by chaining twice a same
    #  codec (e.g. rot-15 is equivalent to rot-3 and rot-12 or rot-6 and rot-9)
    if transitive and prev_encoding:
        ci_prev = lookup(prev_encoding, False)
        if ci_prev.parameters['name'] == codec.parameters['name']:
            return
    # compute input's characteristics only once and only if the control flow reaches this point
    pad = sc.get('padding_char')
    if obj is None:
        obj = _Text(input, pad)
    if heuristic:
        # from here, the goal (e.g. if the input is Base32) is to rank candidate encodings (e.g. multiple base
        #  codecs) so that we can put the right one as early as possible and eventually exclude bad candidates
        s = -sc.get('penalty', .0)
        # first, apply a bonus if the length of input text's charset is exactly the same as encoding's charset ;
        #  on the contrary, if the length of input text's charset is strictly greater, give a penalty
        lcs = sc.get('len_charset', 256)
        if isinstance(lcs, type(lambda: None)):
            lcs = int(lcs(encoding))
        if (pad and obj.padding and lcs + 1 >= obj.lcharset) or lcs >= obj.lcharset:
            s += max(.0, round(.6 * (.99 ** (lcs - obj.lcharset)), 5) - .1)
        elif (pad and obj.padding and lcs + 1 < obj.lcharset) or lcs < obj.lcharset:
            s -= .2  # this can occur for encodings with no_error set to True
        # then, take padding into account, giving a bonus if padding is to be encountered and effectively present,
        #  or a penalty when it should not be encountered but it is present
        if pad and obj.padding:
            s += .2  # when padding is encountered while it is legitimate, it could be a good indication => bonus
        elif not pad and obj.padding:
            s -= .1  # it could arise a padding character is encountered while not being padding => small penalty
        # give a bonus when the rate of printable characters is greater or equal than expected and a penalty when
        #  lower only for codecs that DO NOT tolerate errors (otherwise, the printables rate can be biased)
        if not no_error:
            pr = sc.get('printables_rate', 0)
            if isinstance(pr, type(lambda: None)):
                pr = float(pr(obj.printables))
            if obj.printables - pr <= .05:
                s += .1
        expf = sc.get('expansion_factor', 1.)
        if expf:
            f = obj.len / float(len(new_input))  # expansion while encoding => at decoding: 1/f
            if isinstance(expf, type(lambda: None)):
                try:  # this case allows to consider the current encoding name from the current codec
                    expf = expf(f, encoding)
                except TypeError:
                    expf = expf(f)
            if isinstance(expf, (int, float)):
                expf = 1/f - .1 <= 1/expf <= 1/f + .1
            elif isinstance(expf, (tuple, list)) and len(expf) == 2:
                expf = 1/f - expf[1] <= 1/expf[0] <= 1/f + expf[1]
            s += [-1., .1][expf]
        # afterwards, if the input text has an entropy close to the expected one, give a bonus weighted on the
        #  number of input characters to take bad entropies of shorter strings into account
        entr = sc.get('entropy', lambda e: e)
        entr = entr.get(encoding, entr.get('default')) if isinstance(entr, dict) else entr
        if isinstance(entr, type(lambda: None)):
            try:  # this case allows to consider the current encoding name from the current codec
                entr = entr(obj.entropy, encoding)
            except TypeError:
                entr = entr(obj.entropy)
        if entr is not None:
            # use a quadratic heuristic to compute a weight for the entropy delta, aligned on (256,.2) and (512,1)
            d_entr = min(3.04575e-06 * obj.len**2 + .000394 * obj.len, 1) * abs(entr - obj.entropy)
            if d_entr <= .5:
                s += .5 - d_entr
        # finally, if relevant, apply a custom bonus (e.g. when a regex pattern is matched)
        bonus = sc.get('bonus_func')
        if bonus is not None:
            if isinstance(bonus, type(lambda: None)):
                bonus = bonus(obj, codec, encoding)
            if bonus:
                s += .2
    else:
        s = 1.
    # exclude negative (and eventually null) scores as they are (hopefully) not relevant
    if extended and s >= .0 or not extended and s > .0:
        return s, new_input


def guess(input, stop_func=stopfunc.default, min_depth=0, max_depth=5, include=None, exclude=None, found=(),
          stop=True, show=False, scoring_heuristic=True, extended=False, debug=False):
    """ Try decoding without the knowledge of the encoding(s).
    
    :param input:             input text to be guessed
    :param stop_func:         function defining the stop condition
    :param min_depth:         minimum search depth
    :param max_depth:         maximum search depth
    ;param include:           inclusion item OR list with category, codec or encoding names OR dictionary with lists per
                               depth (nothing means include every encoding)
    :param exclude:           exclusion item OR list with category, codec or encoding names OR dictionary with lists per
                               depth (nothing means exclude no encoding)
    :param found:             tuple of already found encodings
    :param stop:              whether to stop or not when a valid solution is found
    :param show:              whether to immediately show once a solution is found
    :param scoring_heuristic: whether to apply the scoring heuristic during the search (if disabled, all scores are 1.,
                               meaning that every non-failing encoding will be considered with no order of precedence)
    :param extended:          whether to also consider null scores with the heuristic
    :param debug:             whether to show each attempt at each depth during computation
    """
    if len(input) == 0:
        return ""
    # check for min and max depths
    if max_depth <= 0:
        raise ValueError("Depth must be a non-null positive integer")
    if min_depth > max_depth:
        raise ValueError("Min depth shall be less than or equal to the max depth")
    # take the tuple of found encodings into account
    if len(found) > 0:
        for encoding in found:
            input = decode(input, encoding)
    # handle the stop function as a regex if a string was given
    if isinstance(stop_func, str):
        stop_func = stopfunc.regex(stop_func)
    # reformat include and exclude arguments ; supported formats:
    for n, l in zip(["inc", "exc"], [include, exclude]):
        if l is None:
            if n == "inc":
                include = l = {-1: CODECS_CATEGORIES}
            else:
                exclude = l = {}
        #  "category" OR "enc_name" OR whatever => means a single item for all depths
        if isinstance(l, str):
            if n == "inc":
                include = l = {-1: [l]}
            else:
                exclude = l = {-1: [l]}
        #  ["enc_name1", "enc_name2", ...] => means for all depths
        if isinstance(l, (list, tuple)):
            if n == "inc":
                include = l = {-1: l}
            else:
                exclude = l = {-1: l}
        #  {-1: [...], 2: [...], ...}      => means prefedined depths with their lists of in-/excluded encodings
        if not isinstance(l, dict) or not all(isinstance(k, int) for k in l.keys()):
            raise ValueError("Include argument shall be a list or a dictionary with integer keys")
    # precompute encodings lists per depth and cache the related CodecInfo objects
    encodings, result = __make_encodings_dict(include, exclude), {}
    try:
        # breadth-first search
        for d in range(max_depth):
            __guess("", input, stop_func, 0, d+1, min_depth, encodings, result, tuple(found), stop, show,
                    scoring_heuristic, extended, debug)
            if stop and len(result) > 0:
                break
    except KeyboardInterrupt:
        pass
    CODECS_CACHE = {}
    return result
codecs.guess = guess


def rank(input, extended=False, limit=-1, include=None, exclude=None):
    """ Rank the most probable encodings based on the given input.
    
    :param input:    input text to be evaluated
    :param extended: whether to consider null scores too (NB: negative scores are not output !)
    :param limit:    number of encodings to be returned (-1 means all of them)
    :param include:  inclusion list with category, codec or encoding names (nothing means include every encoding)
    :param exclude:  exclusion list with category, codec or encoding names (nothing means exclude no encoding)
    """
    encodings = __make_encodings_dict(include if isinstance(include, dict) else {-1: include or CODECS_CATEGORIES},
                                      exclude if isinstance(exclude, dict) else {-1: exclude or []})
    r = list(__rank(None, input, "", encodings[-1], True, extended, True))
    return r[:limit] if len(r) > 1 else r
codecs.rank = rank

