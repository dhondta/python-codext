# -*- coding: UTF-8 -*-
"""XOR Codec - XOR-with-1-byte content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(xor0|xor--10|xor256|xor300)': None,
    'enc(xor3|xor-3|xor_3)':           {'this is a test': "wkjp#jp#b#wfpw"},
    'enc(xor3|xor-3|xor_3)':           {'wkjp#jp#b#wfpw': "this is a test"},
    'enc(xor6|xor-6|xor_6)':           {'this is a test': "rnou&ou&g&rcur"},
}


def _xorn(text, n=1):
    return "".join(chr(ord(c) ^ (n % 256)) for c in text)


def xor_byte_encode(i):
    def encode(text, errors="strict"):
        r = _xorn(ensure_str(text), i)
        return r, len(r)
    return encode


add("xor", xor_byte_encode, xor_byte_encode, r"^xor[-_]?([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")

