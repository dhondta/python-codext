# -*- coding: UTF-8 -*-
"""Skip Cipher Codec - skip content encoding.

The Skip cipher is a transposition cipher that reads the text by jumping a constant number of characters each time,
 starting from a given position (1 by default) and looping on the text. The skip value must be coprime with the length
 of the text, otherwise some characters would never be read. Every character is transposed, including whitespaces and
 punctuation.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/skip-cipher
"""
from math import gcd

from ..__common__ import *


__examples__ = {
    'enc(skip|skip-cipher|skip-0)': None,
    'dec(skip)':                    None,
    'enc(skip-3|skip_cipher-3|skip-3-1)': {'DCODE': "DDCEO", 'SKIP': "SPIK"},
    'enc(skip-3-2)':                {'DCODE': "CEODD"},
    'enc(skip-2)':                  {'SKIP': None},
    'dec(skip-3)':                  {'DDCEO': "DCODE"},
    'dec(skip-2)':                  {'SISI': None},
    'enc-dec(skip-1|skip-3|skip-9-5|skip-11-100)': ["", "a", "DCODE", "Hello, World!", "Attack at dawn"],
}
__guess__ = []


def __skip(decode=False):
    def _wrapper(skip=None, start=None):
        def _code(text, errors="strict"):
            # a missing skip value is only reported when coding, as the lookup of the bare codec name must succeed (e.g.
            #  when listing the encodings)
            # values starting with "0" are given as strings by the codec name pattern
            if (k := int(skip or 0)) <= 0:
                raise LookupError("Bad parameter for encoding 'skip': skip value must be a positive integer")
            text, n = ensure_str(text), len(ensure_str(text))
            # the skip value must be coprime with the length of the text, otherwise some characters are never read
            if n > 0 and gcd(k, n) != 1:
                return (r := handle_error("skip", errors, decode=decode, kind="text")(text, 0)), len(r)
            positions = [(int(start or 1) - 1 + i * k) % n for i in range(n)]
            if decode:
                r = [""] * n
                for c, p in zip(text, positions):
                    r[p] = c
            else:
                r = [text[p] for p in positions]
            return (s := "".join(r)), len(s)
        return _code
    return _wrapper


add("skip", __skip(), __skip(True), r"^skip(?:[-_]cipher)?(?:[-_](\d+))?(?:[-_](\d+))?$", penalty=.1)
