# -*- coding: UTF-8 -*-
"""NRZI Codec - Non-Return-to-Zero Inverted content encoding.

Non-Return-to-Zero Inverted (NRZI) is a line code where each bit gives the level of the signal during its period, a bit
 being written as a change of the level (a transition) or as no change. By default, the convention NRZ-M ("mark") is
 used: 1 is written with a transition and 0 without, while the "-space" variant uses the convention NRZ-S, where 0 is
 written with a transition and 1 without (as used e.g. by USB and HDLC, before their bit stuffing). The level starts low
 and the bits are taken from the most significant one, the levels being packed in bytes ; each input byte thus gives an
 output byte.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Non-return-to-zero#NRZI
"""
from ..__common__ import *


__examples1__ = {
    'enc(nrzi|nrz-i|nrz-m|nrzi-mark)': {'\x00\xff\x0f': "\x00\xaa\n", 'A': "~", '\xb2': "\xdc"},
    'enc-dec(nrzi)': ["", "@random{512}"],
}
__examples2__ = {
    'enc(nrzi-space|nrz-s)': {'\x00\xff\x0f': "\xaa\x00\xa0", 'A': "\xd4", '\xb2': "v"},
    'enc-dec(nrzi-space)': ["", "@random{512}"],
}


def _nrzi(transition, decode=False):
    """ Encoding or decoding function, given the bit written with a transition. """
    def _code(text, errors="strict"):
        level, r = 0, []
        for x in b(ensure_str(text)):
            y = 0
            for i in range(7, -1, -1):
                bit = x >> i & 1
                if decode:
                    y, level = y << 1 | (bit != level) ^ (not transition), bit
                else:
                    level ^= bit == transition
                    y = y << 1 | level
            r.append(y)
        return bytes(r).decode("latin-1"), len(text)
    return _code


add("nrzi", _nrzi(1), _nrzi(1, True), r"^nrz[-_]?(?:i(?:[-_]mark)?|m)$", examples=__examples1__)
add("nrzi-space", _nrzi(0), _nrzi(0, True), r"^nrz[-_]?(?:i[-_]space|s)$", examples=__examples2__)
