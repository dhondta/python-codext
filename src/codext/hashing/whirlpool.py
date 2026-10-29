# -*- coding: UTF-8 -*-
"""Whirlpool Hashing Codec - string hashing with Whirlpool.

Whirlpool was designed in 2000 by Vincent Rijmen and Paulo Barreto, and adopted in ISO/IEC 10118-3. It produces a
 512-bit digest with a Miyaguchi-Preneel compression function built on a dedicated 512-bit block cipher, similar to AES,
 working on an 8x8 matrix of bytes over 10 rounds. As OpenSSL 3 only provides it in its legacy provider, it is computed
 with hashlib when available and in pure Python otherwise. This codec returns the hexadecimal digest (one-way), for use
 with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://web.archive.org/web/20171129084214/http://www.larc.usp.br/~pbarreto/WhirlpoolPage.html
"""
from ..__common__ import *


def __sbox():
    # the S-box is built from the 4-bit mini-boxes E, its inverse and R (see the specification, section 6.1)
    e = [0x1, 0xb, 0x9, 0xc, 0xd, 0x6, 0xf, 0x3, 0xe, 0x8, 0x7, 0x4, 0xa, 0x2, 0x5, 0x0]
    r = [0x7, 0xc, 0xb, 0xd, 0xe, 0x4, 0x9, 0xf, 0x6, 0x3, 0x8, 0xa, 0x2, 0x5, 0x1, 0x0]
    ei, s = [e.index(i) for i in range(16)], []
    for u in range(256):
        a, b = e[u >> 4], ei[u & 0xf]
        t = r[a ^ b]
        s.append(e[a ^ t] << 4 | ei[b ^ t])
    return s


def __mul(x, y):
    # multiplication in GF(2^8) with the reduction polynomial x^8 + x^4 + x^3 + x^2 + 1
    p = 0
    while y:
        if y & 1:
            p ^= x
        x, y = (x << 1) ^ (0x11d if x & 0x80 else 0), y >> 1
    return p


def __tables():
    # T[j][x] is the row vector (as a 64-bit integer) of S[x] multiplied by row j of the circulant MDS matrix
    #  circ(1, 1, 4, 1, 8, 5, 2, 9), combining the substitution and the diffusion layers
    s, c = __sbox(), [1, 1, 4, 1, 8, 5, 2, 9]
    tables = [[int.from_bytes(bytes(__mul(s[x], c[(k - j) % 8]) for k in range(8)), "big") for x in range(256)]
              for j in range(8)]
    # round constants: the 8 successive entries of the S-box in the first row, other rows being null
    return tables, [int.from_bytes(bytes(s[8*r:8*r+8]), "big") for r in range(10)]


WP_T, WP_RC = __tables()


def __round(a, k):
    # substitution, cyclical permutation (column j shifted down by j), linear diffusion and key addition, each row
    #  of the state being a 64-bit integer
    return [k[i] ^ WP_T[0][a[i] >> 56] ^ WP_T[1][a[(i-1) % 8] >> 48 & 0xff] ^ WP_T[2][a[(i-2) % 8] >> 40 & 0xff] ^
            WP_T[3][a[(i-3) % 8] >> 32 & 0xff] ^ WP_T[4][a[(i-4) % 8] >> 24 & 0xff] ^
            WP_T[5][a[(i-5) % 8] >> 16 & 0xff] ^ WP_T[6][a[(i-6) % 8] >> 8 & 0xff] ^ WP_T[7][a[(i-7) % 8] & 0xff]
            for i in range(8)]


def whirlpool(data):
    """ Pure Python implementation of Whirlpool. """
    d = b(data)
    # padding: a 1 bit, then 0 bits up to an odd multiple of 256 bits, then the length on 256 bits
    d += b"\x80" + b"\x00" * (-(len(d) + 33) % 64) + (8 * len(d)).to_bytes(32, "big")
    h = [0] * 8
    for i in range(0, len(d), 64):
        m = [int.from_bytes(d[i+j:i+j+8], "big") for j in range(0, 64, 8)]
        k, s = h, [x ^ y for x, y in zip(m, h)]
        for rc in WP_RC:
            k = __round(k, [rc] + [0] * 7)
            s = __round(s, k)
        h = [x ^ y ^ z for x, y, z in zip(s, h, m)]
    return b"".join(v.to_bytes(8, "big") for v in h).hex()


def _whirlpool(s, error="strict"):
    try:
        return hashlib.new("whirlpool", b(s)).hexdigest(), len(s)
    except ValueError:
        return whirlpool(s), len(s)


add("whirlpool", _whirlpool, guess=None)
