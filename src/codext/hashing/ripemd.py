# -*- coding: UTF-8 -*-
"""RIPEMD Hashing Codec - string hashing with RIPEMD-160.

RIPEMD-160 (RACE Integrity Primitives Evaluation Message Digest) was designed in 1996 by Hans Dobbertin, Antoon
 Bosselaers and Bart Preneel. It produces a 160-bit digest by processing each block of the data in two parallel lines of
 5 rounds, and is used e.g. in Bitcoin addresses. As OpenSSL 3 only provides it in its legacy provider, it is computed
 with hashlib when available and in pure Python otherwise. This codec returns the hexadecimal digest (one-way), for use
 with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://homes.esat.kuleuven.be/~bosselae/ripemd160.html
"""
from ..__common__ import *


# message word selection, rotation amounts and constants of the left and right lines
RMD_R1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
          3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12, 1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
          4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]
RMD_R2 = [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12, 6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
          15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13, 8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
          12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]
RMD_S1 = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
          7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
          11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
          11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
          9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]
RMD_S2 = [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
          9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
          9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
          15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
          8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]
RMD_K1 = [0x00000000, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e]
RMD_K2 = [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0x00000000]
RMD_F = [lambda x, y, z: x ^ y ^ z,
         lambda x, y, z: x & y | ~x & z,
         lambda x, y, z: (x | ~y) ^ z,
         lambda x, y, z: x & z | y & ~z,
         lambda x, y, z: x ^ (y | ~z)]


def ripemd160(data):
    """ Pure Python implementation of RIPEMD-160. """
    d, m = b(data), 0xffffffff
    rol = lambda v, n: (v << n | v >> (32 - n)) & m
    d += b"\x80" + b"\x00" * (-(len(d) + 9) % 64) + (8 * len(d)).to_bytes(8, "little")
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
    for i in range(0, len(d), 64):
        x = [int.from_bytes(d[i+j:i+j+4], "little") for j in range(0, 64, 4)]
        a1, b1, c1, d1, e1 = a2, b2, c2, d2, e2 = h
        for j in range(80):
            k = j // 16
            t = (rol((a1 + RMD_F[k](b1, c1, d1) + x[RMD_R1[j]] + RMD_K1[k]) & m, RMD_S1[j]) + e1) & m
            a1, e1, d1, c1, b1 = e1, d1, rol(c1, 10), b1, t
            t = (rol((a2 + RMD_F[4-k](b2, c2, d2) + x[RMD_R2[j]] + RMD_K2[k]) & m, RMD_S2[j]) + e2) & m
            a2, e2, d2, c2, b2 = e2, d2, rol(c2, 10), b2, t
        h = [(h[1] + c1 + d2) & m, (h[2] + d1 + e2) & m, (h[3] + e1 + a2) & m, (h[4] + a1 + b2) & m,
             (h[0] + b1 + c2) & m]
    return b"".join(v.to_bytes(4, "little") for v in h).hex()


def _ripemd160(s, error="strict"):
    try:
        return hashlib.new("ripemd160", b(s)).hexdigest(), len(s)
    except ValueError:
        return ripemd160(s), len(s)


add("ripemd160", _ripemd160, pattern=r"^(?:ripemd|rmd)[-_]?160$", guess=None)
