# -*- coding: UTF-8 -*-
"""Barbie typewriter Codec - barbie content encoding.

While Barbie typewriter is more a cipher, its very limited key size of 2 bits
 makes it easy to turn into four variants of the same encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://www.cryptomuseum.com/crypto/mehano/barbie/
"""
from .__common__ import *


REPLACE_CHAR = "?"
STD = [
    "abcdefghijklmnopqrstuvABCDEFGHIJKLMNOPQRSTUVWXYZ0123456 \n\t",
    "icolapxstvybjeruknfhqg>FAUTCYOLVJDZINQKSEHG<.1PB5234067 \n\t",
    "torbiudfhgzcvanqyepskxRC>GHAPND<VUBLIKJETOYXM2QF6340578 \n\t",
    "hrnctqlpsxwogiekzaufydSARYO>QIUX<GFDLJVTHNP1Z3KC7405689 \n\t",
    "sneohkbufd;rxtaywiqpzlE>SPNRKLG1XYCUDV<HOIQ2B4JA805679- \n\t",
]
SPEC = [
    "w x y z 7 8 9 - \' ! \" # % & ( ) * , . ¨ / : ; ? @ ^ _ + < = > ¢ £ § €",
    "; d z w 8 9 - ¨ _ & m @ : \" * ( # W M § ^ , ¢ / ? ! ) % X \' R + € £ =",
    "¢ l w ; 9 - ¨ § ) \" j ? , m # * @ . Z £ ! W + ^ / & ( : 1 _ S % = € \'",
    "+ b ; ¢ - ¨ § £ ( m v / W j @ # ? M B € & . % ! ^ \" * , 2 ) E : \' = _",
    "% c ¢ + ¨ § £ € * j g ^ . v ? @ / Z F = \" N : & ! m # W 3 ( T , _ \' )",
]


class BarbieError(ValueError):
    pass


class BarbieDecodeError(BarbieError):
    pass


class BarbieEncodeError(BarbieError):
    pass


def barbie_encode(code):
    def encode(text, errors="strict"):
        std0, stdn = [c for c in STD[0]], [c for c in STD[code]]
        spec0, specn = SPEC[0].split(), SPEC[code].split()
        mapping = {d: e for d, e in zip(std0 + spec0, stdn + specn)}
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += mapping[c]
            except KeyError:
                if errors == "strict":
                    raise BarbieEncodeError("'barbie' codec can't encode"
                                            " character '{}' in position {}"
                                            .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)
    return encode


def barbie_decode(code):
    def decode(text, errors="strict"):
        std0, stdn = [c for c in STD[0]], [c for c in STD[code]]
        spec0, specn = SPEC[0].split(), SPEC[code].split()
        mapping = {e: d for d, e in zip(std0 + spec0, stdn + specn)}
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += mapping[c]
            except KeyError:
                if errors == "strict":
                    raise BarbieDecodeError("'barbie' codec can't decode"
                                            " character '{}' in position {}"
                                            .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)
    return decode


# note: the integer behind "barbie" is captured for sending to the
#        parametrizable encode and decode functions "barbie_**code"
add("barbie", barbie_encode, barbie_decode, r"barbie[-_]?([1-4])$")
