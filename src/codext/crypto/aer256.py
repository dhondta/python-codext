# -*- coding: UTF-8 -*-
"""AER-256 Codec - AER-256 content encryption.

AER-256 is a toy cipher found on online JavaScript encryption tools. The text is split into blocks of half the key
 length (rounded up), each block being read as a big-endian number of its character codes. For each character of the key
 (at least 3), its code is added to, divides or is subtracted from this number in turn (in floating-point arithmetic),
 and the resulting numbers are written as JavaScript would (e.g. "123.456") and separated by ", ". Decryption applies
 the inverse operations in reverse order and rounds the result. As numbers are double-precision floats, blocks of more
 than 6 characters (i.e. keys of more than 12 characters) lose precision and generally cannot be fully decrypted. Only
 characters with a code below 256 can be encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/AER-256/AER-256.js
"""
from math import floor, isfinite

from ..__common__ import *


__examples__ = {
    'enc(aer256|aer256-ab)':      None,
    'enc(aer256-key|aer-256_key)': {'this is a test': "175.10891089108912, 147.33663366336634, -37.79207920792079, "
                                                      "171.86138613861385, 126.23762376237624, 175.0792079207921, "
                                                      "172.69306930693068"},
    'dec(aer256-key)':            {'175.10891089108912, 147.33663366336634': "this", '175.1, x': None},
    'enc-dec(aer256-key|aer256-secret|aer256-K3y!|aer256-123456789012)': ["", "this is a test", "Hello, World! 123",
                                                                         "\xe9t\xe9 \xff"],
}


def _js_str(x):
    """ Convert a float to a string like JavaScript's Number.prototype.toString. """
    x = float(x)
    if x != x:
        return "NaN"
    if x < 0:
        return "-" + _js_str(-x)
    if x == 0:
        return "0"
    if not isfinite(x):
        return "Infinity"
    # shortest digits that round-trip (as with repr) and decimal exponent n such that x = 0.digits * 10^n
    m, _, e = repr(x).partition("e")
    i, _, f = m.partition(".")
    d = (i + f.rstrip("0")) if f != "0" else i
    n = len(i) + int(e or 0)
    k = len(d.lstrip("0"))
    n -= len(d) - k
    d = d.lstrip("0")
    if k <= n <= 21:
        return d + "0" * (n - k)
    if 0 < n <= 21:
        return d[:n] + "." + d[n:]
    if -6 < n <= 0:
        return "0." + "0" * -n + d
    return d[0] + ("." + d[1:] if k > 1 else "") + "e" + "+-"[n < 1] + str(abs(n - 1))


def __check_key(key):
    key = str(key or "")
    if len(key) < 3:
        raise LookupError("Bad parameter for encoding 'aer256': key must be at least 3 characters long")
    return [ord(c) for c in key], (len(key) + 1) // 2


def aer256_encode(key=None):
    def encode(text, errors="strict"):
        k, n = __check_key(key)
        _h, t = handle_error("aer256", errors), ensure_str(text)
        t = "".join(c for c in "".join(c if ord(c) < 256 else _h(c, i) for i, c in enumerate(t)) if ord(c) < 256)
        r = []
        for i in range(0, len(t), n):
            v = float(int("".join(f"{ord(c):02x}" for c in t[i:i+n]), 16))
            for j, kc in enumerate(k):
                if j % 3 == 0:
                    v += kc
                elif j % 3 == 1:
                    v /= kc
                else:
                    v -= kc
            r.append(_js_str(v))
        return ", ".join(r), len(text)
    return encode


def aer256_decode(key=None):
    def decode(text, errors="strict"):
        k, _ = __check_key(key)
        _h, t, r = handle_error("aer256", errors, decode=True, kind="number"), ensure_str(text), ""
        for i, s in enumerate(t.split(", ") if t else []):
            try:
                v = float(s)
            except ValueError:
                r += _h(s, i)
                continue
            for j in range(len(k) - 1, -1, -1):
                if j % 3 == 0:
                    v -= k[j]
                elif j % 3 == 1:
                    v *= k[j]
                else:
                    v += k[j]
            # Math.round, then the hexadecimal digits of the number (nothing when it is not positive)
            v = floor(v) + (v - floor(v) >= .5) if isfinite(v) else 0
            h = f"{v:x}" if v > 0 else ""
            h = "0" * (len(h) % 2) + h
            r += "".join(chr(int(h[j:j+2], 16)) for j in range(0, len(h), 2))
        return r, len(text)
    return decode


add("aer256", aer256_encode, aer256_decode, r"^aer[-_]?256(?:[-_](\S*))?$", guess=None)
