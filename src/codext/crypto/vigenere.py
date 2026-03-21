# -*- coding: UTF-8 -*-
"""Vigenère Cipher Codec - vigenere content encoding.

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
    'enc(vigenere-lemon|vigenere_lemon)': {'attack at dawn': "lxfopv ef rnhr"},
    'enc(vigenere-key)':                  {'this is a test': "dlgc mq k xccx"},
}
__guess__ = []


def vigenere_encode(key):
    def encode(text, errors="strict"):
        t, r, ki = ensure_str(text), "", 0
        k = key.lower()
        for c in t:
            if c in LC:
                r += LC[(LC.index(c) + ord(k[ki % len(k)]) - ord('a')) % 26]
                ki += 1
            elif c in UC:
                r += UC[(UC.index(c) + ord(k[ki % len(k)]) - ord('a')) % 26]
                ki += 1
            else:
                r += c
        return r, len(t)
    return encode


def vigenere_decode(key):
    def decode(text, errors="strict"):
        t, r, ki = ensure_str(text), "", 0
        k = key.lower()
        for c in t:
            if c in LC:
                r += LC[(LC.index(c) - ord(k[ki % len(k)]) + ord('a')) % 26]
                ki += 1
            elif c in UC:
                r += UC[(UC.index(c) - ord(k[ki % len(k)]) + ord('a')) % 26]
                ki += 1
            else:
                r += c
        return r, len(t)
    return decode


add("vigenere", vigenere_encode, vigenere_decode, r"^(?:vigenere|vigen[eè]re)[-_]([a-zA-Z]+)$",
    penalty=.2, entropy=lambda e: e, printables_rate=lambda pr: pr, transitive=True,
    examples=__examples__, guess=__guess__)
