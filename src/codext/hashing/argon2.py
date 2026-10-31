# -*- coding: UTF-8 -*-
"""Argon2 Hashing Codec - string hashing with Argon2.

Argon2, the winner of the Password Hashing Competition in 2015 (RFC 9106), is a memory-hard password hashing function
 with three variants: Argon2d (data-dependent, resistant to GPU attacks), Argon2i (data-independent, resistant to
 side-channel attacks) and Argon2id (a hybrid, recommended by default). The result is written in the modular crypt
 format "$argon2<variant>$v=19$m=<memory>,t=<time>,p=<parallelism>$<salt>$<digest>". The variant is given in the codec
 name (e.g. "argon2i" ; it defaults to Argon2id) and a random salt is generated each time, hence the output differs
 between calls. This codec relies on the argon2-cffi package ("argon2" extra) and is not available without it. It
 returns the hash string (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc9106
"""
from os import urandom

from ..__common__ import *

try:
    from argon2.low_level import hash_secret, Type
except ImportError:
    hash_secret = None


# default cost parameters (the "low memory" profile of RFC 9106: 64 MiB, 3 passes, 4 lanes)
_PARAMS = dict(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32)
_TYPES = {"d": "D", "i": "I", "id": "ID", "": "ID"}


def argon2(variant=None):
    t = getattr(Type, _TYPES[(variant or "").lower()])
    def _hash(text, errors="strict"):
        return hash_secret(b(ensure_str(text)), urandom(16), type=t, **_PARAMS).decode(), len(text)
    return _hash


if hash_secret is not None:
    add("argon2", argon2, pattern=r"^argon2(id|i|d)?$", guess=None)
