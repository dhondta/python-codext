# -*- coding: UTF-8 -*-
"""Polybius Square Codec - polybius-square content encoding.

The Polybius square is a method for fractionating plaintext characters so that
they can be represented by a smaller set of symbols. Each letter is represented
by its coordinates (row, column) in the 5×5 grid.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Polybius_square
"""
from ..__common__ import *


__examples__ = {
    'enc(polybius|polybius-square|polybius_square)': {
        'this is a test': "44232443 2443 11 44154344",
        'jack':           "24111325",
    },
    'enc(polybius-ABCDEFGHIKLMNOPQRSTUVWXYZ)': {
        'this is a test': "44232443 2443 11 44154344",
    },
    'dec(polybius)': {
        '44232443 2443 11 44154344': "THIS IS A TEST",
    },
}
__guess__ = ["polybius-square"]


# Standard 5×5 Polybius square (I and J share the same cell):
#      1  2  3  4  5
# 1    A  B  C  D  E
# 2    F  G  H  I  K
# 3    L  M  N  O  P
# 4    Q  R  S  T  U
# 5    V  W  X  Y  Z
_DEFAULT_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def _make_maps(alphabet):
    """ Build the encoding and decoding maps for the given 25-character alphabet. """
    alph = alphabet.upper() if alphabet else _DEFAULT_ALPHABET
    if len(alph) != 25 or len(set(alph)) != 25:
        raise LookupError(
            "Polybius square requires exactly 25 distinct characters; "
            "got {} character(s) with {} unique: {}".format(len(alph), len(set(alph)), alph)
        )
    encmap = {alph[i]: str(i // 5 + 1) + str(i % 5 + 1) for i in range(25)}
    decmap = {v: k for k, v in encmap.items()}
    if 'J' not in encmap and 'I' in encmap:
        encmap['J'] = encmap['I']
    encmap[' '] = ' '
    return encmap, decmap


def polybius_encode(alphabet=""):
    encmap, _ = _make_maps(alphabet)

    def encode(text, errors="strict"):
        _handle_error = handle_error("polybius-square", errors)
        r = ""
        for pos, c in enumerate(ensure_str(text).upper()):
            if c in encmap:
                r += encmap[c]
            else:
                r += _handle_error(c, pos, r)
        return r, len(text)
    return encode


def polybius_decode(alphabet=""):
    _, decmap = _make_maps(alphabet)

    def decode(text, errors="strict"):
        _handle_error = handle_error("polybius-square", errors, decode=True)
        r, t, i = "", ensure_str(text), 0
        while i < len(t):
            if t[i] == ' ':
                r += ' '
                i += 1
            elif i + 1 < len(t) and t[i:i+2] in decmap:
                r += decmap[t[i:i+2]]
                i += 2
            elif t[i].isdigit() and i + 1 < len(t):
                r += _handle_error(t[i:i+2], i, r)
                i += 2
            else:
                r += _handle_error(t[i], i, r)
                i += 1
        return r, len(t)
    return decode


add("polybius-square", polybius_encode, polybius_decode,
    r"^polybius(?:[-_]square)?(?:[-_]([A-Za-z]{25}))?$",
    printables_rate=1., expansion_factor=(1.85, .15))
