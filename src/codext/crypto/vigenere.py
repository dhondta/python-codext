# -*- coding: UTF-8 -*-
"""Vigenere Cipher Codec - vigenere content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(vigenere)':             None,
    'enc(vigenere-lemon)':       {'ATTACKATDAWN': 'LXFOPVEFRNHR'},
    'enc(vigenere-key)':         {'hello': 'rijvs'},
    'enc(vigenère_key)':         {'Hello World': 'Rijvs Uyvjn'},
    'enc-dec(vigenere-secret)':  ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__guess__ = ["vigenere-key", "vigenere-secret", "vigenere-password"]


__char = lambda c, k, i, d=False: (LC if (b := c in LC) else UC)[(ord(c) - ord("Aa"[b]) + \
                                                                  [1, -1][d] * (ord(k[i % len(k)]) - ord('a'))) % 26]


def __check(key):
    key = key.lower()
    if not key or not key.isalpha():
        raise LookupError("Bad parameter for encoding 'vigenere': key must be a non-empty alphabetic string")
    return key


def vigenere_encode(key):
    def encode(text, errors="strict"):
        result, i, k = [], 0, __check(key)
        for c in ensure_str(text):
            if c in LC or c in UC:
                result.append(__char(c, k, i))
                i += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)
    return encode


def vigenere_decode(key):
    def decode(text, errors="strict"):
        result, i, k = [], 0, __check(key)
        for c in ensure_str(text):
            if c in LC or c in UC:
                result.append(__char(c, k, i, True))
                i += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)
    return decode


add("vigenere", vigenere_encode, vigenere_decode, r"vigen[eè]re(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)

