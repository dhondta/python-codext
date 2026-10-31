# -*- coding: UTF-8 -*-
"""HMAC Hashing Codec - string hashing with keyed-hash message authentication codes.

HMAC (RFC 2104) computes a message authentication code from a hash function and a secret key, as the hash of the key
 (padded to the block size and XORed with 0x5c) followed by the hash of the key (XORed with 0x36) and the message. The
 hash function and the key (as text, encoded in UTF-8, possibly empty) are given in the codec name (e.g.
 "hmac-sha256-secret"), among the hash functions guaranteed by hashlib (MD5, SHA-1, SHA-2, SHA-3 and BLAKE2). This codec
 returns the hexadecimal digest (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc2104
"""
import hmac as _hmac

from ..__common__ import *


def hmac_hash(algo, key=None):
    # the key is taken as is (a key made of digits being given as an integer by the pattern)
    k, h = str(key or "").encode(), algo.replace("-", "_")
    def _hash(text, errors="strict"):
        return _hmac.new(k, b(text), h).hexdigest(), len(text)
    return _hash


add("hmac", hmac_hash, pattern=r"^hmac[-_](md5|sha1|sha224|sha256|sha384|sha512|sha3[-_](?:224|256|384|512)|blake2[bs])"
    r"(?:[-_](.*))?$", guess=None)
