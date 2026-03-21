# -*- coding: UTF-8 -*-
"""T9/Multitap Codec - phone keypad multitap content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Multi-tap
"""
from ..__common__ import *


__examples__ = {
    'enc(multitap|multi-tap)': {'this is a test': "8-44-444-7777 / 444-7777 / 2 / 8-33-7777-8"},
}
__guess__ = ["multitap"]


# Standard phone keypad layout
_KEYPAD = {
    '2': "abc",
    '3': "def",
    '4': "ghi",
    '5': "jkl",
    '6': "mno",
    '7': "pqrs",
    '8': "tuv",
    '9': "wxyz",
}

ENCMAP = {}
for _digit, _letters in _KEYPAD.items():
    for _pos, _letter in enumerate(_letters):
        _code = _digit * (_pos + 1)
        ENCMAP[_letter] = _code
        ENCMAP[_letter.upper()] = _code


def multitap_encode(text, errors="strict"):
    t = ensure_str(text)
    words, current = [], []
    for c in t:
        if c == ' ':
            if current:
                words.append("-".join(current))
                current = []
            words.append(None)  # represents a space separator
        elif c not in ENCMAP:
            if errors == "strict":
                raise ValueError("Character %r cannot be encoded with multitap" % c)
            elif errors == "replace":
                current.append("?")
            # else ignore
        else:
            current.append(ENCMAP[c])
    if current:
        words.append("-".join(current))
    parts = []
    for w in words:
        if w is None:
            parts.append("/")
        else:
            parts.append(w)
    r = " ".join(parts)
    return r, len(t)


_DECMAP = {v: k for k, v in ENCMAP.items() if k.islower()}


def multitap_decode(text, errors="strict"):
    t = ensure_str(text)
    r = ""
    for word_token in t.split(" / "):
        if r:
            r += " "
        for token in word_token.split("-"):
            if token == "/":
                r += " "
            elif token in _DECMAP:
                r += _DECMAP[token]
            else:
                if errors == "strict":
                    raise ValueError("Token %r cannot be decoded with multitap" % token)
                elif errors == "replace":
                    r += "?"
                # else ignore
    return r, len(t)


add("multitap", multitap_encode, multitap_decode,
    r"^multi(?:[-_]?tap)?$",
    examples=__examples__, guess=__guess__, expansion_factor=(3., .5), printables_rate=1.)
