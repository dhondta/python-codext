# -*- coding: UTF-8 -*-
"""SHA Hashing Codecs - string hashing with Secure Hash Algorithms.

The Secure Hash Algorithms are published by the NIST: SHA-0 (1993, 160 bits, withdrawn soon after its publication and
 implemented here as it is not provided by hashlib), SHA-1 (1995, which only adds a one-bit rotation in the message
 schedule of SHA-0, now broken), the SHA-2 family designed by the NSA (SHA-224, SHA-256, SHA-384 and SHA-512) and the
 SHA-3 family (SHA3-224 to SHA3-512, based on Keccak, standardised in 2015). These codecs return the hexadecimal digest
 (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/SHA-1#SHA-0
           https://csrc.nist.gov/pubs/fips/180-4/upd1/final
           https://csrc.nist.gov/pubs/fips/202/final
"""
from ..__common__ import *


def sha0(data):
    # same as SHA-1 (see FIPS 180-4, section 6.1.2), without the 1-bit left rotation in the message schedule
    d, m = b(data), 0xffffffff
    d += b"\x80" + b"\x00" * (-(len(d) + 9) % 64) + (8 * len(d)).to_bytes(8, "big")
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
    for i in range(0, len(d), 64):
        w = [int.from_bytes(d[i+j:i+j+4], "big") for j in range(0, 64, 4)]
        for t in range(16, 80):
            w.append(w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16])
        a, b_, c, d_, e = h
        for t in range(80):
            if t < 20:
                f, k = (b_ & c) | (~b_ & d_), 0x5a827999
            elif t < 40:
                f, k = b_ ^ c ^ d_, 0x6ed9eba1
            elif t < 60:
                f, k = (b_ & c) | (b_ & d_) | (c & d_), 0x8f1bbcdc
            else:
                f, k = b_ ^ c ^ d_, 0xca62c1d6
            a, b_, c, d_, e = ((a << 5 | a >> 27) + f + e + k + w[t]) & m, a, (b_ << 30 | b_ >> 2) & m, c, d_
        h = [(x + y) & m for x, y in zip(h, [a, b_, c, d_, e])]
    return "".join(f"{x:08x}" for x in h)


add("sha0", lambda s, error="strict": (sha0(s), len(s)), guess=None)
add("sha1", lambda s, error="strict": (hashlib.sha1(b(s)).hexdigest(), len(s)), guess=None)
add("sha224", lambda s, error="strict": (hashlib.sha224(b(s)).hexdigest(), len(s)), guess=None)
add("sha256", lambda s, error="strict": (hashlib.sha256(b(s)).hexdigest(), len(s)), guess=None)
add("sha384", lambda s, error="strict": (hashlib.sha384(b(s)).hexdigest(), len(s)), guess=None)
add("sha512", lambda s, error="strict": (hashlib.sha512(b(s)).hexdigest(), len(s)), guess=None)
add("sha3_224", lambda s, error="strict": (hashlib.sha3_224(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]224$",
    guess=None)
add("sha3_256", lambda s, error="strict": (hashlib.sha3_256(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]256$",
    guess=None)
add("sha3_384", lambda s, error="strict": (hashlib.sha3_384(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]384$",
    guess=None)
add("sha3_512", lambda s, error="strict": (hashlib.sha3_512(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]512$",
    guess=None)

