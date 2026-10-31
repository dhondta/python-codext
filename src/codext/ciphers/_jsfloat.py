# -*- coding: UTF-8 -*-
"""Floating-point block ciphers, shared by the toy ciphers of online JavaScript encryption tools (AER-256, ARMON-64,
 EZIP-64, OKTO3, ZARA-128).

The text is split into blocks of a fraction of the key length (e.g. half of it, rounded), each block being read as a
 big-endian number of its character codes. For each character of the key (at least 3), an operation with its code is
 applied to this number in turn (in floating-point arithmetic, cycling through the operations of the cipher), and the
 resulting numbers are written as JavaScript would (e.g. "123.456") and joined with a separator. Decryption applies the
 inverse operations in reverse order and rounds the result. As numbers are double-precision floats, blocks of more than
 6 characters lose precision and generally cannot be fully decrypted. Only characters with a code below 256 can be
 encrypted, and null characters at the start of a block are lost.
"""
import re
from math import floor, isfinite

from ..__common__ import ensure_str, handle_error


# operations of the ciphers with their inverses, as (encryption, decryption) pairs ; the last one also takes the factor
#  of the cipher (as in JavaScript, the factor and the key code are multiplied first)
OPERATIONS = [
    (lambda v, k, f: v + k, lambda v, k, f: v - k),
    (lambda v, k, f: v / k, lambda v, k, f: v * k),
    (lambda v, k, f: v - k, lambda v, k, f: v + k),
    (lambda v, k, f: v * (f * k), lambda v, k, f: v / (f * k)),
]


def js_str(x):
    """ Convert a float to a string like JavaScript's Number.prototype.toString. """
    x = float(x)
    if x != x:
        return "NaN"
    if x < 0:
        return "-" + js_str(-x)
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


def float_cipher(name, sep, n_ops, divisor=2, factor=.01):
    """ Make the encoding and decoding function factories of a cipher, given its separator, its number of operations,
         the divisor of the key length giving the block size and the factor of its fourth operation. """
    # the separator is not matched inside numbers in exponent notation (e.g. "1e+21")
    split = re.compile(r"(?<![eE])" + re.escape(sep))

    def _key(key):
        key = str(key or "")
        if len(key) < 3:
            raise LookupError(f"Bad parameter for encoding '{name}': key must be at least 3 characters long")
        # block size as given by Math.round(key.length / divisor)
        return [ord(c) for c in key], (2 * len(key) + divisor) // (2 * divisor)

    def encode_factory(key=None):
        def encode(text, errors="strict"):
            k, n = _key(key)
            _h, t = handle_error(name, errors), ensure_str(text)
            t = "".join(c for c in "".join(c if ord(c) < 256 else _h(c, i) for i, c in enumerate(t)) if ord(c) < 256)
            r = []
            for i in range(0, len(t), n):
                v = float(int("".join(f"{ord(c):02x}" for c in t[i:i+n]), 16))
                for j, kc in enumerate(k):
                    v = OPERATIONS[j % n_ops][0](v, kc, factor)
                r.append(js_str(v))
            return sep.join(r), len(text)
        return encode

    def decode_factory(key=None):
        def decode(text, errors="strict"):
            k, _ = _key(key)
            _h, t, r = handle_error(name, errors, decode=True, kind="number"), ensure_str(text), ""
            for i, s in enumerate(split.split(t) if t else []):
                try:
                    v = float(s)
                except ValueError:
                    r += _h(s, i)
                    continue
                for j in range(len(k) - 1, -1, -1):
                    v = OPERATIONS[j % n_ops][1](v, k[j], factor)
                # Math.round, then the hexadecimal digits of the number (nothing when it is not positive)
                v = floor(v) + (v - floor(v) >= .5) if isfinite(v) else 0
                h = f"{v:x}" if v > 0 else ""
                h = "0" * (len(h) % 2) + h
                r += "".join(chr(int(h[j:j+2], 16)) for j in range(0, len(h), 2))
            return r, len(text)
        return decode

    return encode_factory, decode_factory
