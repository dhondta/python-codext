# -*- coding: UTF-8 -*-
"""Dvorak Codec - QWERTY to Dvorak keyboard layout content encoding.

The Dvorak Simplified Keyboard, patented by August Dvorak and William Dealey in 1936, rearranges the letters and some
 punctuation of the standard QWERTY layout (US) so that the most frequent letters are on the home row. Encoding replaces
 each character by the one of the same key with the Dvorak layout (as when typing with the QWERTY layout on a computer
 set to Dvorak), while decoding does the opposite (as when typing with the Dvorak layout on a computer set to QWERTY).
 This permutation of 35 keys (letters and the "-", "=", "[", "]", ";", "'", ",", "." and "/" keys, with their shifted
 characters) is made of cycles of 15, 14, 2, 2, 1 and 1 keys, hence it gets back to the text after 210 encodings.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.montefischer.com/2021/03/21/dvorak-group-action.html
"""
from ..__common__ import *


__examples__ = {
    'enc(dvorak|qwerty-dvorak|qwerty_to_dvorak)': {'Hello, World!': "D.nnrw <rpne!", 'dvorak': "ekrpat"},
    'dec(dvorak)': {'D.nnrw <rpne!': "Hello, World!", 'Cbol.jyrp Mai': "Inspector Mag"},
    'enc-dec(dvorak)': ["@random{256}", "The quick brown fox jumps over the lazy dog: \"-=[];',./_+{}:<>?\""],
}
__guess__ = ["dvorak"]


# characters of the keys of the QWERTY layout and of the Dvorak layout, unshifted then shifted (US)
QWERTY = "-=qwertyuiop[]asdfghjkl;'zxcvbnm,./" "_+QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
DVORAK = "[]',.pyfgcrl/=aoeuidhtns-;qjkxbmwvz" "{}\"<>PYFGCRL?+AOEUIDHTNS_:QJKXBMWVZ"
_ENCODE, _DECODE = str.maketrans(QWERTY, DVORAK), str.maketrans(DVORAK, QWERTY)


def dvorak_encode(text, errors="strict"):
    return ensure_str(text).translate(_ENCODE), len(text)


def dvorak_decode(text, errors="strict"):
    return ensure_str(text).translate(_DECODE), len(text)


add("dvorak", dvorak_encode, dvorak_decode, r"^(?:qwerty[-_](?:to[-_])?)?dvorak$", examples=__examples__,
    guess=__guess__, entropy=lambda e: e, printables_rate=lambda pr: pr, transitive=True)
