# -*- coding: UTF-8 -*-
"""Polybius Square Codec - polybius-square content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(polybius|polybius-square|polybius_square)': {'this is a test': "44232443 2443 11 44154344"},
    'enc(polybius-ABCDEFGHIKLMNOPQRSTUVWXYZ)':       {'this is a test': "44232443 2443 11 44154344"},
    'dec(polybius)':                                 {'44232443 2443 11 44154344': "THIS IS A TEST"},
}
__guess__ = ["polybius"]


# Standard 5×5 Polybius square (I and J share the same cell):
#      1  2  3  4  5
# 1    A  B  C  D  E
# 2    F  G  H  I  K
# 3    L  M  N  O  P
# 4    Q  R  S  T  U
# 5    V  W  X  Y  Z
_DEFAULT_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def __make_maps(alphabet):
    """ Build the encoding and decoding maps for the given 25-character alphabet. """
    alph = alphabet.upper() if alphabet else _DEFAULT_ALPHABET
    if len(alph) != 25 or len(set(alph)) != 25:
        raise LookupError("Polybius square requires exactly 25 distinct characters; "
                          f"got {len(alph)} character(s) with {len(set(alph))} unique: {alph}")
    encmap = {alph[i]: str(i // 5 + 1) + str(i % 5 + 1) for i in range(25)}
    decmap = {v: k for k, v in encmap.items()}
    if 'J' not in encmap and 'I' in encmap:
        encmap['J'] = encmap['I']
    encmap[' '] = ' '
    return encmap, decmap


def polybius_encode(alphabet=_DEFAULT_ALPHABET):
    encmap, _ = __make_maps(alphabet)
    def encode(text, errors="strict"):
        _h = handle_error("polybius", errors)
        r = ""
        for pos, c in enumerate(ensure_str(text).upper()):
            r += encmap[c] if c in encmap else _h(c, pos, r)
        return r, len(text)
    return encode


def polybius_decode(alphabet=_DEFAULT_ALPHABET):
    _, decmap = __make_maps(alphabet)
    def decode(text, errors="strict"):
        _h = handle_error("polybius", errors, decode=True)
        r, t, i = "", ensure_str(text), 0
        while i < len(t):
            if t[i] == " ":
                r += " "
                i += 1
            elif i + 1 < len(t):
                r += decmap.get(t[i:i+2]) or _h(t[i:i+2], i, r)
                i += 2
            else:
                r += _h(t[i], i, r)
                i += 1
        return r, len(t)
    return decode


add("polybius", polybius_encode, polybius_decode, r"^polybius(?:[-_]square)?(?:[-_]([A-Za-z]{25}))?$",
    printables_rate=1., expansion_factor=(1.7, .3))

