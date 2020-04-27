# -*- coding: UTF-8 -*-
"""XOR-N Codec - XOR-with-1-byte content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


def _xorn(text, n=1):
    return "".join(chr(ord(c) ^ (n % 256)) for c in text)


def xor_byte_encode(i):
    def encode(text, errors="strict"):
        r = _xorn(ensure_str(text), i)
        return r, len(r)
    return encode


add("xorN", xor_byte_encode, xor_byte_encode, r"(?i)xor[-_]?([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")
