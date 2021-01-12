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
        'This is a test!':       ";t7C\x84H6T8D\x83e<\xa3eD\x944D\x84I6`",
        'This is another test ': ";t7C\x84H6T8D\x83e<\xa4CDDICt4DseD\x944D\x84I6P",
    },
    'dec(excess-3|xs3)': {
        '\x00':                                            None,
        '\xff':                                            None,
        ';t7C\x84H6T8D\x83e<\xa3eD\x944D\x84I6`':          "This is a test!",
        ';t7C\x84H6T8D\x83e<\xa4CDDICt4DseD\x944D\x84I6P': "This is another test ",
    },
}


CODE = {
    '0': "0011", '1': "0100", '2': "0101", '3': "0110", '4': "0111",
    '5': "1000", '6': "1001", '7': "1010", '8': "1011", '9': "1100",
}


def excess3_encode(text, errors="strict"):
    r, bits = "", ""
    for c in text:
        for i in str(ord(c)).zfill(3):
            bits += CODE[i]
            if len(bits) == 8:
                r += chr(int(bits, 2))
                bits = ""
    if len(bits) > 0:
        r += chr(int(bits + "0000", 2))
    return r, len(b(text))


def excess3_decode(text, errors="strict"):
    code = {v: k for k, v in CODE.items()}
    r, d = "", ""
    for i, c in enumerate(text):
        bin_c = bin(ord(c))[2:].zfill(8)
        for k in range(0, 8, 4):
            hb = bin_c[k:k+4]
            try:
                d += code[hb]
            except KeyError:  # (normal case) occurs when 0000 was used for padding
                if i != len(text) - 1 or k != 4 or hb != "0000":
                    d += handle_error("excess3", errors, decode=True)(hb, i)
            if len(d) == 3:
                r += chr(int(d))
                d = ""
    return r, len(b(text))


add("excess3", excess3_encode, excess3_decode, pattern=r"^(?:excess\-?3|xs\-?3|stibitz)$", entropy=1.,
    printables_rate=.45)

