# -*- coding: UTF-8 -*-
"""BCD Codec - Binary Coded Decimal content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples1__ = {
    'enc(bcd|binary-coded-decimal|binary_coded_decimal)': {
        'This is a test!': "\x08A\x04\x10Q\x15\x03!\x05\x11P2\tp2\x11a\x01\x11Q\x16\x030",
   },
    'dec(binary-coded-decimal)': {
        '\xaf':                                                         None,
        '\xff':                                                         None,
        '\x08A\x04\x10Q\x15\x03!\x05\x11P2\tp2\x11a\x01\x11Q\x16\x030': "This is a test!",
   },
}
__examples2__ = {
    'enc(bcd-ext0|bcd_extended_zeros)': {
        'This is a test': "\x00\x08\x04\x01\x00\x04\x01\x00\x05\x01\x01\x05\x00\x03\x02\x01\x00\x05\x01\x01\x05\x00"
                          "\x03\x02\x00\t\x07\x00\x03\x02\x01\x01\x06\x01\x00\x01\x01\x01\x05\x01\x01\x06\x00",
   },
}
__examples3__ = {
    'enc(bcd-ext1|bcd_extended_ones)': {
        'This is a test': "\xf0\xf8\xf4\xf1\xf0\xf4\xf1\xf0\xf5\xf1\xf1\xf5\xf0\xf3\xf2\xf1\xf0\xf5\xf1\xf1\xf5\xf0"
                          "\xf3\xf2\xf0\xf9\xf7\xf0\xf3\xf2\xf1\xf1\xf6\xf1\xf0\xf1\xf1\xf1\xf5\xf1\xf1\xf6\xf0",
   },
}


CODE = {str(i): bin(i)[2:].zfill(4) for i in range(10)}


def bcd_encode(prefix=""):
    def encode(text, errors="strict"):
        r, bits = "", prefix
        for c in text:
            for i in str(ord(c)).zfill(3):
                bits += CODE[i]
                if len(bits) == 8:
                    r += chr(int(bits, 2))
                    bits = prefix
        if len(bits) > 0:
            r += chr(int(bits + "0000", 2))
        return r, len(b(text))
    return encode


def bcd_decode(prefix=""):
    def decode(text, errors="strict"):
        code = {v: k for k, v in CODE.items()}
        r, d = "", ""
        for i, c in enumerate(text):
            bin_c = bin(ord(c))[2:].zfill(8)
            for k in range(len(prefix), 8, 4):
                hb = bin_c[k:k+4]
                try:
                    d += code[hb]
                except KeyError:
                    d += handle_error("bcd", errors, decode=True)(hb, i)
                if len(d) == 3:
                    r += chr(int(d))
                    d = ""
        return r, len(b(text))
    return decode


add("bcd", bcd_encode(), bcd_decode(), pattern=r"^(?:bcd|binary[-_]coded[-_]decimals?)$", examples=__examples1__,
    entropy=lambda e: .45739*e+2.63519, printables_rate=.2)
add("bcd-extended0", bcd_encode("0000"), bcd_decode("0000"), examples=__examples2__, entropy=lambda e: .13584*e+2.07486,
    pattern=r"^(?:bcd|binary[-_]coded[-_]decimals?)[-_]ext(?:ended)?(?:[-_]?0|[-_]zeros?)$")
add("bcd-extended1", bcd_encode("1111"), bcd_decode("1111"), examples=__examples3__, entropy=lambda e: .13584*e+2.07486,
    pattern=r"^(?:bcd|binary[-_]coded[-_]decimals?)[-_]ext(?:ended)?(?:[-_]?1|[-_]ones?)$")

