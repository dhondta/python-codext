# -*- coding: UTF-8 -*-
"""Phillips Cipher Codec - phillips content encoding.

The Phillips cipher is a polyalphabetic substitution cipher using 8 key
squares.  The first square is a 5×5 grid built from a keyword (I and J share
one cell).  Seven additional squares are derived by rotating every row of the
previous square one step to the left.  Plaintext is enciphered in bigrams,
each pair using the next square in a cycle of 8.  Non-alphabetic characters
are passed through unchanged; J is treated as I.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/phillips-cipher
"""
from ..__common__ import *


__examples__ = {
    'enc(phillips)':             None,
    'enc(phillips-key)':         {'ATTACK': 'BSSBIC', 'TESTME': 'QBTPLY', 'ABCDEF': 'BKDFYD'},
    'enc-dec(phillips-key)':     ['ATTACK', 'TESTME', 'ABCDEF'],
    'enc-dec(phillips-secret)':  ['HELLOWORLD', 'ATTACKATDAWN'],
}
__guess__ = ["phillips-key", "phillips-secret", "phillips-password"]


_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def __make_grids(key):
    """Return all 8 grids: the initial grid plus 7 row-rotated variants."""
    # build the initial 5×5 grid from a keyword (J treated as I)
    seen, letters = set(), []
    for c in key.upper().replace("J", "I") + _ALPHABET:
        if c in set(_ALPHABET) and c not in seen:
            letters.append(c)
            seen.add(c)
    grid = [letters[i * 5:(i + 1) * 5] for i in range(5)]
    # now build the other 7 row-rotated variant grids
    grids = [grid]
    for _ in range(7):
        grid = [row[1:] + [row[0]] for row in grid]
        grids.append(grid)
    return grids


def __process_pair(a, b, grid, decode=False):
    """Encode or decode a letter pair using Playfair substitution rules.

    Same row   → each letter shifts one step right (encode) / left (decode).
    Same col   → each letter shifts one step down  (encode) / up   (decode).
    Rectangle  → each letter moves to the other's column (self-inverse).
    """
    pos = {ch: (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)}
    r1, c1 = pos[a]
    r2, c2 = pos[b]
    d = -1 if decode else 1
    if r1 == r2:
        return grid[r1][(c1 + d) % 5], grid[r2][(c2 + d) % 5]
    if c1 == c2:
        return grid[(r1 + d) % 5][c1], grid[(r2 + d) % 5][c2]
    return grid[r1][c2], grid[r2][c1]  # rectangle rule is its own inverse


def phillips_encode(key):
    _key = (key or "").strip()
    # Compute grids eagerly if key is valid; otherwise defer error to call time
    _grids = __make_grids(_key) if _key and _key.isalpha() else None
    def encode(text, errors="strict"):
        if _grids is None:
            raise LookupError("Bad parameter for encoding 'phillips': "
                              "key must be a non-empty alphabetic string")
        t = ensure_str(text).upper().replace("J", "I")
        alpha = [(i, c) for i, c in enumerate(t) if c in set(_ALPHABET)]
        # Pad to an even count with a trailing X
        padding_char = None
        if len(alpha) % 2 == 1:
            alpha.append((-1, "X"))
        enc_map = {}
        for pair_num, k in enumerate(range(0, len(alpha), 2)):
            pos1, a = alpha[k]
            pos2, b = alpha[k + 1]
            e1, e2 = __process_pair(a, b, _grids[pair_num % 8])
            enc_map[pos1] = e1
            if pos2 >= 0:
                enc_map[pos2] = e2
            else:
                padding_char = e2
        result = [enc_map.get(i, c) for i, c in enumerate(t)]
        if padding_char is not None:
            result.append(padding_char)
        return "".join(result), len(text)
    return encode


def phillips_decode(key):
    _key = (key or "").strip()
    # Compute grids eagerly if key is valid; otherwise defer error to call time
    _grids = __make_grids(_key) if _key and _key.isalpha() else None
    def decode(text, errors="strict"):
        if _grids is None:
            raise LookupError("Bad parameter for decoding 'phillips': "
                              "key must be a non-empty alphabetic string")
        t = ensure_str(text).upper().replace("J", "I")
        alpha = [(i, c) for i, c in enumerate(t) if c in set(_ALPHABET)]
        if len(alpha) % 2 == 1:
            if errors == "strict":
                raise ValueError("phillips: encoded text must contain an even "
                                 "number of alphabetic characters")
            alpha = alpha[:-1]
        dec_map = {}
        for pair_num, k in enumerate(range(0, len(alpha), 2)):
            pos1, a = alpha[k]
            pos2, b = alpha[k + 1]
            d1, d2 = __process_pair(a, b, _grids[pair_num % 8], decode=True)
            dec_map[pos1] = d1
            dec_map[pos2] = d2
        return "".join(dec_map.get(i, c) for i, c in enumerate(t)), len(text)
    return decode


add("phillips", phillips_encode, phillips_decode, r"^phillips(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", printables_rate=1.,
    penalty=.1)
