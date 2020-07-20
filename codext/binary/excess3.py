# -*- coding: UTF-8 -*-
"""Excess-3 Codec - Excess-3 code (aka Stibitz code) content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(excess3|xs-3|stibitz)': {
        'This is a test!': ";t7C\x84H6T8D\x83e<\xa3eD\x944D\x84I6`",
        'This is another test ': ";t7C\x84H6T8D\x83e<\xa4CDDICt4DseD\x944D\x84I6P",
    },
}


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
        r += chr(int(b + "0000", 2))
    return r, len(text)


def excess3_decode(text, errors="strict"):
    code = {v: k for k, v in CODE.items()}
    r, d = "", ""
    for c in text:
        bin_c = bin(ord(c))[2:].zfill(8)
        for i in range(0, 8, 4):
            try:
                d += code[bin_c[i:i+4]]
            except KeyError:  # (normal case) occurs when 0000 was used for padding
                break
            if len(d) == 3:
                r += chr(int(d))
                d = ""
    return r, len(b(text))


add("excess3", excess3_encode, excess3_decode, pattern=r"^(?:excess\-?3|xs\-?3|stibitz)$", text=False)

