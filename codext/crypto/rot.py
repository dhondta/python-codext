# -*- coding: UTF-8 -*-
"""ROT Codec - rot-with-N-offset content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(rot0|rot--10|rot100)': None,
    'enc(rot1|rot-1|rot_1)':    {'this is a test': "uijt jt b uftu"},
    'enc(rot3)':                {'this is a test': "wklv lv d whvw"},
}


def _rotn(text, n=13):
    n = n % 26
    t = maketrans(LC + UC, LC[n:] + LC[:n] + UC[n:] + UC[:n])
    return text.translate(t)


def rot_encode(i):
    def encode(text, errors="strict"):
        r = _rotn(ensure_str(text), i)
        return r, len(r)
    return encode


def rot_decode(i):
    def decode(text, errors="strict"):
        r = _rotn(ensure_str(text), -i)
        return r, len(r)
    return decode


add("rot", rot_encode, rot_decode, r"rot[-_]?([1-9]|1[0-9]|2[0-5])$")

