# -*- coding: UTF-8 -*-
"""Polybius Square Codec - polybius content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Polybius_square
"""
from ..__common__ import *


__examples__ = {
    'enc(polybius|polybius-square|polybius_square)': {'this is a test': "44 23 24 43 / 24 43 / 11 / 44 15 43 44"},
}
__guess__ = ["polybius"]


# Standard 5x5 Polybius square (I and J share position 24)
_LETTERS = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # 25 letters (I=J)
ENCMAP = {}
for _i, _c in enumerate(_LETTERS):
    _row, _col = divmod(_i, 5)
    _code = "%d%d" % (_row + 1, _col + 1)
    ENCMAP[_c] = _code
    ENCMAP[_c.lower()] = _code
ENCMAP['J'] = ENCMAP['I']
ENCMAP['j'] = ENCMAP['i']
ENCMAP[' '] = "/"


def polybius_encode(text, errors="strict"):
    t = ensure_str(text)
    parts = []
    for c in t:
        if c not in ENCMAP:
            if errors == "strict":
                raise ValueError("Character %r cannot be encoded with polybius" % c)
            elif errors == "replace":
                parts.append("??")
            # else ignore
        else:
            parts.append(ENCMAP[c])
    r = " ".join(parts)
    return r, len(t)


_DECMAP = {}
for _k, _v in ENCMAP.items():
    if (_k.isupper() or _k == ' ') and _v not in _DECMAP:
        _DECMAP[_v] = _k


def polybius_decode(text, errors="strict"):
    t = ensure_str(text)
    r = ""
    for token in t.split(" "):
        if token == "/":
            r += " "
        elif token in _DECMAP:
            r += _DECMAP[token].lower()
        else:
            if errors == "strict":
                raise ValueError("Token %r cannot be decoded with polybius" % token)
            elif errors == "replace":
                r += "?"
            # else ignore
    return r, len(t)


add("polybius", polybius_encode, polybius_decode,
    r"^polybius(?:[-_]square)?$",
    examples=__examples__, guess=__guess__, expansion_factor=(3.2, .4), printables_rate=1.)
