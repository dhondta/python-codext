# -*- coding: UTF-8 -*-
"""Trithemius Cipher Codec - trithemius content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(trithemius|trithemius-cipher)': {'this is a test': "tikv mx g ambd"},
    'enc(trithemius)':                   {'': "", 'HELLO': "HFNOS", '12345!@#$': "12345!@#$"},
    'enc-dec(trithemius)':               ["Hello, World!", "@random"],
}
__guess__ = ["trithemius"]


def _trithemius(text, decode=False):
    r, pos = "", 0
    for c in ensure_str(text):
        if c in LC or c in UC:
            r += (a := LC if c in LC else UC)[(a.index(c) + [1, -1][decode] * pos) % 26]
            pos += 1
        else:
            r += c
    return r


def trithemius_encode(text, errors="strict"):
    r = _trithemius(ensure_str(text))
    return r, len(r)


def trithemius_decode(text, errors="strict"):
    r = _trithemius(ensure_str(text), True)
    return r, len(r)


add("trithemius", trithemius_encode, trithemius_decode, r"trithemius(?:[-_]cipher)?$", printables_rate=lambda pr: pr,
    entropy=lambda e: e)
