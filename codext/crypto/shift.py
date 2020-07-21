# -*- coding: UTF-8 -*-
"""Shift Codec - Shift-ordinal-with-N content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(shift0|shift--10|shift256)': None,
    'enc(shift1|shift_1|shift-1)':    {'this is a test': "uijt!jt!b!uftu"},
    'enc(shift9|shift_9|shift-9)':    {'this is a test': "}qr|)r|)j)}n|}"},
}


def ord_shift_decode(i):
    return ord_shift_encode(-i)


def ord_shift_encode(i):
    def encode(text, errors="strict"):
        r = "".join(chr((ord(c) + i) % 256) for c in text)
        return r, len(r)
    return encode


add("shift", ord_shift_encode, ord_shift_decode, r"shift[-_]?([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")

