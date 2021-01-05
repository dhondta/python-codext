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


__guess__ = ["atbash"]


def encmap_factory(mask=None):
    mask = mask or "?u?l"
    # [...] enclosure causes the mask to be handled as a whole
    if mask[0] == "[" and mask[-1] == "]":
        alphabet = get_alphabet_from_mask(mask[1:-1])
        return {k: v for k, v in zip(alphabet, alphabet[::-1])}
    # not enclosing the whole mask means that each group is to be considered separately
    else:
        m = {}
        for group in re.findall(r"(\?.|[^?]+)", mask):
            alphabet = get_alphabet_from_mask(group)
            m.update({k: v for k, v in zip(alphabet, alphabet[::-1])})
        return m


add_map("atbash", encmap_factory, no_error=True, pattern=r"atbash(?:[-_]cipher)?(?:[-_](.+))?$")

