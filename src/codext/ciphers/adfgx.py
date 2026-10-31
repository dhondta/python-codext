# -*- coding: UTF-8 -*-
"""ADFGX/ADFGVX Cipher Codec - adfgx/adfgvx content encoding.

The ADFGX and ADFGVX ciphers were used by the German Army during World War I. Each letter is first replaced by the
 labels of its row and column in a Polybius square (5x5 with ADFGX, I and J sharing a cell ; 6x6 with ADFGVX, letters
 and digits), then the result is written in rows under a transposition keyword and read column by column, in the
 alphabetical order of the keyword letters. The square is filled with an optional keyword (without duplicates), then
 with the remaining characters of the alphabet.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/ADFGVX_cipher
"""
from string import ascii_uppercase as UC, digits as DG

from ..__common__ import *


__examples1__ = {
    'enc(adfgx)':                         None,
    'enc(adfgx-cargo)':                   {'TEST': "GGGFXGAG"},
    'enc(adfgx-btalpdhozkqfvsngicuxmrewy-cargo)': {'Attack at once': "FAXDFADDDGDGFFFAFAXAFAFX"},
    'dec(adfgx-btalpdhozkqfvsngicuxmrewy-cargo)': {'FAXDF ADDDG DGFFF AFAX AFAFX': "ATTACKATONCE"},
    'enc(adfgx-1234-cargo)':              None,
    'enc(adfgx-cargo_)':                  None,
    'enc(adfgx-key-cargo)':               {'TEST!': None},
    'dec(adfgx-key-cargo)':               {'ADFGV': None, 'ADF': None},
    'enc-dec(adfgx-cipher-key-cargo)':    ["TEST", "ATTACKATDAWN", "THEQUICKBROWNFOX"],
}
__examples2__ = {
    'enc(adfgvx)':                        None,
    'enc(adfgvx-na1c3h8tb2ome5wrpd4f6g7i9j0klqsuvxyz-privacy)': {'attack at 1200am': "DGDDDAGDDGAFADDFDADVDVFAADVX"},
    'dec(adfgvx-na1c3h8tb2ome5wrpd4f6g7i9j0klqsuvxyz-privacy)': {'DGDD DAGD DGAF ADDF DADV DVFA ADVX':
                                                                 "ATTACKAT1200AM"},
    'enc-dec(adfgvx-privacy)':            ["TEST", "ATTACKAT1200AM", "JUMP42"],
    'enc-dec(adfgvx_cipher-nachtbommenwerper-privacy)': ["ATTACKAT1200AM"],
    'enc-dec(adfgvx-2026-1918)':          ["ATTACKAT1200AM"],
}
__guess1__ = __guess2__ = []


_ALPHABETS = {"adfgx": UC.replace("J", ""), "adfgvx": UC + DG}


def __set_params(name, square_key, trans_key):
    # keys made of digits are given as integers by the codec name pattern
    alphabet, square_key, trans_key = _ALPHABETS[name], str(square_key or ""), str(trans_key or "")
    if not trans_key or not trans_key.isalnum():
        raise LookupError(f"Bad parameter for encoding '{name}': transposition key must be a non-empty alphanumeric "
                          "string")
    square, square_key = [], square_key.upper()
    if name == "adfgx":
        square_key = square_key.replace("J", "I")
    for c in square_key:
        if c not in alphabet:
            raise LookupError(f"Bad parameter for encoding '{name}': square key can only hold characters from "
                              f"'{alphabet}'")
        if c not in square:
            square.append(c)
    square += [c for c in alphabet if c not in square]
    labels, n = name.upper(), len(name)
    enc = {c: labels[i // n] + labels[i % n] for i, c in enumerate(square)}
    # columns are read in the alphabetical order of the keyword letters, from left to right for repeated letters
    order = sorted(range(len(trans_key)), key=lambda i: (trans_key.upper()[i], i))
    return enc, {v: k for k, v in enc.items()}, order


def __adfgx(name, decode=False):
    def _wrapper(square_key=None, trans_key=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            params = __set_params(name, square_key, trans_key)
        except LookupError as e:
            params = e
        def _code(text, errors="strict"):
            if isinstance(params, LookupError):
                raise params
            enc, dec, order = params
            _h = handle_error(name, errors, decode=decode, repl_char=["X", "?"][decode])
            # whitespaces are ignored (ciphertexts are usually written in groups of 5 letters)
            text, r, n = ensure_str(text).upper(), [], len(order)
            if name == "adfgx":
                text = text.replace("J", "I")
            if decode:
                s = []
                for i, c in enumerate(text):
                    if c in name.upper():
                        s.append(c)
                    elif not c.isspace():
                        # a character out of the labels cannot be placed back in the transposition matrix
                        _h(c, i)
                # columns lengths, considering the last row of the matrix may be incomplete
                lengths, i, cols = [len(s) // n + (j < len(s) % n) for j in range(n)], 0, [None] * n
                for j in order:
                    cols[j], i = s[i:i+lengths[j]], i + lengths[j]
                s = "".join(cols[j][k] for k in range(max(lengths, default=0)) for j in range(n) if k < lengths[j])
                for i in range(0, len(s) - 1, 2):
                    r.append(dec[s[i:i+2]])
                if len(s) % 2:
                    r.append(_h(s[-1], len(s) - 1, "".join(r)))
            else:
                s = []
                for i, c in enumerate(text):
                    if c in enc:
                        s.append(enc[c])
                    elif not c.isspace():
                        # the replacement character is encrypted too ; other characters are dropped
                        s.extend(enc[x] for x in _h(c, i) if x in enc)
                s = "".join(s)
                r = [s[j::n] for j in order]
            return (s := "".join(r)), len(s)
        return _code
    return _wrapper


for _name, _ex, _gs in [("adfgx", __examples1__, __guess1__), ("adfgvx", __examples2__, __guess2__)]:
    add(_name, __adfgx(_name), __adfgx(_name, True),
        rf"^{_name}(?:[-_]cipher)?(?:[-_]([a-zA-Z0-9]+))?[-_]([a-zA-Z0-9]*)$",
        examples=_ex, guess=_gs, penalty=.1, expansion_factor=(2., .2))
