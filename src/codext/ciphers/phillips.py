# -*- coding: UTF-8 -*-
"""Phillips Cipher Codec - phillips content encoding.

The Phillips cipher is a polyalphabetic substitution cipher using 8 key squares.  The first square is a 5×5 grid built
 from a keyword (I and J share one cell).  Seven additional squares are derived by sequentially swapping adjacent rows
 in a descending bubble pattern.  Plaintext is divided into blocks of T letters (default 5); each letter is individually
 enciphered by shifting its grid position right by DH columns and down by DV rows (both default to 1), wrapping
 around with toroidal topology.  J is treated as I.

Parameters:
  key        -- keyword used to seed the initial 5×5 grid (required)
  block_size -- number of letters per grid-cycle block, 1–25 (default 5)
  dh         -- horizontal (column) shift for encryption, 1–4 (default 1)
  dv         -- vertical (row) shift for encryption, 1–4 (default 1)

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/phillips-cipher
"""
from ..__common__ import *


__examples__ = {
    'dec(phillips)':               None,
    'enc(phillips)':               None,
    'enc(phillips-key)':           {'ATTACK1': None},
    'enc(phillips-key)':           {'ATTACK': "HUUHLL", 'TESTME': "UFZUSM", 'ABCDEF': "HCLMFA"},
    'enc(phillips-key-5-1-2)':     {'This is a Test String': "KPVBVHTCRHCHCGQBT"},
    'dec(phillips-key-5-1-2)':     {'KPVBVHTCRHCHCGQBT': "THISISATESTSTRING"},
    'enc-dec(phillips-key)':       ["ATTACK", "TESTME", "ABCDEF"],
    'enc-dec(phillips-secret)':    ["HELLOWORLD", "ATTACKATDAWN"],
    'enc-dec(phillips-key-2)':     ["ATTACK", "TESTME"],
    'enc-dec(phillips-key-5-2)':   ["ATTACK"],
    'enc-dec(phillips-key-5-1-2)': ["ATTACK"],
}
__guess__ = ["phillips-key", "phillips-secret", "phillips-password"]


_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def __make_grids(key):
    """Return all 8 grids built by a descending bubble-swap row permutation."""
    seen, letters = set(), []
    for c in key.upper().replace("J", "I") + _ALPHABET:
        if c in set(_ALPHABET) and c not in seen:
            letters.append(c)
            seen.add(c)
    grid = [letters[i * 5:(i + 1) * 5] for i in range(5)]
    grids = [grid]
    for k in range(7):
        r = k % 4
        grid = [row[:] for row in grid]
        grid[r], grid[r + 1] = grid[r + 1], grid[r]
        grids.append(grid)
    return grids


def __set_params(key, block_size, dh, dv):
    return (key or "").strip(), \
           int(block_size) if block_size else 5, \
           int(dh) if dh else 1, \
           int(dv) if dv else 1, \
           __make_grids(key) if key and key.isalpha() else None


def __shift_text(text, grids, block_size, dh, dv, errors, decode=False):
    pos_maps = [{ch: (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)} for grid in grids]
    r, i, t = "", 0, ensure_str(text).upper().replace("J", "I").replace(" ", "")
    _h = handle_error("phillips", errors, decode=decode)
    for pos, c in enumerate(t):
        if c not in set(_ALPHABET):
            r += _h(c, pos, r)
        else:
            grid_idx = (i // block_size) % 8
            grid = grids[grid_idx]
            s, col = pos_maps[grid_idx][c]
            r += grid[(s + dv) % 5][(col + dh) % 5]
            i += 1
    return r, len(r)


def phillips_encode(key, block_size=None, dh=None, dv=None):
    _key, block_size, dh, dv, grids = __set_params(key, block_size, dh, dv)
    def encode(text, errors="strict"):
        if _key == "":
            raise LookupError("Bad parameter for encoding 'phillips': key cannot be empty")
        return __shift_text(text, grids, block_size, dh, dv, errors)
    return encode


def phillips_decode(key, block_size=None, dh=None, dv=None):
    _key, block_size, dh, dv, grids = __set_params(key, block_size, dh, dv)
    def decode(text, errors="strict"):
        if _key == "":
            raise LookupError("Bad parameter for encoding 'phillips': key cannot be empty")
        return __shift_text(text, grids, block_size, -dh, -dv, errors, True)
    return decode


add("phillips", phillips_encode, phillips_decode,
    r"^phillips(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?(?:[-_]([1-9]|1[0-9]|2[0-5]))?(?:[-_]([1-4]))?(?:[-_]([1-4]))?$",
    printables_rate=1., penalty=.1)

