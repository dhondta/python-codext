# -*- coding: UTF-8 -*-
import _codecs
import codecs
import re
import sys
import types
from functools import wraps
from six import binary_type, string_types, text_type


__all__ = ["add", "b", "codecs", "ensure_str", "re", "PY3"]
PY3 = sys.version[0] == "3"


isb = lambda s: isinstance(s, binary_type)
iss = lambda s: isinstance(s, string_types)
fix = lambda x, ref: b(x) if isb(ref) else ensure_str(x) if iss(ref) else x


def add(ename, encode=None, decode=None, pattern=None, text=True):
    """
    This adds a new codec to the codecs module setting its encode and/or decode
     functions, eventually dynamically naming the encoding with a pattern and
     with file handling (if text is True).
    
    :param ename:   encoding name
    :param encode:  encoding function or None
    :param decode:  decoding function or None
    :param pattern: pattern for dynamically naming the encoding
    :param text:    specify whether the codec is a text encoding
    """
    if encode and not isinstance(encode, types.FunctionType):
        raise ValueError("Bad encode function")
    if decode and not isinstance(decode, types.FunctionType):
        raise ValueError("Bad decode function")
    if not encode and not decode:
        raise ValueError("At least one function must be defined")
    # search function for the new encoding
    def getregentry(encoding):
        if encoding != ename and not (pattern and re.match(pattern, encoding)):
            return
        fenc, fdec, name = encode, decode, encoding
        # prepare CodecInfo input arguments
        class Codec(codecs.Codec):
            def encode(self, input, errors='strict'):
                if fenc is None:
                    raise NotImplementedError
                return fenc(input, errors)

            def decode(self, input, errors='strict'):
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
                g = m.group(1)
                if g.isdigit():
                    g = int(g)
                fenc = fenc(g) if fenc else fenc
                fdec = fdec(g) if fdec else fdec
            except AttributeError:
                return  # this occurs when m is None, meaning no match
            except IndexError:
                pass    # this occurs while m is not None, but possibly no
                        #  capture group that gives at least 1 group index
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
    codecs.register(getregentry)
codecs.add = add


def b(s):
    """
    Non-crashing bytes conversion function.
    """
    if PY3:
        try:
            return s.encode("latin-1")
        except:
            pass
        try:
            return s.encode("utf-8")
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
orig_lookup                = _codecs.lookup
orig_register              = _codecs.register
_ts_codecs_registry        = []
_ts_codecs_registry_hashes = []


def __decode(obj, encoding='utf-8', errors='strict'):
    """
    Custom decode function relying on the hooked lookup function.
    """
    codecinfo = __lookup(encoding)
    return codecinfo.decode(obj, errors)[0]
codecs.decode = __decode


def __encode(obj, encoding='utf-8', errors='strict'):
    """
    Custom encode function relying on the hooked lookup function.
    """
    codecinfo = __lookup(encoding)
    return codecinfo.encode(obj, errors)[0]
codecs.encode = __encode


def __lookup(encoding):
    """
    Hooked lookup function for searching first for codecs in the local registry
     of this module.
    """
    for search in _ts_codecs_registry:
        codecinfo = search(encoding)
        if codecinfo is not None:
            return codecinfo
    return orig_lookup(encoding)
codecs.lookup = __lookup


def __register(search_function):
    """
    Hooked register function for registering new codecs in the local registry
     of this module.
    """
    h = hash(search_function)
    if h not in _ts_codecs_registry_hashes:
        _ts_codecs_registry_hashes.append(h)
        _ts_codecs_registry.append(search_function)
    orig_register(search_function)
codecs.register = __register
