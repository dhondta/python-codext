# -*- coding: UTF-8 -*-
"""Base45 Codec - base45 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ._base import digits, lower, main, upper
from ..__common__ import *


__examples__ = {
    'enc(base45|base-45|base_45)': {'this is a test!': "AWE+EDH44.OEOCC7WE QEX0"},
    'dec(base45)':                 {'BAD STRING\00': None},
}
__guess__ = ["base45", "base45-inv"]


B45 = {
    '':    digits + upper + " $%*+-./:",
    'inv': upper + digits + " $%*+-./:",
}


__chr = lambda c: chr(c) if isinstance(c, int) else c
__ord = lambda c: ord(c) if not isinstance(c, int) else c


class Base45DecodeError(ValueError):
    pass


def base45_encode(mode):
    mode = mode.replace("inverted", "inv").replace("_", "-").lstrip("-")
    b45 = B45[['inv', ''][mode == ""]]
    def encode(text, errors="strict"):
        t, s = b(text), ""
        for i in range(0, len(text), 2):
            n = 256 * __ord(t[i])
            try:
                n += __ord(t[i+1])
            except IndexError:
                n = __ord(t[i])
                s += b45[n % 45] + b45[n // 45]
                break
            m = n // 45**2
            n -= m * 45**2
            s += b45[n % 45] + b45[n // 45] + b45[m]
        return s, len(text)
    return encode


def base45_decode(mode):
    mode = mode.replace("inverted", "inv").replace("_", "-").lstrip("-")
    b45 = {c: i for i, c in enumerate(B45[['inv', ''][mode == ""]])}
    def decode(text, errors="strict"):
        t, s, err = b(text), "", "'base45' codec can't decode character '%s' in position %d"
        ehandler = handle_error("base45", errors, Base45DecodeError, decode=True)
        for i in range(0, len(text), 3):
            try:
                n = b45[__chr(t[i])]
            except KeyError:
                ehandler(__chr(t[i]), i, s)
            try:
                j = i + 1
                n += 45 * b45[__chr(t[j])]
            except KeyError:
                ehandler(__chr(t[j]), j, s)
            except IndexError:
                ehandler(__chr(t[i]), i, s)
            try:
                k = i + 2
                n += 45 ** 2 * b45[__chr(t[k])]
            except KeyError:
                ehandler(__chr(t[k]), k, s)
            except IndexError:
                s += __chr(n)
                continue
            s += __chr(n // 256) + __chr(n % 256)
        return s, len(text)
    return decode


add("base45", base45_encode, base45_decode, r"^base[-_]?45(|[-_]inv(?:erted)?)$")
main = main(45, "<https://datatracker.ietf.org/doc/html/draft-faltstrom-base45-04.txt>")

