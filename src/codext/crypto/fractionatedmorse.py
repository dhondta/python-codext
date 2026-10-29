# -*- coding: UTF-8 -*-
"""Fractionated Morse Cipher Codec - fractionated Morse content encoding.

The Fractionated Morse cipher, described by M. E. Ohaver in 1937, first converts the text to Morse code, separating the
 characters by "x" and the words by "xx", with a trailing "xx" to mark the end of the message. This Morse string is
 then split into groups of three symbols (the last one being padded with dots), and each group is replaced by a letter
 of an alphabet ordered with an optional keyword (without duplicates, then followed by the remaining letters). As the
 group "xxx" never occurs, the 26 letters are enough. Case and whitespace are not kept.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/fractionated-morse
           https://www.cryptogram.org/downloads/aca.info/ciphers/FractionatedMorse.pdf
"""
from itertools import product
from string import ascii_uppercase as UC

from ..__common__ import *
from ..languages.morse import ENCMAP


__examples__ = {
    'enc(fractionated-morse|fractionated_morse|fmorse)': {'DCODE MORSE': "JVLNVGZQODSGY",
                                                          'dcode  morse ': "JVLNVGZQODSGY"},
    'enc(fractionated-morse-roundtable|fmorse_roundtable)': {'this is a test': "JRPPLURYMJPBY"},
    'enc(fractionated-morse)': {'this is a #': None},
    'dec(fractionated-morse)': {'JVLNVGZQODSGY': "dcode morse", 'jvlnvgzqodsgy': "dcode morse", 'J1': None},
    'enc-dec(fractionated-morse|fractionated-morse-keyword|fmorse-roundtable)': ["", "this is a test",
                                                                                 "hello, world! 1234"],
}
__guess__ = ["fractionated-morse"]


_MORSE = {k: v for k, v in ENCMAP.items() if k != " "}
_CHARS = {v: k for k, v in _MORSE.items()}
# the 26 groups of three symbols, ordered with "." < "-" < "x" ("xxx" excluded)
_GROUPS = ["".join(g) for g in product(".-x", repeat=3)][:-1]


def __alphabet(key):
    a = []
    for c in str(key or "").upper() + UC:
        if c in UC and c not in a:
            a.append(c)
    return a


def fmorse_encode(key=None):
    letters = dict(zip(_GROUPS, __alphabet(key)))
    def encode(text, errors="strict"):
        _h, m = handle_error("fractionated-morse", errors), ""
        for word in ensure_str(text).lower().split():
            for i, c in enumerate(word):
                if c in _MORSE:
                    m += _MORSE[c] + "x"
                else:
                    _h(c, i)
            m += "x" if m else ""
        m += "." * (-len(m) % 3)
        r = "".join(letters[m[i:i+3]] for i in range(0, len(m), 3))
        return r, len(text)
    return encode


def fmorse_decode(key=None):
    groups = dict(zip(__alphabet(key), _GROUPS))
    def decode(text, errors="strict"):
        _h, m = handle_error("fractionated-morse", errors, decode=True), ""
        for i, c in enumerate(ensure_str(text).upper()):
            if c in groups:
                m += groups[c]
            else:
                _h(c, i)
        # the message ends with "xx", possibly followed by padding dots
        m = m[:m.rfind("xx")] if "xx" in m[-4:] else m.rstrip("x")
        _h, r = handle_error("fractionated-morse", errors, decode=True, kind="Morse code"), []
        for word in m.split("xx") if m else []:
            w = ""
            for i, g in enumerate(word.split("x")):
                w += _CHARS[g] if g in _CHARS else _h(g, i)
            r.append(w)
        return " ".join(r), len(text)
    return decode


add("fractionated-morse", fmorse_encode, fmorse_decode, r"^f(?:ractionated)?[-_]?morse(?:[-_]([a-zA-Z]+))?$",
    printables_rate=1., expansion_factor=(1.2, .3), penalty=.1)
