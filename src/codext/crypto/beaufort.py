# -*- coding: UTF-8 -*-
"""Beaufort Cipher Codec - beaufort content encoding.

The Beaufort cipher is a polyalphabetic substitution cipher similar to the
Vigenère cipher, but based on a different operation: instead of adding the key
to the plaintext, the plaintext is subtracted from the key (C = K - P mod 26).
This makes the cipher self-reciprocal: the same operation is used for both
encoding and decoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/beaufort-cipher
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(beaufort)':              None,
    'enc(beaufort-lemon)':        {'ATTACKATDAWN': 'LLTOLBETLNPR'},
    'enc(beaufort-key)':          {'hello': 'danzq'},
    'enc(beaufort_key)':          {'Hello World': 'Danzq Cwnnh'},
    'enc-dec(beaufort-secret)':   ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__guess__ = ["beaufort-key", "beaufort-secret", "beaufort-password"]


__char = lambda c, k, i: (LC if (b := c in LC) else UC)[(ord(k[i % len(k)]) - ord('a') - \
                                                          (ord(c) - ord("Aa"[b]))) % 26]


def __check(key):
    key = key.lower()
    if not key or not key.isalpha():
        raise LookupError("Bad parameter for encoding 'beaufort': key must be a non-empty alphabetic string")
    return key


def beaufort_encode(key):
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


# Beaufort is self-reciprocal: decoding uses the same operation as encoding
beaufort_decode = beaufort_encode


add("beaufort", beaufort_encode, beaufort_decode, r"beaufort(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)
