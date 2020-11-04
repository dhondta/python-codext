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


__guess__ = []


def encmap_factory(mask=None):
    alphabet = get_alphabet_from_mask(mask or "?l?u?s")
    return {k: v for k, v in zip(alphabet, alphabet[::-1])}


add_map("atbash", encmap_factory, pattern=r"atbash(?:[-_]cipher)?(?:[-_](.+))?$")

