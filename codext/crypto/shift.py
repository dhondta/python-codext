# -*- coding: UTF-8 -*-
"""Shift-N Codec - Shift-ordinal-with-N content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


def ord_shift_decode(i):
    return ord_shift_encode(-i)


def ord_shift_encode(i):
    def encode(text, errors="strict"):
        r = "".join(chr((ord(c) + i) % 256) for c in text)
        return r, len(r)
    return encode


add("shiftN", ord_shift_encode, ord_shift_decode,
    r"(?i)(?:ord(?:inal)?[-_]?)?shift[-_]?([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")
