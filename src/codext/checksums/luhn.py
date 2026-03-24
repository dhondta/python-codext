# -*- coding: UTF-8 -*-
"""Luhn Codec - Luhn Mod N checksum algorithm.

This is a codec for computing checksums, for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)
"""
from ..__common__ import *


def luhn(n=""):
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:(mod := n if isinstance(n, int) else 10)]
    def encode(data, errors="strict"):
        total, data = 0, "".join(c if c in alphabet else handle_error("luhn", errors, kind="character")(c, i, data) \
                                 for i, c in enumerate(data))
        if not (data := ensure_str(data).upper() if mod > 10 else ensure_str(data)):
            return "", 0
        for i, c in enumerate(reversed(data)):
            code = alphabet.index(c)
            if i % 2 == 0:
                d = code * 2
                code = d % mod + d // mod
            total += code
        check = (mod - total % mod) % mod
        return alphabet[check], len(b(data))
    return encode


add("luhn", luhn, pattern=r"^luhn[-_]?(\d{1,2})?$", guess=None)

