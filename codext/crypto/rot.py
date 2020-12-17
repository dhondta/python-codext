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
    'enc(rot1|rot-1|caesar_1)': {'this is a test': "uijt jt b uftu"},
    'enc(rot3|caesar-3)':       {'this is a test': "wklv lv d whvw"},
    'enc(rot47)':               {'this is a test': "E9:D :D 2 E6DE"},
}
__guess__ = ["rot%d" % i for i in range(1, 26)] + ["rot47"]


ROT47 = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"


def _rotn(text, n=13, a=LC+UC, l=26):
    n = n % l
    t = maketrans(a, "".join(a[i:i+l][n:] + a[i:i+l][:n] for i in range(0, len(a), l)))
    return text.translate(t)


def rot_encode(i):
    def encode(text, errors="strict"):
        t = ensure_str(text)
        r = _rotn(t, 47, ROT47, 94) if i == 47 else _rotn(t, i)
        return r, len(r)
    return encode


def rot_decode(i):
    def decode(text, errors="strict"):
        t = ensure_str(text)
        r = _rotn(t, -47, ROT47, 94) if i == 47 else _rotn(t, -i)
        return r, len(r)
    return decode


add("rot", rot_encode, rot_decode, r"(?:caesar|rot)[-_]?([1-9]|1[0-9]|2[0-5]|47)$")

