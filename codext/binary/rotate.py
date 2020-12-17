# -*- coding: UTF-8 -*-
"""Rotate-Bits Codec - rotate-N-bits content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import operator

from ..__common__ import *


__examples__ = {
    'enc(rotate-0|rotate-8|rotate-left-8)': None,
    'enc(rotate1|rotate-right-1|rotate_1)': {'This is a test': "*449\x1049\x100\x10:29:"},
    'dec(rotate1)':                         {'*449\x1049\x100\x10:29:': "Thhr hr ` tdrt"},
    'enc(rotate-left-1|rotate_left_1)':     {'This is a test': "¨ÐÒæ@Òæ@Â@èÊæè"},
}
__guess__ = ["rotate-%s" % i for i in "12"] + ["rotate-left-%s" % i for i in "12"]


if PY3:
    def _getn(i):
        m = 1
        if str(i).startswith("left"):
            i = i[4:].lstrip("-_")
            m = -1
        return m * int(i)


    def _rotaten(text, n=1):
        op = [operator.lshift, operator.rshift][n > 0]
        n = abs(n)
        return "".join(chr(op(ord(c), n)) for c in ensure_str(text))


    def rotate_encode(i):
        def encode(text, errors="strict"):
            return _rotaten(text, _getn(i)), len(text)
        return encode


    def rotate_decode(i):
        def decode(text, errors="strict"):
            return _rotaten(text, -_getn(i)), len(text)
        return decode


    add("rotate", rotate_encode, rotate_decode, r"rotate(?:[-_]?bits)?[-_]?((?:left[-_]?)?[1-7])$")

