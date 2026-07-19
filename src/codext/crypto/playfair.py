# -*- coding: UTF-8 -*-
"""Playfair Cipher Codec - playfair content encoding.

The Playfair cipher is a symmetric encryption method using polygram substitution
with bigrams (pairs of letters), invented in 1854 by Charles Wheatstone, but
popularized by his friend Lord Playfair.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/playfair-cipher
"""
from string import ascii_uppercase as UC, digits as DG

from ..__common__ import *


__examples__ = {
    'dec(playfair_cipher-testkey-4)': None,
    'dec(playfair)':                  {'SIHTHTDQCUUTUSHOHW': "THISISATESTSTRINGX", '1a': None, 'a1b': None},
    'dec(playfair-playfairexample)':  {'BMODZBXDNABEKUDMUIXMMOUVIF': 'HIDETHEGOLDINTHETREXESTUMP'},
    'enc(playfair-*-5-XQ-IJ)':        {'UDTUTUTGMH': "TESTSTRJNG"},
    'enc(playfair_cipher-*-5-XX)':    None,
    'enc(playfair_cipher-*-5-X-JJ)':  None,
    'enc(playfair)':                  {'String!': None, 'This is a test String': "SIHTHTDQCUUTUSHOHW"},
    'enc(playfair-*-5-XQ-IJ)':        {'TESTSTRING': "UDTUTUTGMH"},
    'enc(playfair-playfairexample)':  {'HIDETHEGOLDINTHETREESTUMP': 'BMODZBXDNABEKUDMUIXMMOUVIF'},
    'enc-dec(playfair-keyword)':      ["TEST"],
    'enc-dec(playfair-*-5-X-IJ)':     ["TEST", "TESTSENTENCE"],
}
__guess__ = ["playfair"]


# Standard 5×5 Playfair alphabet (I and J share the same cell)
_DEFAULT_ALPHABET = {
    5: UC.replace("J", ""),
    6: UC + DG,
}


def __build_grid(key=None, grid_size=5, replace_char=('J', 'I')):
    """Build the Playfair grid from an optional keyword. """
    seen, grid = set(), []
    for c in key.upper():
        if c == replace_char[0]:
            c = replace_char[1]
        if c.isalpha() and c not in seen:
            seen.add(c)
            grid.append(c)
    for c in _DEFAULT_ALPHABET[grid_size]:
        if c not in seen:
            seen.add(c)
            grid.append(c)
    return grid, {grid[i]: (i // grid_size, i % grid_size) for i in range(grid_size ** 2)}


def __set_params(key, grid_size, fill_chars, replace_char):
    if len(fc := str(fill_chars or "XQ").upper()) == 2 and fc[0] == fc[1]:
        raise LookupError("Bad parameter for encoding 'playfair': filling char must be a single letter or a pair of "
                          "distinct letters")
    if len(rc := str(replace_char or "JI").upper()) == 2 and rc[0] == rc[1]:
        raise LookupError("Bad parameter for encoding 'playfair': replaced char must be a pair of distinct letters")
    gs = int(grid_size or 5)
    a = _DEFAULT_ALPHABET[gs]
    if len(fc) == 1:
        fc += a[(a.index(fc[0])+1) % len(a)]
    return (a if key == "*" else a[::-1] if key == "^" else key).upper(), gs, tuple(fc), tuple(rc)


def playfair_encode(key=None, grid_size=None, fill_chars=None, replace_char=None):
    key, gsize, fchars, rchar = __set_params(key, grid_size, fill_chars, replace_char)
    grid, pos = __build_grid(key, gsize, rchar)
    def encode(text, errors="strict"):
        _filler = lambda c: fchars[1] if c == fchars[0] else fchars[0]
        chars = [rchar[1] if c == rchar[0] else c for c in ensure_str(text).upper().replace(" ", "")]
        result, i, _h = [], 0, handle_error("playfair", errors)
        while i < len(chars):
            a = chars[i]
            if a not in grid:
                result.append(_h(a, i))
                i += 1
                continue
            if i + 1 < len(chars):
                b = chars[i+1]
                if a == b:
                    b = _filler(a)
                else:
                    i += 1
            else:
                b = _filler(a)
            r_a, c_a = pos[a]
            r_b, c_b = pos[b]
            if r_a == r_b:
                ea, eb = grid[r_a * 5 + (c_a + 1) % 5], grid[r_b * 5 + (c_b + 1) % 5]
            elif c_a == c_b:
                ea, eb = grid[((r_a + 1) % 5) * 5 + c_a], grid[((r_b + 1) % 5) * 5 + c_b]
            else:
                ea, eb = grid[r_a * 5 + c_b], grid[r_b * 5 + c_a]
            result.extend([ea, eb])
            i += 1
        return (r := "".join(result)), len(r)
    return encode


def playfair_decode(key=None, grid_size=None, fill_chars=None, replace_char=None):
    key, gsize, _, rchar = __set_params(key, grid_size, fill_chars, replace_char)
    grid, pos = __build_grid(key, gsize, rchar)
    def decode(text, errors="strict"):
        chars = [rchar[1] if c == rchar[0] else c for c in ensure_str(text)]
        result, i, _h = [], 0, handle_error("playfair", errors, decode=True)
        while i < len(chars):
            try:
                r_a, c_a = pos[chars[i]]
            except KeyError:
                result.append(_h(chars[i], i, "".join(result)))
                i += 1
                continue
            try:
                r_b, c_b = pos[chars[i+1]]
            except KeyError:
                result.append(chars[i])
                result.append(_h(chars[i+1], i+1, "".join(result)))
                i += 2
                continue
            if r_a == r_b:
                da, db = grid[r_a * 5 + (c_a - 1) % 5], grid[r_b * 5 + (c_b - 1) % 5]
            elif c_a == c_b:
                da, db = grid[((r_a - 1) % 5) * 5 + c_a], grid[((r_b - 1) % 5) * 5 + c_b]
            else:
                da, db = grid[r_a * 5 + c_b], grid[r_b * 5 + c_a]
            result.extend([da, db])
            i += 2
        return (r := "".join(result)), len(r)
    return decode


add("playfair", playfair_encode, playfair_decode,
    r"^playfair(?:[-_]cipher)?(?:[-_]([\^*]|[a-zA-Z]+))?(?:[-_]([56]))?(?:[-_]([A-Z]{1,2}))?(?:[-_]([A-Z]{2}))?$",
    printables_rate=1., penalty=.1)

