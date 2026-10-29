# -*- coding: UTF-8 -*-
"""Bcrypt Hashing Codec - string hashing with bcrypt.

bcrypt is the password hashing function designed by Niels Provos and David Mazieres in 1999, based on the Blowfish
 cipher. Its expensive key schedule (EksBlowfish) mixes the password (null-terminated and truncated to 72 bytes) and a
 128-bit salt into the Blowfish state 2^cost times, then encrypts "OrpheanBeholderScryDoubt" 64 times with it. The
 result is written in the modular crypt format "$2b$<cost>$<salt><digest>", with a custom base64 alphabet. The cost is
 given in the codec name (from 4 to 31, e.g. "bcrypt-12" ; it defaults to 12) and a random salt is generated each time,
 hence the output differs between calls. This codec relies on the bcrypt package when it is installed ("bcrypt" extra),
 and on a pure Python implementation otherwise (much slower, a cost of 12 taking about 40 seconds). It returns the hash
 string (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://www.usenix.org/legacy/events/usenix99/provos/provos.pdf
"""
from os import urandom

from ..__common__ import *


BCRYPT_B64 = "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
BCRYPT_TEXT = b"OrpheanBeholderScryDoubt"
M32 = 0xffffffff
_BF = []


def __blowfish_init():
    """ Compute the initial Blowfish state (P-array and S-boxes) from the hexadecimal digits of the fractional part of
         pi, with Machin's formula. """
    if not _BF:
        n = 1042 * 32 + 64
        def arctan_inv(x):
            s, t, k, x2 = 0, (1 << n) // x, 1, x * x
            while t:
                s += t // k if k % 4 == 1 else -(t // k)
                t //= x2
                k += 2
            return s
        f = (16 * arctan_inv(5) - 4 * arctan_inv(239)) >> 64
        w = [f >> (32 * (1041 - i)) & M32 for i in range(1042)]
        _BF.extend([w[:18]] + [w[18+256*i:274+256*i] for i in range(4)])
    return [l[:] for l in _BF]


def _b64(data):
    """ Encode bytes with the bcrypt base64 alphabet (big-endian bit order, without padding). """
    v, n = int.from_bytes(data, "big"), len(data) * 8
    v <<= -n % 6
    return "".join(BCRYPT_B64[v >> (6 * i) & 63] for i in range((n + 5) // 6 - 1, -1, -1))


def bcrypt(password, salt, cost):
    """ Pure Python implementation of bcrypt, returning the raw 23 bytes of the digest. """
    P, S0, S1, S2, S3 = __blowfish_init()
    def encipher(l, r):
        for i in range(0, 16, 2):
            l ^= P[i]
            r ^= (((S0[l >> 24] + S1[l >> 16 & 255]) & M32 ^ S2[l >> 8 & 255]) + S3[l & 255]) & M32
            r ^= P[i+1]
            l ^= (((S0[r >> 24] + S1[r >> 16 & 255]) & M32 ^ S2[r >> 8 & 255]) + S3[r & 255]) & M32
        return r ^ P[17], l ^ P[16]
    def words(data):
        d = (data * 4)[:len(data) * 4]
        return [int.from_bytes(d[i:i+4], "big") for i in range(0, len(d), 4)]
    def expand(key, salt=None):
        k = words(key)
        for i in range(18):
            P[i] ^= k[i % len(k)]
        s = words(salt) if salt else [0, 0]
        l = r = 0
        j = 0
        for box in (P, S0, S1, S2, S3):
            for i in range(0, len(box), 2):
                l, r = encipher(l ^ s[j], r ^ s[j+1])
                box[i], box[i+1] = l, r
                j = (j + 2) % len(s)
    key = (b(password) + b"\x00")[:72]
    expand(key, salt)
    for _ in range(1 << cost):
        expand(key)
        expand(salt)
    c = words(BCRYPT_TEXT)[:6]
    for _ in range(64):
        for i in range(0, 6, 2):
            c[i], c[i+1] = encipher(c[i], c[i+1])
    return b"".join(x.to_bytes(4, "big") for x in c)[:23]


def bcrypt_hash(cost=None):
    cost = int(cost or 12)
    def _encode(text, errors="strict"):
        if not 4 <= cost <= 31:
            raise LookupError("Bad parameter for encoding 'bcrypt': cost must be from 4 to 31")
        try:
            import bcrypt as _bcrypt
            return _bcrypt.hashpw(b(text)[:72], _bcrypt.gensalt(cost)).decode(), len(text)
        except ImportError:
            salt = urandom(16)
            return f"$2b${cost:02d}${_b64(salt)}{_b64(bcrypt(text, salt, cost))}", len(text)
    return _encode


add("bcrypt", bcrypt_hash, pattern=r"^bcrypt(?:[-_](\d{1,2}))?$", guess=None)
