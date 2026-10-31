# -*- coding: UTF-8 -*-
"""Affine Cipher Codec - affine content encoding.

The affine cipher is a monoalphabetic substitution cipher where each character of index x in the alphabet is replaced by
 the character of index (a * x + b) mod m, m being the length of the alphabet ; a must be coprime with m for the
 substitution to be reversible (with a = 1, this is a Caesar cipher). The alphabet is given as a mask (e.g. "?l?u?s" for
 lowercase letters, uppercase letters and symbols) followed by the key "a,b" (e.g. "affine-?l?u-5,8").

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

