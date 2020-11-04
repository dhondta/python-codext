# -*- coding: UTF-8 -*-
"""Base91 Codec - base91 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits

from ..__common__ import *

# no __examples__ ; handled manually in tests/test_base.py
__guess__    = ["base91", "base91-inv"]


B91 = {
    '':    upper + lower + digits + "!#$%&()*+,./:;<=>?@[]^_`{|}~\"",
    'inv': lower + upper + digits + "!#$%&()*+,./:;<=>?@[]^_`{|}~\"",
}


__chr = lambda c: chr(c) if isinstance(c, int) else c
__ord = lambda c: ord(c) if not isinstance(c, int) else c


class Base91DecodeError(ValueError):
    pass

    
def base91_encode(mode):
    b91 = B91[["inv", ""][mode == ""]]
    def encode(text, errors="strict"):
        t = b(text)
        s = ""
        bits = ""
        for c in t:
            bits = bin(__ord(c))[2:].zfill(8) + bits
            if len(bits) > 13:
                n = int(bits[-13:], 2)
                if n > 88:
                    bits = bits[:-13]
                else:
                    n = int(bits[-14:], 2)
                    bits = bits[:-14]
                s += b91[n % 91] + b91[n // 91]
        if len(bits) > 0:
            n = int(bits, 2)
            s += b91[n % 91]
            if len(bits) > 7 or n > 90:
                s += b91[n // 91]
        return s, len(t)
    return encode


def base91_decode(mode):
    b91 = {c: i for i, c in enumerate(B91[["inv", ""][mode == ""]])}
    def decode(text, errors="strict"):
        t = b(text)
        s = ""
        bits = ""
        for i in range(0, len(t), 2):
            try:
                n = b91[__chr(t[i])]
            except KeyError:
                raise Base91DecodeError("'base91' codec can't decode character '%s' in position %d" % (__chr(t[i]), i))
            try:
                j = i + 1
                n += b91[__chr(t[j])] * 91
            except IndexError:
                pass
            except KeyError:
                raise Base91DecodeError("'base91' codec can't decode character '%s' in position %d" % (__chr(t[j]), j))
            bits = bin(n)[2:].zfill([14, 13][n & 8191 > 88]) + bits
            while len(bits) > 8:
                s += chr(int(bits[-8:], 2))
                bits = bits[:-8]
        if len(bits) > 0 and not set(bits) == {"0"}:
            s += chr(int(bits, 2))
        return s, len(t)
    return decode


add("base91", base91_encode, base91_decode, r"^base[-_]?91(|[-_]inv(?:erted)?)$")

