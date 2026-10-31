# -*- coding: UTF-8 -*-
"""Scrypt Hashing Codec - string hashing with scrypt.

scrypt, designed by Colin Percival in 2009 (RFC 7914), is a memory-hard password-based key derivation function whose
 cost is set by three parameters: the CPU/memory cost N (a power of two, given as its base-2 logarithm), the block size
 r and the parallelism p. The result is written in the modular crypt format
 "$scrypt$ln=<log2n>,r=<r>,p=<p>$<salt>$<digest>", with the 16-byte salt and the 32-byte digest encoded in base64
 (without padding). The parameters are given in the codec name (e.g. "scrypt-14" or "scrypt-14-8-2" ; they default to
 ln=16, r=8, p=1) and a random salt is generated each time, hence the output differs between calls. This codec returns
 the hash string (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc7914
"""
import os
from base64 import b64encode

from ..__common__ import *


def _b64(data):
    return b64encode(data).decode().rstrip("=")


def scrypt(ln=None, r=None, p=None):
    ln = int(ln) if ln not in (None, "") else 16
    r = int(r) if r not in (None, "") else 8
    p = int(p) if p not in (None, "") else 1
    if not 1 <= ln <= 31:
        raise LookupError("Bad parameter for encoding 'scrypt': ln must be between 1 and 31")
    if r < 1 or p < 1:
        raise LookupError("Bad parameter for encoding 'scrypt': r and p must be strictly positive")
    def _hash(text, errors="strict"):
        salt, n = os.urandom(16), 1 << ln
        digest = hashlib.scrypt(b(ensure_str(text)), salt=salt, n=n, r=r, p=p, dklen=32, maxmem=128 * r * (n + p + 2))
        return "$scrypt$ln=%d,r=%d,p=%d$%s$%s" % (ln, r, p, _b64(salt), _b64(digest)), len(text)
    return _hash


add("scrypt", scrypt, pattern=r"^scrypt(?:[-_](\d{1,2}))?(?:[-_](\d+))?(?:[-_](\d+))?$", guess=None)
