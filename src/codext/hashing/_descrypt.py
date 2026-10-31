# -*- coding: UTF-8 -*-
"""DES-based crypt primitive, shared by the traditional crypt(3) password hashes (bigcrypt, BSDi crypt and crypt16).

These hashes build a DES key from the password and encrypt a zero block a number of times (25 for the traditional
 scheme), a 24-bit salt mutating the DES algorithm by swapping bits of the expansion. This module reuses the pure
 Python DES tables of the Windows hashes module.
"""
from .windows import _perm, DES_IP, DES_FP, DES_E, DES_P, DES_S, DES_PC1, DES_PC2, DES_SHIFTS


def _subkeys(key):
    """ The 16 DES subkeys of the given 64-bit key. """
    k, sk = _perm(key, DES_PC1, 64), []
    c, d = k >> 28, k & 0xfffffff
    for s in DES_SHIFTS:
        c = ((c << s) | (c >> (28 - s))) & 0xfffffff
        d = ((d << s) | (d >> (28 - s))) & 0xfffffff
        sk.append(_perm((c << 28) | d, DES_PC2, 56))
    return sk


def _feistel(r, sk, salt):
    """ The DES round function, the 24-bit salt swapping bits i and i+24 of the 48-bit expansion. """
    e = _perm(r, DES_E, 32)
    for i in range(24):
        if (salt >> i) & 1 and (e >> (47 - i) ^ e >> (23 - i)) & 1:
            e ^= (1 << (47 - i)) | (1 << (23 - i))
    x, f = e ^ sk, 0
    for i in range(8):
        g = (x >> (42 - 6 * i)) & 0x3f
        f = (f << 4) | DES_S[i][(g & 0x20) | ((g & 1) << 4) | ((g >> 1) & 0xf)]
    return _perm(f, DES_P, 32)


def des_int(key, salt=0, rounds=1, block=0):
    """ Encrypt a 64-bit block with the DES key, repeating the encryption the given number of rounds (as the crypt(3)
         scheme does) and mutating the algorithm with the 24-bit salt. """
    sk = _subkeys(key)
    v = _perm(block, DES_IP, 64)
    l, r = v >> 32, v & 0xffffffff
    for _ in range(rounds):
        for k in sk:
            l, r = r, l ^ _feistel(r, k, salt)
        l, r = r, l
    return _perm((l << 32) | r, DES_FP, 64)


def secret_to_key(secret):
    """ Build a 64-bit DES key from the first 8 bytes of the secret (7 bits each, null parity bits). """
    return sum((c & 0x7f) << (57 - i * 8) for i, c in enumerate(secret[:8]))
