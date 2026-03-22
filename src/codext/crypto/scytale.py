# -*- coding: UTF-8 -*-
"""Scytale-N Codec - scytale content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from math import ceil

from ..__common__ import *


__examples__ = {
    'enc(scytale0|scytale--10|scytale01)': None,
    'enc(scytale2|scytale-2|scytale_2)':   {'this is a test': "ti satshsi  et"},
    'enc(scytale5|scytale-5|scytale_5)':   {'this is a test': "tithsei ssat  "},
}
__guess__ = ["scytale-%d" % i for i in range(1, 10)]


PADDING_CHAR = ""


def scytale_encode(l):
    def encode(text, errors="strict"):
        s, n = "", int(ceil(len(text) / float(l)))
        for x in range(l):
            for y in range(n):
                try:
                    s += text[y*l+x]
                except IndexError:
                    s += PADDING_CHAR
        return s, len(s)
    return encode


def scytale_decode(l):
    def decode(text, errors="strict"):
        s, n = "", int(ceil(len(text) / float(l)))
        pl = l * n - len(text)
        for x in range(n):
            for y in range(l):
                if y >= l-pl and x == n-1:
                    continue
                s += text[y*n+x-max(0,y-(l-pl))]
        s = s.rstrip(PADDING_CHAR)
        return s, len(s)
    return decode


add("scytale", scytale_encode, scytale_decode, r"^scytale[-_]?([1-9]\d*)$")

