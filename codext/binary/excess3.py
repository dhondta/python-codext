# -*- coding: UTF-8 -*-
"""Excess-3 Codec - Excess-3 code (aka Stibitz code) content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {'enc(excess3|xs-3|stibitz)': {'This is a test': ";t7C\x84H6T8D\x83e<£eD\x944D\x84I"}}


CODE = {
    '0': "0011", '1': "0100", '2': "0101", '3': "0110", '4': "0111",
    '5': "1000", '6': "1001", '7': "1010", '8': "1011", '9': "1100",
}


def excess3_encode(text, errors="strict"):
    r, b = "", ""
    for c in text:
        for i in str(ord(c)).zfill(3):
            b += CODE[i]
            if len(b) == 8:
                r += chr(int(b, 2))
                b = ""
    if len(b) > 0:
        b += "0000"
        r += chr(int(b, 2))
    return r, len(text)


def excess3_decode(text, errors="strict"):
    code = {v: k for k, v in CODE}
    r, d = "", ""
    for c in text:
        b = bin(ord(c))[2:].zfill(8)
        for i in range(0, 8, 4):
            d += code[b[i:i+4]]
            if len(d) == 3:
                r += chr(int(d))
                d = ""
    if len(d) > 0:
        r += chr(int(d))
    return r, len(text)


add("excess3", excess3_encode, excess3_decode, pattern=r"^(?:excess\-3|xs\-?3|stibitz)$")

