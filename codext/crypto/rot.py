# -*- coding: UTF-8 -*-
"""ROT Codec - rot-with-N-offset content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC, digits as DIG

from ..__common__ import *


__examples1__ = {
    'enc(rot0|rot--10|rot100)': None,
    'enc(rot1|rot-1|caesar_1)': {'this is a test': "uijt jt b uftu"},
    'enc(rot3|caesar-3)':       {'this is a test': "wklv lv d whvw"},
    'enc(rot47)':               {'this is a test': "E9:D :D 2 E6DE"},
}
__examples2__ = {
    'enc(prot0|prot--10|prot100)': None,
    'enc(prot1|prog-caesar_1)':    {'this is a test': "ujlw oz j eqfh"},
    'enc(prot3|pcaesar-3)':        {'this is a test': "wlny qb l gshj"},
}
__guess1__ = ["rot-%d" % i for i in range(1, 26)] + ["rot-47"]
__guess2__ = ["progressive-rot-%d" % i for i in range(1, 26)] + ["progressive-rot-n%d" % i for i in range(1, 26)]


ROT47 = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"


def _rotn(text, n=13, a=(LC, UC, DIG), prog=False, neg=False):
    r = ""
    for i, c in enumerate(ensure_str(text)):
        found = False
        for l in a:
            if c in l:
                r += l[(l.index(c) + n + ([1, -1][neg] * i if prog else 0)) % len(l)]
                found = True
                break
        if not found:
            r += c
    return r


def rot_encode(i):
    def encode(text, errors="strict"):
        t = ensure_str(text)
        r = _rotn(t, 47, [ROT47]) if i == 47 else _rotn(t, i)
        return r, len(r)
    return encode


def rot_decode(i):
    def decode(text, errors="strict"):
        t = ensure_str(text)
        r = _rotn(t, -47, [ROT47]) if i == 47 else _rotn(t, -i)
        return r, len(r)
    return decode


def prot_encode(n, i):
    def encode(text, errors="strict"):
        return _rotn(ensure_str(text), i, prog=True, neg=n == "n"), len(text)
    return encode


def prot_decode(n, i):
    def decode(text, errors="strict"):
        return _rotn(ensure_str(text), -i, prog=True, neg=n != "n"), len(text)
    return decode


add("rot", rot_encode, rot_decode, r"(?:caesar|rot)[-_]?([1-9]|1[0-9]|2[0-5]|47)$", aliases=["caesar"],
    entropy=lambda e: e, printables_rate=lambda pr: pr, examples=__examples1__, guess=__guess1__)
add("progressive-rot", prot_encode, prot_decode, r"p(?:rog(?:ressive)?-)?(?:caesar|rot)[-_]?(n?)([1-9]|1[0-9]|2[0-5])$",
    entropy=lambda e: e, printables_rate=lambda pr: pr, examples=__examples2__, guess=__guess2__)

