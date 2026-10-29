# -*- coding: UTF-8 -*-
"""Windows Hashing Codecs - string hashing with the LM and NT hashes.

The LAN Manager (LM) hash is the legacy password hash of Windows: the password is uppercased, encoded with the OEM code
 page (CP437), truncated or null-padded to 14 bytes, and each half is used as a DES key to encrypt the constant
 "KGS!@#$%" (DES being implemented here in pure Python, as the standard library does not provide it). The NT hash
 (often called the NTLM hash) replaced it: it is the MD4 digest of the password encoded in UTF-16LE. These codecs return
 the hexadecimal digest (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/LAN_Manager
           https://en.wikipedia.org/wiki/NTLM
           https://csrc.nist.gov/files/pubs/fips/46-3/final/docs/fips46-3.pdf
"""
from ..__common__ import *
from .md import _md4


# DES tables (see FIPS 46-3): initial permutation, expansion, permutation, permuted choices, key schedule shifts and
#  S-boxes
DES_IP = [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40,
          32, 24, 16, 8, 57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63,
          55, 47, 39, 31, 23, 15, 7]
DES_FP = [DES_IP.index(i) + 1 for i in range(1, 65)]
DES_E = [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 16, 17, 18, 19, 20, 21, 20,
         21, 22, 23, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]
DES_P = [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10, 2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11,
         4, 25]
DES_PC1 = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
           63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
DES_PC2 = [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4, 26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47,
           55, 30, 40, 51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]
DES_SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
DES_S = [
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7, 0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
     4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0, 15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10, 3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
     0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15, 13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8, 13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
     13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7, 1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15, 13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
     10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4, 3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9, 14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
     4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14, 11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11, 10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
     9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6, 4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1, 13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
     1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2, 6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7, 1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
     7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8, 2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
]


def _perm(v, table, n):
    """ Permute the bits of the n-bit integer v according to the table (1-based positions, from the MSB). """
    r = 0
    for p in table:
        r = r << 1 | v >> (n - p) & 1
    return r


def des_encrypt(key, block):
    """ Pure Python DES encryption of a single 8-bytes block with an 8-bytes key. """
    k = _perm(int.from_bytes(key, "big"), DES_PC1, 64)
    c, d, subkeys = k >> 28, k & 0xfffffff, []
    for s in DES_SHIFTS:
        c, d = (c << s | c >> (28 - s)) & 0xfffffff, (d << s | d >> (28 - s)) & 0xfffffff
        subkeys.append(_perm(c << 28 | d, DES_PC2, 56))
    v = _perm(int.from_bytes(block, "big"), DES_IP, 64)
    l, r = v >> 32, v & 0xffffffff
    for sk in subkeys:
        x, f = _perm(r, DES_E, 32) ^ sk, 0
        for i in range(8):
            # each 6-bit group selects a row (outer bits) and a column (inner bits) of its S-box
            g = x >> (42 - 6 * i) & 0x3f
            f = f << 4 | DES_S[i][(g & 0x20) | (g & 1) << 4 | g >> 1 & 0xf]
        l, r = r, l ^ _perm(f, DES_P, 32)
    return _perm(r << 32 | l, DES_FP, 64).to_bytes(8, "big")


def _deskey(k7):
    """ Spread 7 bytes (56 bits) over 8 bytes, leaving the (ignored) parity bit of each byte to 0. """
    v = int.from_bytes(k7, "big")
    return bytes((v >> (49 - 7 * i) & 0x7f) << 1 for i in range(8))


def lm(text, errors="strict"):
    p = ensure_str(text).upper().encode("cp437")[:14].ljust(14, b"\x00")
    return "".join(des_encrypt(_deskey(p[i:i+7]), b"KGS!@#$%").hex() for i in (0, 7)), len(text)


def nt(text, errors="strict"):
    return _md4(ensure_str(text).encode("utf-16-le"))[0], len(text)


add("lm", lm, pattern=r"^lm(?:[-_]?hash)?$", guess=None)
add("ntlm", nt, pattern=r"^(?:nt(?:lm)?(?:[-_]?hash)?)$", guess=None)
