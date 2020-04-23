# -*- coding: UTF-8 -*-
import _codecs
import codecs
import os
import re
import sys
from functools import wraps
from importlib import import_module
from inspect import currentframe
from six import binary_type, string_types, text_type
from types import FunctionType
try:  # Python3
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
try: # Python3
    from importlib import reload
except ImportError:
    pass
try:                 # Python 2
    from string import maketrans
except ImportError:  # Python 3
    maketrans = str.maketrans


__all__ = ["add", "add_map", "b", "clear", "codecs", "ensure_str", "maketrans", "re", "register", "remove", "reset",
           "s2i", "PY3"]
CODECS_REGISTRY = None
PY3 = sys.version[0] == "3"
__codecs_registry = []


isb = lambda s: isinstance(s, binary_type)
iss = lambda s: isinstance(s, string_types)
fix = lambda x, ref: b(x) if isb(ref) else ensure_str(x) if iss(ref) else x

s2i = lambda s: int(codecs.encode(s, "base16"), 16)


def add(ename, encode=None, decode=None, pattern=None, text=True, add_to_codecs=False):
    """
    This adds a new codec to the codecs module setting its encode and/or decode functions, eventually dynamically naming
     the encoding with a pattern and with file handling (if text is True).
    
    :param ename:         encoding name
    :param encode:        encoding function or None
    :param decode:        decoding function or None
    :param pattern:       pattern for dynamically naming the encoding
    :param text:          specify whether the codec is a text encoding
    :param add_to_codecs: also add the search function to the native registry
                           NB: this will make the codec available in the built-in open(...) but will make it impossible
                                to remove the codec later
    """
    if encode and not isinstance(encode, FunctionType):
        raise ValueError("Bad 'encode' function")
    if decode and not isinstance(decode, FunctionType):
        raise ValueError("Bad 'decode' function")
    if not encode and not decode:
        raise ValueError("At least one en/decoding function must be defined")
    # search function for the new encoding
    def getregentry(encoding):
        if encoding != ename and not (pattern and re.match(pattern, encoding)):
            return
        fenc, fdec, name = encode, decode, encoding
        # prepare CodecInfo input arguments
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
        
        incrementalencoder = IncrementalEncoder
        incrementaldecoder = IncrementalDecoder
        streamwriter       = None
        streamreader       = None
        if pattern:
            m = re.match(pattern, encoding)
            try:
                g = m.group(1) or ""
                if g.isdigit():
                    g = int(g)
                fenc = fenc(g) if fenc else fenc
                fdec = fdec(g) if fdec else fdec
            except AttributeError:
                return  # this occurs when m is None, meaning no match
            except IndexError:
                # this occurs while m is not None, but possibly no capture group that gives at least 1 group index ; in
                #  this case, if fenc/fdec is a decorated function, execute it with no arg
                if fenc and len(getfullargspec(fenc).args) == 1:
                    fenc = fenc()
                if fdec and len(getfullargspec(fdec).args) == 1:
                    fdec = fdec()
        if fenc:
            fenc = fix_inout_formats(fenc)
        if fdec:
            fdec = fix_inout_formats(fdec)
        
        if text:
            
            class StreamWriter(Codec, codecs.StreamWriter):
                charbuffertype = bytes

            class StreamReader(Codec, codecs.StreamReader):
                charbuffertype = bytes
            
            streamwriter = StreamWriter
            streamreader = StreamReader
        
        return codecs.CodecInfo(
            name=name,
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=incrementalencoder,
            incrementaldecoder=incrementaldecoder,
            streamwriter=streamwriter,
            streamreader=streamreader,
            _is_text_encoding=text,
        )
    getregentry.__name__ = re.sub(r"[\s\-]", "_", ename)
    register(getregentry, add_to_codecs)


def add_map(ename, encmap, repl_char="?", sep="", ignore_case=False, no_error=False, binary=False, **kwargs):
    """
    This adds a new mapping codec (that is, declarable with a simple character mapping dictionary) to the codecs module
     dynamically setting its encode and/or decode functions, eventually dynamically naming the encoding with a pattern
     and with file handling (if text is True).
    
    :param ename:         encoding name
    :param encmap:        characters encoding map ; can be a dictionary of encoding maps (for use with the first capture
                           group of the regex pattern)
    :param repl_char:     replacement char (used when errors handling is set to "replace")
    :param sep:           string of possible character separators (hence, only single-char separators are considered) ;
                           - while encoding, the first separator is used
                           - while decoding, separators can be mixed in the input text
    :param ignore_case:   ignore text case
    :param no_error:      this encoding triggers no error (hence, always in "leave" errors handling)
    :param binary:        encoding applies to the binary string of the input text
    :param pattern:       pattern for dynamically naming the encoding
    :param text:          specify whether the codec is a text encoding
    :param add_to_codecs: also add the search function to the native registry
                           NB: this will make the codec available in the built-in open(...) but will make it impossible
                                to remove the codec later
    """
    def __generic_code(mapdict, exc, decode=False):
        def _wrapper(param):
            """
            The parameter for wrapping comes from the encoding regex pattern ; e.g.
                [no pattern]           => param will be None everytime
                r"barbie[-_]?([1-4])$" => param could be int 1, 2, 3 or 4
                r"^morse(|[-_]?.{3})$" => param could be None, "-ABC" (for mapping to ".-/")
            
            In order of precedence:
            1. when param is a key in mapdict or mapdict is a list of encoding maps (hence in the case of "barbie...",
                param MUST be an int, otherwise for the first case it could clash with a character of the encoding map)
            2. otherwise handle it as a new encoding character map "ABC" translates to ".-/" for morse
            """
            if isinstance(mapdict, dict):
                smapdict = {k: v for k, v in mapdict.items()}
            elif isinstance(mapdict, list) and isinstance(mapdict[0], dict):
                smapdict = {k: v for k, v in mapdict[0].items()}
            else:
                raise ValueError("Bad mapping dictionary or list of mapping dictionaries")
            if param:
                # case 1: list or dictionary of parameter-dependent encodings
                if isinstance(param, int):
                    if isinstance(mapdict, list):
                        param -= 1
                    if isinstance(mapdict, list) and 0 <= param < len(mapdict) or \
                       isinstance(mapdict, dict) and param in mapdict.keys():
                        smapdict = mapdict[param]
                    else:
                        raise LookupError("Bad parameter for encoding '{}': {}".format(ename, param))
                # case 2: encodinc characters translation
                else:
                    # collect base tokens in order of appearance in the mapping dictionary
                    base_tokens = ""
                    for _, c in sorted(mapdict.items()):
                        for t in c:
                            if t not in base_tokens:
                                base_tokens += t
                    if param[0] in "-_" and len(param[1:]) == len(set(param[1:])) == len(base_tokens):
                        param = param[1:]
                    if len(param) == len(set(param)) == len(base_tokens):
                        t = maketrans(base_tokens, param)
                        for k, v in smapdict.items():
                            smapdict[k] = v.translate(t)
                    else:
                        raise LookupError("Bad parameter for encoding '{}': {}".format(ename, param))
            if ignore_case:
                case = ["upper", "lower"][any(c in "".join(smapdict.keys()) for c in "abcdefghijklmnopqrstuvwxyz")]
            # use the first mapped group from the mapping dictionary to determine token length ; this is useful e.g. for
            #  tokenizing a binary string when the text is to be converted as binary
            tlen = len(list(smapdict.keys())[0])
            if decode:
                tmp = {}
                # this has a meaning for encoding maps that could have clashes in encoded chars (e.g. Bacon's cipher ;
                #  I => abaaa but also J => abaaa, with the following, we keep I instead of letting J overwrite it)
                for k, v in smapdict.items():
                    if v not in tmp.keys():
                        tmp[v] = k
                smapdict = tmp
            # this allows to avoid an error with Python2 in the "for i, c in enumerate(parts)" loop
            if '' not in smapdict.keys():
                smapdict[''] = ""
            
            def code(text, errors="strict"):
                if ignore_case:
                    text = getattr(text, case)()
                if no_error:
                    errors = "leave"
                text = ensure_str(text)
                if binary and not decode:
                    text = "".join("{:0>8}".format(bin(ord(c))[2:]) for c in text)
                    text = [text[i:i+tlen] for i in range(0, len(text), tlen)]
                parts = re.split("[" + sep + "]", text) if decode and len(sep) > 0 else text
                r = ""
                lsep = "" if decode else sep if len(sep) <= 1 else sep[0]
                for i, c in enumerate(parts):
                    try:
                        r += smapdict[c] + lsep
                    except KeyError:
                        if errors == "strict":
                            raise exc("'{}' codec can't {}code character '{}' in position {}"
                                      .format(ename, ["en", "de"][decode], c, i))
                        elif errors == "leave":
                            r += c + lsep
                        elif errors == "replace":
                            r += repl_char * [1, tlen][decode] + lsep
                        elif errors == "ignore":
                            continue
                        else:
                            raise ValueError("Unsupported error handling '{}'".format(errors))
                if binary and decode:
                    tmp, r = "", r.replace(lsep, "")
                    for i in range(0, len(r), 8):
                        bs = r[i:i+8]
                        try:
                            tmp += chr(int(bs, 2))
                        except ValueError:
                            if len(bs) > 0:
                                tmp += "[" + bs + "]"
                    r = tmp + lsep
                return r[:len(r)-len(lsep)], len(text)
            return code
        if re.search(r"\([^(?:)]", kwargs.get('pattern', "")) is None:
            # in this case, there is no capturing group for parametrization
            return _wrapper(None)
        return _wrapper

    name = "".join(t.capitalize() for t in re.split(r"[-_]", ename))
    glob = currentframe().f_back.f_globals
    # dynamically make dedicated exception classes
    decexc = "{}DecodeError".format(name)
    exec("class {}(ValueError): pass".format(decexc), glob)
    encexc = "{}EncodeError".format(name)
    exec("class {}(ValueError): pass".format(encexc), glob)
    # now use the generic add() function
    add(ename, __generic_code(encmap, glob[encexc]), __generic_code(encmap, glob[decexc], True), **kwargs)
codecs.add_map = add_map


def clear():
    """
    Clear codext's local registry of search functions.
    """
    global __codecs_registry
    __codecs_registry = []
codecs.clear = clear


def remove(encoding):
    """
    Remove all search functions matching the input encoding name from codext's
     local registry.
    
    :param encoding: encoding name
    """
    tbr = []
    for search in __codecs_registry:
        if search(encoding) is not None:
            tbr.append(search)
    for search in tbr:
        __codecs_registry.remove(search)
codecs.remove = remove


def reset():
    """
    Reset codext's local registry of search functions.
    """
    global CODECS_REGISTRY, __codecs_registry
    clear()
    for pkg in ["base", "crypto", "languages", "others", "stegano"]:
        reload(import_module("codext." + pkg))
    # backup codext's registry
    if CODECS_REGISTRY is None:
        CODECS_REGISTRY = __codecs_registry[:]
    # restore codext's registry
    else:
        __codecs_registry = CODECS_REGISTRY[:]
codecs.reset = reset


# conversion functions
def b(s):
    """
    Non-crashing bytes conversion function.
    """
    if PY3:
        try:
            return s.encode("utf-8")
        except:
            pass
        try:
            return s.encode("latin-1")
        except:
            pass
    return s


def ensure_str(s, encoding='utf-8', errors='strict'):
    """
    Similar to six.ensure_str. Adapted here to avoid messing up with six version
     errors.
    """
    if not PY3 and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif PY3 and isinstance(s, binary_type):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    return s


# make conversion functions compatible with input/output strings/bytes
def fix_inout_formats(f):
    """
    This decorator ensures that the first output of f will have the same text
     format as the first input (str or bytes).
    """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        a0 = args[0]
        a0 = ensure_str(a0) if iss(a0) or isb(a0) else a0
        r = f(a0, *args[1:], **kwargs)
        return (fix(r[0], args[0]), ) + r[1:] if isinstance(r, (tuple, list)) \
               else fix(r, args[0])
    return _wrapper


# codecs module hooks
orig_lookup   = _codecs.lookup
orig_register = _codecs.register


def __add(ename, encode=None, decode=None, pattern=None, text=True, add_to_codecs=True):
    add(ename, encode, decode, pattern, text, add_to_codecs)
__add.__doc__ = add.__doc__
codecs.add = __add


def __decode(obj, encoding='utf-8', errors='strict'):
    """
    Custom decode function relying on the hooked lookup function.
    """
    return __lookup(encoding).decode(obj, errors)[0]
codecs.decode = __decode


def __encode(obj, encoding='utf-8', errors='strict'):
    """
    Custom encode function relying on the hooked lookup function.
    """
    return __lookup(encoding).encode(obj, errors)[0]
codecs.encode = __encode


def __lookup(encoding):
    """
    Hooked lookup function for searching first for codecs in the local registry
     of this module.
    """
    for search in __codecs_registry:
        codecinfo = search(encoding)
        if codecinfo is not None:
            return codecinfo
    return orig_lookup(encoding)
codecs.lookup = __lookup


def register(search_function, add_to_codecs=False):
    """
    Register function for registering new codecs in the local registry of this
     module and, if required, in the native codecs registry (for use with the
     built-in 'open' function).
    
    :param search_function: search function for the codecs registry
    :param add_to_codecs:   also add the search function to the native registry
                            NB: this will make the codec available in the
                                 built-in open(...) but will make it impossible
                                 to remove the codec later
    """
    if search_function not in __codecs_registry:
        __codecs_registry.append(search_function)
    if add_to_codecs:
        orig_register(search_function)


def __register(search_function, add_to_codecs=True):
    """
    Hooked register function for registering new codecs in the local registry
     of this module and in the native codecs registry (for use with the built-in
     'open' function).
    
    :param search_function: search function for the codecs registry
    :param add_to_codecs:   also add the search function to the native registry
                            NB: this will make the codec available in the
                                 built-in open(...) but will make it impossible
                                 to remove the codec later
    """
    register(search_function, add_to_codecs)
codecs.register = __register
