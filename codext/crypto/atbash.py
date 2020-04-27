# -*- coding: UTF-8 -*-
"""Atbash Cipher Codec - atbash content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://crypto.interactive-maths.com/atbash-cipher.html
"""
from ..__common__ import *


def encmap_factory(mask=None):
    mask = mask or "lus"
    alphabet = ""
    for m in mask:
        try:
            for c in MASKS[m]:
                if c not in alphabet:
                    alphabet += c
        except KeyError:
            raise LookupError("Bad parameter for encoding 'atbash': '{}'".format(mask))
    return {k: v for k, v in zip(alphabet, alphabet[::-1])}


add_map("atbash", encmap_factory, pattern=r"atbash(?:[-_]cipher)?(?:[-_]([" + r"".join(MASKS.keys()) + r"]+))?$")
