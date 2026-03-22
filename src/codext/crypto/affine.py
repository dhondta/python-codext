# -*- coding: UTF-8 -*-
"""Affine Cipher Codec - affine content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://crypto.interactive-maths.com/affine-cipher.html
"""
from ..__common__ import *


__guess__ = []


def encmap_factory(mask=None):
    mask = mask or "?l?u?s-1,2"
    mask, key = mask.split("-")
    a, b = map(int, key.split(","))
    alphabet = get_alphabet_from_mask(mask)
    encmap = {c: alphabet[(a * alphabet.index(c) + b) % len(alphabet)] for c in alphabet}
    if len(set(encmap.keys())) != len(set(encmap.values())):
        raise LookupError("Bad parameter for encoding 'affine': {}, {}".format(a, b))
    if ' ' not in encmap.keys():
        encmap[' '] = " "
    return encmap


add_map("affine", encmap_factory, pattern=r"^affine(?:[-_]cipher)?(?:[-_](.+?\-\d+\,\d+))?$")

