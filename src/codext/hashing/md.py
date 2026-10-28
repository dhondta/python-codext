# -*- coding: UTF-8 -*-
"""MD Hashing Codecs - string hashing with Message Digest (MD).

The Message Digest algorithms were designed by Ronald Rivest: MD2 (1989, implemented here as it is not provided by
 hashlib anymore), MD4 (1990, only when available in hashlib) and MD5 (1991), all producing 128-bit digests ; they are
 now considered broken for cryptographic use. MD6 (2008, submitted to the SHA-3 competition) is unrelated to them: it
 compresses blocks of 512 bytes into chaining values of 128 bytes along a 4-ary tree, which the last compression
 truncates to the digest size (from 8 to 512 bits, given with the codec name, e.g. "md6-512" ; it defaults to 256). It
 is implemented here in its default mode, unkeyed and with a tree height of 64. These codecs return the hexadecimal
 digest (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc1319
           https://datatracker.ietf.org/doc/html/rfc1320
           https://datatracker.ietf.org/doc/html/rfc1321
           https://people.csail.mit.edu/rivest/pubs/RABCx08.pdf
"""
from math import isqrt

from ..__common__ import *


MD2_TABLE = [41, 46, 67, 201, 162, 216, 124, 1, 61, 54, 84, 161, 236, 240, 6, 19, 98, 167, 5, 243, 192, 199, 115, 140,
    152, 147, 43, 217, 188, 76, 130, 202, 30, 155, 87, 60, 253, 212, 224, 22, 103, 66, 111, 24, 138, 23, 229, 18, 190,
    78, 196, 214, 218, 158, 222, 73, 160, 251, 245, 142, 187, 47, 238, 122, 169, 104, 121, 145, 21, 178, 7, 63, 148,
    194, 16, 137, 11, 34, 95, 33, 128, 127, 93, 154, 90, 144, 50, 39, 53, 62, 204, 231, 191, 247, 151, 3, 255, 25, 48,
    179, 72, 165, 181, 209, 215, 94, 146, 42, 172, 86, 170, 198, 79, 184, 56, 210, 150, 164, 125, 182, 118, 252, 107,
    226, 156, 116, 4, 241, 69, 157, 112, 89, 100, 113, 135, 32, 134, 91, 207, 101, 230, 45, 168, 2, 27, 96, 37, 173,
    174, 176, 185, 246, 28, 70, 97, 105, 52, 64, 126, 15, 85, 71, 163, 35, 221, 81, 175, 58, 195, 92, 249, 206, 186,
    197, 234, 38, 44, 83, 13, 110, 133, 40, 132, 9, 211, 223, 205, 244, 65, 129, 77, 82, 106, 220, 55, 200, 108, 193,
    171, 250, 36, 225, 123, 8, 12, 189, 177, 74, 120, 136, 149, 139, 227, 99, 232, 109, 233, 203, 213, 254, 59, 0, 29,
    57, 242, 239, 183, 14, 102, 88, 208, 228, 166, 119, 114, 248, 235, 117, 75, 10, 49, 68, 80, 180, 143, 237, 31, 26,
    219, 153, 141, 51, 159, 17, 131, 20]


def md2(data):
    # see spec in RFC1319
    bs, buff, rnd, data = 16, 48, 18, bytearray(b(data))
    # first pad the input data
    n = bs - len(data) % bs
    data += bytearray([n for _ in range(n)])
    # then compute the checksum and append it to the data
    checksum, prev, l, lt = bytearray(bs), 0, len(data) // bs, len(MD2_TABLE)
    for i in range(l):
        for j in range(bs):
            curr = data[bs * i + j]
            checksum[j] ^= MD2_TABLE[curr ^ prev]
            prev = checksum[j]
    data += checksum
    # now compute the digest
    digest = bytearray(buff)
    for i in range(l + 1):
        for j in range(bs):
            digest[bs + j] = data[i * bs + j]
            digest[2 * bs + j] = digest[bs + j] ^ digest[j]
        prev = 0
        for j in range(rnd):
            for k in range(buff):
                digest[k] = prev = digest[k] ^ MD2_TABLE[prev]
            prev = (prev + j) % lt
    return "".join("{:02x}".format(x) for x in digest[:16])


# MD6 constants (see the specification, section 9): Q (15 words of the fractional part of sqrt(6)), the tap positions,
#  the shift amounts and the round constants (initial value and mask)
M64 = (1 << 64) - 1
MD6_Q = [isqrt(6 << 1920) >> (64 * (14 - i)) & M64 for i in range(15)]
MD6_T = (17, 18, 21, 31, 67, 89)
MD6_R = (10, 5, 13, 10, 11, 12, 2, 7, 14, 15, 7, 13, 11, 7, 6, 12)
MD6_L = (11, 24, 9, 16, 15, 9, 27, 15, 6, 2, 29, 8, 15, 5, 31, 9)
MD6_S0, MD6_SM = 0x0123456789abcdef, 0x7311c2812425cfa0


def __md6_compress(n, rounds):
    a, s, (t0, t1, t2, t3, t4, t5) = n[:], MD6_S0, MD6_T
    for i in range(89, 89 + 16 * rounds):
        j = (i - 89) % 16
        if j == 0 and i > 89:
            s = (s << 1 | s >> 63) & M64 ^ s & MD6_SM
        x = s ^ a[i-t5] ^ a[i-t0] ^ (a[i-t1] & a[i-t2]) ^ (a[i-t3] & a[i-t4])
        x ^= x >> MD6_R[j]
        a.append((x ^ x << MD6_L[j]) & M64)
    return a[-16:]


def md6(n=""):
    # a bad digest size is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
    #  listing the encodings)
    n = n or 256
    def _hash(data, errors="strict"):
        if n not in range(8, 513, 8):
            raise LookupError("Bad parameter for encoding 'md6': digest size must be a multiple of 8 from 8 to 512")
        # default mode (see the specification, section 2.4): no key, tree of height L=64 and r=40+d/4 rounds ; with
        #  L=64, the sequential mode at level L+1 is never reached
        m, rounds, lvl, key = b(data), 40 + n // 4, 0, [0] * 8
        while True:
            lvl += 1
            nb, out = max(1, -(-len(m) // 512)), b""
            for i in range(nb):
                blk = m[512*i:512*(i+1)]
                # control word: rounds, L, final compression flag (z), padding bits (p), key length and digest size
                p = 8 * (512 - len(blk))
                v = rounds << 48 | 64 << 40 | (nb == 1) << 36 | p << 20 | n
                blk += b"\x00" * (p // 8)
                w = [int.from_bytes(blk[k:k+8], "big") for k in range(0, 512, 8)]
                out += b"".join(x.to_bytes(8, "big") for x in __md6_compress(MD6_Q + key + [lvl << 56 | i, v] + w,
                                                                               rounds))
            m = out
            if nb == 1:
                return m[-n // 8:].hex(), len(data)
    return _hash


add("md2", lambda s, error="strict": (md2(s), len(s)), guess=None)
add("md5", lambda s, error="strict": (hashlib.new("md5", b(s)).hexdigest(), len(s)), guess=None)
if "md4" in hashlib.algorithms_available:
    add("md4", lambda s, error="strict": (hashlib.new("md4", b(s)).hexdigest(), len(s)), guess=None)

add("md6", md6, pattern=r"^md6(?:[-_]?(\d+))?$", guess=None)
