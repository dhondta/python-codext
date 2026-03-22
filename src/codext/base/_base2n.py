# -*- coding: UTF-8 -*-
"""BaseN functions with N a power of 2.

"""
from math import ceil, log

from ..__common__ import *
from ..__common__ import _set_exc
from ._base import base, _get_charset


_bin = lambda x: bin(x if isinstance(x, int) else ord(x))


# base en/decoding functions for N a power of 2
_set_exc("Base2NDecodeError")
_set_exc("Base2NEncodeError")


def base2n(charset, pattern=None, name=None, **kwargs):
    """ Base-N codec factory for N a power of 2.
    
    :param charset: charset selection function
    :param pattern: matching pattern for the codec name (first capturing group is used as the parameter for selecting
                     the charset)
    :param name:    forced encoding name (useful e.g. for zbase32)
    """
    base(charset, pattern, True, base2n_encode, base2n_decode, name, **kwargs)


def base2n_encode(string, charset, errors="strict"):
    """ 8-bits characters to base-N encoding for N a power of 2.
    
    :param string:  string to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    """
    bs, r, n = "", "", len(charset)
    # find the number of bits for the given character set and the quantum
    nb_out = int(log(n, 2))
    q = nb_out
    while q % 8 != 0:
        q += nb_out
    # iterate over the characters, gathering bits to be mapped to the charset
    for i, c in enumerate(b(string)):
        bs += "{:0>8}".format(_bin(c)[2:])
        while len(bs) >= nb_out:
            r += charset[int(bs[:nb_out], 2)]
            bs = bs[nb_out:]
    if len(bs) > 0:
        for i in range(0, len(bs), nb_out):
            c = ("{:0<%d}" % nb_out).format(bs[i:i+nb_out])
            p = len(c) - len(bs[i:i+nb_out])
            r += charset[int(c, 2)]
    l = len(r) * nb_out
    while l % q != 0:
        l += nb_out
    return r + int(l / nb_out - len(r)) * "="


def base2n_decode(string, charset, errors="strict"):
    """ Base-N to 8-bits characters decoding for N a power of 2.
    
    :param string:  string to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    """
    bs, r, n = "", "", len(charset)
    # particular case: for hex, ensure the right case in the charset ; not that this way, if mixed cases are used, it
    #                   will trigger an error (this is the expected behavior)
    if n == 16:
        if any(c in string for c in "abcdef"):
            charset = charset.lower()
        elif any(c in string for c in "ABCDEF"):
            charset = charset.upper()
    string = re.sub(r"\s", "", string)
    # find the number of bits for the given character set and the number of padding characters
    nb_in = int(log(n, 2))
    n_pad = len(string) - len(string.rstrip("="))
    # iterate over the characters, mapping them to the character set and converting the resulting bits to 8-bits chars
    for i, c in enumerate(string):
        if c == "=":
            bs += "0" * nb_in
        else:
            try:
                bs += ("{:0>%d}" % nb_in).format(_bin(charset.index(c))[2:])
            except ValueError:
                if errors == "strict":
                    e = Base2NDecodeError("'base%d' codec can't decode character '%s' in position %d" % (n, c, i))
                    e.__cause__ = e  # block exceptions chaining
                    raise e
                elif errors == "replace":
                    bs += "0" * nb_in
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}".format(errors))
        if len(bs) > 8:
            r += chr(int(bs[:8], 2))
            bs = bs[8:]
    # if the number of bits is not multiple of 8 bits, it could mean a bad padding
    if len(bs) != 8:
        if errors == "strict":
            raise Base2NDecodeError("Incorrect padding")
        elif errors in ["replace", "ignore"]:
            pass
        else:
            raise ValueError("Unsupported error handling {}".format(errors))
    r += chr(int(bs, 2))
    np = int(ceil(n_pad * nb_in / 8.0))
    return r[:-np] if np > 0 else r

