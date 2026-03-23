# -*- coding: UTF-8 -*-
"""Autoclave Cipher Codec - autoclave content encoding.

The Autoclave (Autokey) cipher is a variant of the Vigenere cipher where the key
is extended by appending the plaintext to the initial key (key+plaintext), making
the key stream as long as the message itself.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/autoclave-cipher
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(autoclave)':             None,
    'enc(autoclave-queenly)':     {'ATTACKATDAWN': 'QNXEPVYTWTWP'},
    'enc-dec(autoclave-key)':     ['hello world', 'ATTACK AT DAWN', 'Test 1234!', 'Mixed Case 123'],
}
__guess__ = ["autoclave-key", "autoclave-secret", "autoclave-password"]


def __check(key):
    key = key.lower()
    if not key or not key.isalpha():
        raise LookupError("Bad parameter for encoding 'autoclave': key must be a non-empty alphabetic string")
    return key


def autoclave_encode(key):
    def encode(text, errors="strict"):
        k = __check(key)
        text_str = ensure_str(text)
        alpha_chars = [c.lower() for c in text_str if c in LC or c in UC]
        key_stream = k + "".join(alpha_chars)
        result = []
        ki = 0
        for c in text_str:
            if c in LC:
                result.append(LC[(ord(c) - ord('a') + ord(key_stream[ki]) - ord('a')) % 26])
                ki += 1
            elif c in UC:
                result.append(UC[(ord(c) - ord('A') + ord(key_stream[ki]) - ord('a')) % 26])
                ki += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)
    return encode


def autoclave_decode(key):
    def decode(text, errors="strict"):
        k = __check(key)
        text_str = ensure_str(text)
        result = []
        key_stream = list(k)
        ki = 0
        for c in text_str:
            if c in LC:
                dec_c = LC[(ord(c) - ord('a') - (ord(key_stream[ki]) - ord('a'))) % 26]
                result.append(dec_c)
                key_stream.append(dec_c)
                ki += 1
            elif c in UC:
                dec_c = UC[(ord(c) - ord('A') - (ord(key_stream[ki]) - ord('a'))) % 26]
                result.append(dec_c)
                key_stream.append(dec_c.lower())
                ki += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)
    return decode


add("autoclave", autoclave_encode, autoclave_decode,
    r"auto(?:clave|key)(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)
