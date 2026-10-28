# -*- coding: UTF-8 -*-
"""Bifid/Trifid Cipher Codec - bifid/trifid content encoding.

The Bifid and Trifid ciphers were invented by Felix Delastelle. Each letter is replaced by its coordinates in a 5x5
 Polybius square (Bifid ; I and J sharing a cell) or in a 3x3x3 cube (Trifid ; 26 letters and "+"). Within each block of
 letters (whose size is the period, the whole text by default), the coordinates are written in rows (all the rows, then
 all the columns, ...), then read again as groups of coordinates that give the new letters. The square or cube is
 filled with an optional keyword (without duplicates), then with the remaining characters of the alphabet.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Bifid_cipher
           https://en.wikipedia.org/wiki/Trifid_cipher
"""
from string import ascii_uppercase as UC

from ..__common__ import *


__examples1__ = {
    'enc(bifid-bgwkzqpndsioaxefclumthyvr)':   {'FLEEATONCE': "UAEOLWRINS", 'Flee at once!': "Uaeo lw rins!"},
    'dec(bifid_cipher-bgwkzqpndsioaxefclumthyvr)': {'UAEOLWRINS': "FLEEATONCE"},
    'enc(bifid)':                             {'TEST': "QTUO", 'Jump': "Inuk"},
    'enc-dec(bifid|bifid-keyword|bifid-keyword-5|bifid-7|bifid-0)': ["", "Hello, World!", "Test 1234!",
                                                                     "Delastelle's ciphers"],
}
__examples2__ = {
    'enc(trifid-felixmariedelastelle-5)':     {'AIDETOILECIELTAIDERA': "FMJFVOISSUFTFPUFEQQC",
                                               "aide-toi, le ciel t'aidera": "FMJF-VOI, SS UFTF P'UFEQQC"},
    'dec(trifid_cipher-felixmariedelastelle-5)': {'FMJFVOISSUFTFPUFEQQC': "AIDETOILECIELTAIDERA"},
    'enc(trifid)':                            {'TEST': "UTBK"},
    'enc-dec(trifid|trifid-keyword|trifid-keyword-5|trifid-7|trifid-0)': ["", "HELLO, WORLD!", "JUMP + 42"],
}
__guess1__, __guess2__ = ["bifid"], ["trifid"]


# cipher: (alphabet, base of the coordinates, number of coordinates per letter)
_PARAMS = {'bifid': (UC.replace("J", ""), 5, 2), 'trifid': (UC + "+", 3, 3)}


def __fractionation(name, decode=False):
    alphabet, base, n = _PARAMS[name]
    def _wrapper(key=None, period=None):
        key, square = str(key or "").upper(), []
        for c in (key.replace("J", "I") if name == "bifid" else key) + alphabet:
            if c in alphabet and c not in square:
                square.append(c)
        coords = {c: tuple(i // base ** (n - 1 - k) % base for k in range(n)) for i, c in enumerate(square)}
        letters = {v: c for c, v in coords.items()}
        period = int(str(period or 0))
        def _code(text, errors="strict"):
            text = ensure_str(text)
            # only letters of the alphabet are fractionated ; other characters are kept in place
            slots, chars = [], []
            for i, c in enumerate(text):
                if (u := c.upper()) == "J" and name == "bifid":
                    u = "I"
                if u in coords:
                    slots.append(i)
                    chars.append(u)
            result, size = [], period or len(chars) or 1
            for b in range(0, len(chars), size):
                block = chars[b:b+size]
                if decode:
                    # the coordinates of the block, written in a row, hold the rows of the encoding matrix one by one
                    digits, l = [d for c in block for d in coords[c]], len(block)
                    result += [letters[tuple(digits[k*l+j] for k in range(n))] for j in range(l)]
                else:
                    digits = [coords[c][k] for k in range(n) for c in block]
                    result += [letters[tuple(digits[j:j+n])] for j in range(0, len(digits), n)]
            r = list(text)
            for pos, c in zip(slots, result):
                # with Trifid, a letter may be substituted by "+", which cannot hold its case ; hence, uppercase
                r[pos] = c.lower() if name == "bifid" and text[pos].islower() else c
            return (s := "".join(r)), len(s)
        return _code
    return _wrapper


for _name, _ex, _gs in [("bifid", __examples1__, __guess1__), ("trifid", __examples2__, __guess2__)]:
    add(_name, __fractionation(_name), __fractionation(_name, True),
        rf"^{_name}(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?(?:[-_](\d+))?$",
        examples=_ex, guess=_gs, printables_rate=1., penalty=.1)
