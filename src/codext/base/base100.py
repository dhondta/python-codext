# -*- coding: UTF-8 -*-
"""Base100 Codec - base100 content encoding.

Base100, also known as the emoji encoding, was created by Adam Niederer. Each byte is written with one of 256 emojis,
 from U+1F3F7 to U+1F4F6, whose UTF-8 encoding is the 4 bytes F0 9F followed by two bytes computed from the byte value
 (hence a fixed expansion factor of 4 in bytes, but of 1 in characters). This implementation is strongly inspired by
 pybase100.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/AdamNiederer/base100
           https://github.com/MasterGroosha/pybase100
"""
from ._base import main
from ..__common__ import *

# no __examples__ ; handled manually in tests/test_base.py

class Base100DecodeError(ValueError):
    __module__ = "builtins"


def base100_encode(input, errors="strict"):
    input = b(input)
    r = [240, 159, 0, 0] * len(input)
    for i, c in enumerate(input):
        r[4*i+2] = (c + 55) // 64 + 143
        r[4*i+3] = (c + 55) % 64 + 128
    return bytes(r), len(input)


def base100_decode(input, errors="strict"):
    input = b(_stripl(input, True, True))
    if errors == "ignore":
        input = input.replace(b"\n", b"")
    if len(input) % 4 != 0:
        raise Base100DecodeError("Bad input (length should be multiple of 4)")
    r = [None] * (len(input) // 4)
    for i, c in enumerate(input):
        if i % 4 == 2:
            tmp = ((c - 143) * 64) % 256
        elif i % 4 == 3:
            r[i//4] = (c - 128 + tmp - 55) & 0xff
    return bytes(r), len(input)
    
    
add("base100", base100_encode, base100_decode, r"^(?:base[-_]?100|emoji)$", expansion_factor=1.)
main100 = main(100, "<https://github.com/AdamNiederer/base100>")

