# -*- coding: UTF-8 -*-
"""Vigenère Cipher Codec - vigenere content encoding.

Method of encrypting alphabetic text by using a series of interwoven Caesar
ciphers based on the letters of a keyword. Though the 'chiffre indéchiffrable'
is easy to understand and implement, for three centuries it resisted all
attempts to break it.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(vigenere-lemon)':       {'ATTACKATDAWN': 'LXFOPVEFRNHR'},
    'enc(vigenere-key)':         {'hello': 'rijvs'},
    'enc(vigenere_key)':         {'Hello World': 'Rijvs Uyvjn'},
    'enc-dec(vigenere-secret)':  ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__guess__ = ["vigenere-key", "vigenere-secret", "vigenere-password"]


def vigenere_encode(key):
    key = key.lower()
    if not key or not key.isalpha():
        raise LookupError("Bad parameter for encoding 'vigenere': key must be a non-empty alphabetic string")

    def encode(text, errors="strict"):
        text = ensure_str(text)
        result = []
        ki = 0
        for c in text:
            if c in LC:
                shift = ord(key[ki % len(key)]) - ord('a')
                result.append(LC[(ord(c) - ord('a') + shift) % 26])
                ki += 1
            elif c in UC:
                shift = ord(key[ki % len(key)]) - ord('a')
                result.append(UC[(ord(c) - ord('A') + shift) % 26])
                ki += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)

    return encode


def vigenere_decode(key):
    key = key.lower()
    if not key or not key.isalpha():
        raise LookupError("Bad parameter for encoding 'vigenere': key must be a non-empty alphabetic string")

    def decode(text, errors="strict"):
        text = ensure_str(text)
        result = []
        ki = 0
        for c in text:
            if c in LC:
                shift = ord(key[ki % len(key)]) - ord('a')
                result.append(LC[(ord(c) - ord('a') - shift) % 26])
                ki += 1
            elif c in UC:
                shift = ord(key[ki % len(key)]) - ord('a')
                result.append(UC[(ord(c) - ord('A') - shift) % 26])
                ki += 1
            else:
                result.append(c)
        r = "".join(result)
        return r, len(r)

    return decode


add("vigenere", vigenere_encode, vigenere_decode,
    r"vigen[eè]re[-_](?:cipher[-_])?([a-zA-Z]+)$",
    penalty=.2, entropy=lambda e: e, printables_rate=lambda pr: pr,
    transitive=True, examples=__examples__, guess=__guess__)
