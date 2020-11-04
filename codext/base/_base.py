# -*- coding: UTF-8 -*-
"""Generic baseN functions.

"""
from math import log
from six import integer_types, string_types
from string import printable
from types import FunctionType

from ..__common__ import *


class BaseError(ValueError):
    pass


class BaseDecodeError(BaseError):
    pass


class BaseEncodeError(BaseError):
    pass


def _generate_charset(n):
    """
    Generate a characters set.
    
    :param n: size of charset
    """
    if 1 < n <= len(printable):
        return printable[:n]
    elif len(printable) < n < 256:
        return "".join(chr(i) for i in range(n))
    raise ValueError("Bad size of character set")


def _get_charset(charset, p=""):
    """
    Characters set selection function. It allows to define charsets in many different ways.
    
    :param charset: charset object, can be a string (the charset itself), a function (that chooses the right charset
                     depending on the input parameter) or a dictionary (either by exact key or by pattern matching)
    :param p:       the parameter for choosing the charset
    """
    # case 1: charset is a function, so return its result
    if isinstance(charset, FunctionType):
        return charset(p)
    # case 2: charset is a string, so return it
    elif isinstance(charset, string_types):
        return charset
    # case 3: charset is a dict with keys '' and 'inv', typically for a charset using lowercase and uppercase characters
    #          that can be inverted
    elif isinstance(charset, dict) and list(charset.keys()) == ["", "inv"]:
        return charset["inv" if re.match(r"[-_]inv(erted)?$", p) else ""]
    # case 4: charset is a dict, but not with the specific keys '' and 'inv', so consider it as pattern-charset pairs
    elif isinstance(charset, dict):
        # try to handle [p]arameter as a simple key
        try:
            return charset[p]
        except KeyError:
            pass
        # or handle [p]arameter as a pattern
        default, n = None, None
        for pattern, cset in charset.items():
            n = len(cset)
            if pattern == "":
                default = cset
                continue
            if re.match(pattern, p):
                return cset
        # special case: the given [p]arameter can be the charset itself if it has the right length
        p = re.sub(r"^[-_]+", "", p)
        if len(p) == n:
            return p
        # or simply rely on key ''
        if default is not None:
            return default
    raise ValueError("Bad charset descriptor")


# generic base en/decoding functions
def base_encode(input, charset, errors="strict", exc=BaseEncodeError):
    """
    Base-10 to base-N encoding.
    
    :param input:   input (str or int) to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    i = input if isinstance(input, integer_types) else s2i(input)
    n = len(charset)
    r = ""
    while i > 0:
        i, c = divmod(i, n)
        r = charset[c] + r
    return r


def base_decode(input, charset, errors="strict", exc=BaseDecodeError):
    """
    Base-N to base-10 decoding.
    
    :param input:   input to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    i, n = 0, len(charset)
    for k, c in enumerate(input):
        try:
            i = i * n + charset.index(c)
        except ValueError:
            handle_error("base", errors, exc, decode=True)(c, k)
    return base_encode(i, [chr(j) for j in range(256)], errors, exc)


# base codec factory functions
def base(charset, pattern, pow2=False, encode_template=base_encode, decode_template=base_decode, name=None):
    """
    Base-N codec factory.
    
    :param charset: charset selection function
    :param pattern: matching pattern for the codec name (first capturing group is used as the parameter for selecting
                     the charset)
    :param pow2:    whether the base codec's N is a power of 2
    """
    n = len(_get_charset(charset))
    nb = log(n, 2)
    if pow2 and nb != int(nb):
        raise BaseError("Bad charset ; {} is not a power of 2".format(n))
    
    def encode(param=""):
        a = _get_charset(charset, param)
        def _encode(input, errors="strict"):
            return encode_template(input, a, errors), len(input)
        return _encode
    
    def decode(param=""):
        a = _get_charset(charset, param)
        def _decode(input, errors="strict"):
            return decode_template(input, a, errors), len(input)
        return _decode
    
    add("base{}".format(n) if name is None else name, encode, decode, pattern)


def base_generic():
    """
    Base-N generic codec.
    """
    def encode(n):
        a = _generate_charset(int(n))
        def _encode(input, errors="strict"):
            return base_encode(input, a, errors), len(input)
        return _encode
    
    def decode(n):
        a = _generate_charset(int(n))
        def _decode(input, errors="strict"):
            return base_decode(input, a, errors), len(input)
        return _decode
    
    add("base", encode, decode, r"^base[-_]?([2-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?:[-_]generic)?$",
        guess=["base%d-generic" % i for i in range(2, 255)])

