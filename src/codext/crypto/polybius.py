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
_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
ENCMAP = {_ALPHABET[i]: str(i // 5 + 1) + str(i % 5 + 1) for i in range(25)}
ENCMAP['J'] = ENCMAP['I']
ENCMAP[' '] = ' '


add_map("polybius-square", ENCMAP, ignore_case="both",
        pattern=r"^(?:polybius(?:[-_]square)?)$", printables_rate=1.,
        expansion_factor=(1.85, .15))
