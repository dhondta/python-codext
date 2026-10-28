# -*- coding: UTF-8 -*-
"""Keccak Codecs - string hashing with Keccak.

Keccak was designed by Guido Bertoni, Joan Daemen, Michaël Peeters and Gilles Van Assche, and won the SHA-3 competition
 in 2012. It is a sponge construction over the Keccak-f[1600] permutation, whose capacity is twice the digest size. The
 SHA-3 standard (FIPS 202, provided by hashlib) differs from the original submission only in the padding of the data
 (domain separation bits "01" added before the "10*1" padding). The original Keccak, implemented here, is still used
 e.g. by Ethereum (Keccak-256).

The digest size (224, 256, 384 or 512 bits) is given with the codec name (e.g. "keccak-512") ; it defaults to 256. These
 codecs return the hexadecimal digest (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://keccak.team/files/Keccak-reference-3.0.pdf
"""
from ..__common__ import *


M64 = (1 << 64) - 1


def __rc(t):
    # output bit of the LFSR x^8 + x^6 + x^5 + x^4 + 1 (see the reference, section 1.2)
    r = 1
    for _ in range(t % 255):
        r <<= 1
        if r & 0x100:
            r ^= 0x171
    return r & 1


def __rot():
    r, x, y = [0] * 25, 1, 0
    for t in range(24):
        r[x + 5 * y], x, y = (t + 1) * (t + 2) // 2 % 64, y, (2 * x + 3 * y) % 5
    return r


# round constants and rotation offsets (see the reference, sections 1.2 and 2.3)
RC = [sum(__rc(j + 7 * i) << (2 ** j - 1) for j in range(7)) for i in range(24)]
ROT = __rot()


def __keccak_f(a):
    rol = lambda v, n: (v << n | v >> (64 - n)) & M64 if n else v
    for rc in RC:
        # theta
        c = [a[x] ^ a[x+5] ^ a[x+10] ^ a[x+15] ^ a[x+20] for x in range(5)]
        d = [c[(x - 1) % 5] ^ rol(c[(x + 1) % 5], 1) for x in range(5)]
        a = [v ^ d[i % 5] for i, v in enumerate(a)]
        # rho and pi
        r = [0] * 25
        for i, v in enumerate(a):
            x, y = i % 5, i // 5
            r[y + 5 * ((2 * x + 3 * y) % 5)] = rol(v, ROT[i])
        # chi and iota
        a = [r[i] ^ (~r[(i + 1) % 5 + i - i % 5] & r[(i + 2) % 5 + i - i % 5]) for i in range(25)]
        a[0] ^= rc
    return a


def keccak(n=""):
    # a bad digest size is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
    #  listing the encodings)
    n = n or 256
    def _hash(data, errors="strict"):
        if n not in (224, 256, 384, 512):
            raise LookupError("Bad parameter for encoding 'keccak': digest size must be 224, 256, 384 or 512")
        # rate in bytes, then pad10*1 (without the SHA-3 domain separation bits)
        d, rate = b(data), 200 - n // 4
        d += b"\x01" + b"\x00" * (-(len(d) + 1) % rate)
        d = d[:-1] + bytes([d[-1] | 0x80])
        a = [0] * 25
        for i in range(0, len(d), rate):
            for j in range(rate // 8):
                a[j] ^= int.from_bytes(d[i+8*j:i+8*j+8], "little")
            a = __keccak_f(a)
        # the digest is always shorter than the rate, hence a single squeeze
        return b"".join(v.to_bytes(8, "little") for v in a)[:n // 8].hex(), len(data)
    return _hash


add("keccak", keccak, pattern=r"^keccak(?:[-_]?(\d+))?$", guess=None)
