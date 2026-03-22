# -*- coding: UTF-8 -*-
"""Rotate-Bits Codec - rotate-N-bits content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(rotate-0|rotate-8|rotate-left-8)': None,
    'enc(rotate1|rotate-right-1|rotate_1)': {'This is a test': "*4\xb4\xb9\x10\xb4\xb9\x10\xb0\x10:\xb2\xb9:"},
    'enc(rotate-left-1|rotate_left_1)':     {'This is a test': "¨ÐÒæ@Òæ@Â@èÊæè"},
}
__guess__ = ["rotate-%d" % i for i in range(1, 8)] + ["rotate-left-%d" % i for i in range(1, 8)]


def _getn(i):
    m = 1
    if str(i).startswith("left"):
        i = i[4:].lstrip("-_")
        m = -1
    return m * int(i)


def _rotaten(text, n=1):
    r = ""
    for c in ensure_str(text):
        b = bin(ord(c))[2:].zfill(8)
        r += chr(int(b[-n:] + b[:-n], 2))
    return r


def rotate_encode(i):
    def encode(text, errors="strict"):
        return _rotaten(text, _getn(i)), len(text)
    return encode


def rotate_decode(i):
    def decode(text, errors="strict"):
        return _rotaten(text, -_getn(i)), len(text)
    return decode


add("rotate", rotate_encode, rotate_decode, r"rotate(?:[-_]?bits)?[-_]?((?:(?:left|right)[-_]?)?[1-7])$",
    transitive=True)

