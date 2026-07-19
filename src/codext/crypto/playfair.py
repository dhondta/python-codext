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
from ..__common__ import *


__examples__ = {
    # Classic example from Wikipedia (key "PLAYFAIR EXAMPLE"):
    #   the EE in "TREE" is split with an X filler during encoding, so decoding
    #   exposes the filler: "TREESTUMP" → encoded → decoded as "TREXESTUMP"
    'enc(playfair-playfairexample)': {'HIDETHEGOLDINTHETREESTUMP': 'BMODZBXDNABEKUDMUIXMMOUVIF'},
    'dec(playfair-playfairexample)': {'BMODZBXDNABEKUDMUIXMMOUVIF': 'HIDETHEGOLDINTHETREXESTUMP'},
    'enc-dec(playfair-keyword)':     ['INSTRUMENT'],
}
__guess__ = ["playfair"]


# Standard 5×5 Playfair alphabet (I and J share the same cell)
_DEFAULT_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def _build_grid(key=None):
    """Build the 5×5 Playfair grid from an optional keyword."""
    seen, grid = set(), []
    if key:
        for c in key.upper():
            if c == 'J':
                c = 'I'
            if c.isalpha() and c not in seen:
                seen.add(c)
                grid.append(c)
    for c in _DEFAULT_ALPHABET:
        if c not in seen:
            seen.add(c)
            grid.append(c)
    pos = {grid[i]: (i // 5, i % 5) for i in range(25)}
    return grid, pos


def _filler(c):
    """Return the filler character for a given letter (X, or Q when the letter is X)."""
    return 'Q' if c == 'X' else 'X'


def _make_bigrams(text):
    """Convert plaintext to bigrams, inserting fillers for repeated-letter pairs."""
    chars = []
    for c in ensure_str(text).upper():
        if c == 'J':
            chars.append('I')
        elif c.isalpha():
            chars.append(c)
    bigrams = []
    i = 0
    while i < len(chars):
        a = chars[i]
        if i + 1 < len(chars):
            b = chars[i + 1]
            if a == b:
                bigrams.append((a, _filler(a)))
                i += 1
            else:
                bigrams.append((a, b))
                i += 2
        else:
            bigrams.append((a, _filler(a)))
            i += 1
    return bigrams


def _encode_bigram(grid, pos, a, b):
    r_a, c_a = pos[a]
    r_b, c_b = pos[b]
    if r_a == r_b:
        return grid[r_a * 5 + (c_a + 1) % 5], grid[r_b * 5 + (c_b + 1) % 5]
    elif c_a == c_b:
        return grid[((r_a + 1) % 5) * 5 + c_a], grid[((r_b + 1) % 5) * 5 + c_b]
    else:
        return grid[r_a * 5 + c_b], grid[r_b * 5 + c_a]


def _decode_bigram(grid, pos, a, b):
    r_a, c_a = pos[a]
    r_b, c_b = pos[b]
    if r_a == r_b:
        return grid[r_a * 5 + (c_a - 1) % 5], grid[r_b * 5 + (c_b - 1) % 5]
    elif c_a == c_b:
        return grid[((r_a - 1) % 5) * 5 + c_a], grid[((r_b - 1) % 5) * 5 + c_b]
    else:
        return grid[r_a * 5 + c_b], grid[r_b * 5 + c_a]


def playfair_encode(key=None):
    grid, pos = _build_grid(key)
    def encode(text, errors="strict"):
        t = ensure_str(text)
        result = []
        for a, b in _make_bigrams(t):
            ea, eb = _encode_bigram(grid, pos, a, b)
            result.extend([ea, eb])
        r = "".join(result)
        return r, len(t)
    return encode


def playfair_decode(key=None):
    grid, pos = _build_grid(key)
    def decode(text, errors="strict"):
        t = ensure_str(text)
        chars = []
        for c in t.upper():
            if c == 'J':
                chars.append('I')
            elif c.isalpha():
                chars.append(c)
        result = []
        for i in range(0, len(chars) - 1, 2):
            da, db = _decode_bigram(grid, pos, chars[i], chars[i + 1])
            result.extend([da, db])
        r = "".join(result)
        return r, len(t)
    return decode


add("playfair", playfair_encode, playfair_decode, r"^playfair(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$",
    printables_rate=1.)
