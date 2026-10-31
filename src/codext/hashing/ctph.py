# -*- coding: UTF-8 -*-
"""CTPH Hashing Codecs - string hashing with context triggered piecewise hashes (fuzzy hashes).

Context triggered piecewise hashing (CTPH), devised by Jesse Kornblum from Andrew Tridgell's spamsum, splits the data
 where a rolling hash of the last 7 bytes hits a trigger value depending on a block size, and writes one Base64
 character (from an FNV hash) per piece, hence similar data give similar hashes. The "ssdeep" codec gives the hash of
 ssdeep (libfuzzy), i.e. "blocksize:hash1:hash2" with at most 64 and 32 characters, the block size starting at 3 and
 doubling until 64 pieces fit the data, then being halved while the first hash has less than 32 characters. The "ctph"
 codec gives the variant of the ctph.js library (used e.g. by CyberChef's "CTPH" operation), whose block size starts at
 24, whose hashes are not truncated, and whose first field is the Base64 character of the block size exponent. These
 codecs return the hash (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://ssdeep-project.github.io/ssdeep/
           https://github.com/huwenshuo/ctph.js
"""
from math import ceil, log

from ..__common__ import *


B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
FNV_INIT, FNV_PRIME = 0x28021967, 0x01000193


def _pieces(data, bs, fnv, limits=None):
    """ Compute the two piecewise hashes of the data for the given block size, with the given FNV step. """
    h1 = h2 = FNV_INIT
    rx = ry = rz = r = 0
    win, s1, s2, l1, l2, last = [0] * 7, "", "", "", "", len(data) - 1
    for i, c in enumerate(data):
        h1, h2 = fnv(h1, c), fnv(h2, c)
        # rolling hash of the last 7 bytes
        ry = (ry - rx + 7 * c) & 0xffffffff
        rx = (rx + c - win[i % 7]) & 0xffffffff
        win[i % 7] = c
        rz = (rz << 5 ^ c) & 0xffffffff
        r = (rx + ry + rz) & 0xffffffff
        if limits:
            # ssdeep: at most 63 and 31 characters, the last pieces being merged with the final one (the character of
            #  the last trigger being kept for the case where the rolling hash ends with 0)
            if r % bs == bs - 1:
                l1 = B64[h1 & 63]
                if len(s1) < limits[0]:
                    s1, h1, l1 = s1 + l1, FNV_INIT, ""
            if r % (2 * bs) == 2 * bs - 1:
                l2 = B64[h2 & 63]
                if len(s2) < limits[1]:
                    s2, h2, l2 = s2 + l2, FNV_INIT, ""
        else:
            # ctph.js: the last byte always ends a piece
            if i == last or r % bs == bs - 1:
                s1, h1 = s1 + B64[h1 & 63], FNV_INIT
            if i == last or r % (2 * bs) == 2 * bs - 1:
                s2, h2 = s2 + B64[h2 & 63], FNV_INIT
    # final characters: from the current FNV hashes, or from the last triggers if the rolling hash ends with 0
    return s1, s2, (B64[h1 & 63], B64[h2 & 63]) if r else (l1, l2)


def ssdeep(text, errors="strict"):
    data = b(ensure_str(text))
    # only the 6 least significant bits of the FNV hashes are used, hence the multiplication can be done modulo 64
    fnv = lambda h, c: (h * FNV_PRIME ^ c) & 63
    bs = 3
    while bs * 64 < len(data):
        bs *= 2
    while True:
        s1, s2, (c1, c2) = _pieces(data, bs, fnv, (63, 31))
        if bs > 3 and len(s1) < 32:
            bs //= 2
            continue
        return f"{bs}:{s1 + c1}:{s2 + c2}", len(text)


def ctph(text, errors="strict"):
    data = b(ensure_str(text))
    # as in JavaScript, the multiplication is made with double-precision floats (losing the low bits of large products)
    fnv = lambda h, c: (int(float(h) * FNV_PRIME) & 0xffffffff) ^ c
    bi = max(3, ceil(log(len(data) / 192, 2))) if data else 3
    s1, s2, _ = _pieces(data, 3 << bi, fnv)
    while bi > 0 and len(s1) < 32:
        bi -= 1
        s1, s2, _ = _pieces(data, 3 << bi, fnv)
    return f"{B64[bi]}:{s1}:{s2}", len(text)


add("ssdeep", ssdeep, pattern=r"^ssdeep$", guess=None)
add("ctph", ctph, pattern=r"^ctph$", guess=None)
