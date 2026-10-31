# -*- coding: UTF-8 -*-
"""Vernam Cipher Codec - vernam content encoding.

The Vernam cipher, patented by Gilbert Vernam in 1919, XORs each character of the text with the corresponding character
 of a repeated key ; with a random key as long as the text, used only once, it becomes the one-time pad. As XOR is its
 own inverse, decoding is the same as encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Gilbert_Vernam
"""
from ..__common__ import *


__examples__ = {
    'enc(vernam|vernam-cipher)': None,
    'enc(vernam-key)':           {'this is a test': "\x1f\r\x10\x18E\x10\x18E\x18K\x11\x1c\x18\x11"},
    'enc(vernam_cipher-Key)':    {'this is a test': "?\r\x108E\x108E\x18k\x11\x1c8\x11"},
    'dec(vernam-key)':           {"\x1f\r\x10\x18E\x10\x18E\x18K\x11\x1c\x18\x11": 'this is a test'},
    'enc-dec(vernam-secret|vernam-a b!)': ["", "this is a test", "@random{256}", "Caf\xe9 €"],
}
__guess__ = ["vernam-key", "vernam-password", "vernam-secret"]


def vernam(key=None):
    def code(text, errors="strict"):
        if not key:
            raise LookupError("Bad parameter for encoding 'vernam': key must be a non-empty string")
        r = "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(ensure_str(text)))
        return r, len(r)
    return code


add("vernam", vernam, vernam, r"^vernam(?:[-_]cipher)?(?:[-_](.+))?$", examples=__examples__, guess=__guess__,
    transitive=True, penalty=.1)
