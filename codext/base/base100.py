# -*- coding: UTF-8 -*-
"""Base100 Codec - base100 content encoding.

Note: only works in Python3 ; strongly inspired from https://github.com/MasterGroosha/pybase100

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


# no __examples__ ; handled manually in tests/test_base.py


if PY3:
    class Base100DecodeError(ValueError):
        pass
    
    
    def base100_encode(input, errors='strict'):
        input = b(input)
        r = [240, 159, 0, 0] * len(input)
        for i, c in enumerate(input):
            r[4*i+2] = (c + 55) // 64 + 143
            r[4*i+3] = (c + 55) % 64 + 128
        return bytes(r), len(input)
    
    
    def base100_decode(input, errors='strict'):
        input = b(input)
        if len(input) % 4 != 0:
            raise Base100DecodeError("Bad input (length should be multiple of 4)")
        r = [None] * (len(input) // 4)
        for i, c in enumerate(input):
            if i % 4 == 2:
                tmp = ((c - 143) * 64) % 256
            elif i % 4 == 3:
                r[i//4] = (c - 128 + tmp - 55) & 0xff
        return bytes(r), len(input)
    
    
    add("base100", base100_encode, base100_decode, r"^(?:base[-_]?100|emoji)$")

