# -*- coding: UTF-8 -*-
"""Trithemius Cipher Codec - trithemius content encoding.

The Trithemius cipher is a polyalphabetic encryption method invented by the German
abbot Johannes Trithemius. It applies a sequence of progressive Caesar shifts (0, 1,
2, ...) to each successive letter in the plaintext, leaving non-alphabetic characters
unchanged. It is equivalent to a Vigenère cipher with the key "ABCDEFGHIJKLMNOPQRSTUVWXYZ...".

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/trithemius-cipher
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(trithemius|trithemius-cipher)': {'this is a test': "tikv mx g ambd"},
    'enc(trithemius)': {
        '':          "",
        'HELLO':     "HFNOS",
        '12345!@#$': "12345!@#$",
    },
    'enc-dec(trithemius)': ["Hello, World!", "@random"],
}
__guess__ = ["trithemius"]


def _trithemius(text, decode=False):
    r, pos = "", 0
    for c in ensure_str(text):
        if c in LC:
            r += LC[(LC.index(c) + (-pos if decode else pos)) % 26]
            pos += 1
        elif c in UC:
            r += UC[(UC.index(c) + (-pos if decode else pos)) % 26]
            pos += 1
        else:
            r += c
    return r


def trithemius_encode(text, errors="strict"):
    r = _trithemius(ensure_str(text))
    return r, len(text)


def trithemius_decode(text, errors="strict"):
    r = _trithemius(ensure_str(text), decode=True)
    return r, len(text)


add("trithemius", trithemius_encode, trithemius_decode,
    r"trithemius(?:[-_]cipher)?$",
    entropy=lambda e: e, printables_rate=lambda pr: pr, transitive=True)
