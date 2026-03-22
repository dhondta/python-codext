# -*- coding: UTF-8 -*-
"""Luhn Codec - Luhn Mod N checksum algorithm.

The Luhn algorithm, also known as the "modulus 10" algorithm, is a simple checksum
formula used to validate identification numbers (e.g. credit card numbers, IMEI
numbers). Encoding appends a check character; decoding verifies the check character
and strips it.

The Luhn Mod N generalization extends the algorithm to alphabets of arbitrary size N.
When called as 'luhn' or 'luhn-10', the standard decimal alphabet (0-9, N=10) is
used. When called as 'luhn-<N>' for 2 ≤ N ≤ 36, the first N characters of
'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' form the alphabet.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Luhn_algorithm
          https://bitcoinwiki.org/wiki/luhn-mod-n-algorithm
"""
from ..__common__ import *


__examples__ = {
    'enc(luhn|luhn-10|luhn10)': {
        '7992739871': '79927398713',
        '':           '',
        '0':          '00',
        '1':          '18',
    },
    'dec(luhn|luhn-10|luhn10)': {
        '79927398713': '7992739871',
        '':            '',
        '00':          '0',
        '18':          '1',
    },
    'enc-dec(luhn)':    ['123456789', '0' * 10, '9999999999999999'],
    'enc-dec(luhn-16)': ['0123456789ABCDEF', 'DEADBEEF'],
    'enc-dec(luhn-36)': ['HELLO', 'WORLD123'],
}

_FULL_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _luhn_encode(n=""):
    mod = n if isinstance(n, int) else 10
    alphabet = _FULL_ALPHABET[:mod]

    def _encode(text, errors="strict"):
        text = ensure_str(text).upper() if mod > 10 else ensure_str(text)
        if not text:
            return "", 0
        for pos, c in enumerate(text):
            if c not in alphabet:
                handle_error("luhn", errors, kind="character")(c, pos, text)
        total = 0
        for i, c in enumerate(reversed(text)):
            code = alphabet.index(c)
            if i % 2 == 0:
                d = code * 2
                code = d % mod + d // mod
            total += code
        check = (mod - total % mod) % mod
        return text + alphabet[check], len(b(text))

    return _encode


def _luhn_decode(n=""):
    mod = n if isinstance(n, int) else 10
    alphabet = _FULL_ALPHABET[:mod]

    def _decode(text, errors="strict"):
        text = ensure_str(text).upper() if mod > 10 else ensure_str(text)
        if not text:
            return "", 0
        for pos, c in enumerate(text):
            if c not in alphabet:
                handle_error("luhn", errors, decode=True, kind="character")(c, pos, text)
        total = 0
        for i, c in enumerate(reversed(text)):
            code = alphabet.index(c)
            if i % 2 == 1:
                d = code * 2
                code = d % mod + d // mod
            total += code
        if total % mod != 0:
            handle_error("luhn", errors, decode=True)(text[-1], len(text) - 1, text[:-1])
        return text[:-1], len(b(text))

    return _decode


add("luhn", _luhn_encode, _luhn_decode, pattern=r"^luhn[-_]?(\d{1,2})?$", guess=None)
