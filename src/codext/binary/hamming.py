# -*- coding: UTF-8 -*-
"""Hamming Codec - Hamming(7,4) error-correcting content encoding.

The Hamming(7,4) code, invented by Richard Hamming in 1950, writes 4 data bits (d1 to d4) with 3 parity bits (p1, p2
 and p3), as the codeword p1 p2 d1 p3 d2 d3 d4, where p1 = d1 ^ d2 ^ d4, p2 = d1 ^ d3 ^ d4 and p3 = d2 ^ d3 ^ d4: the
 parity checks of a received codeword (its syndrome) give the position of a flipped bit, hence a single-bit error is
 corrected. The extended Hamming(8,4) code (aka SECDED, for single error correction and double error detection) adds an
 overall parity bit, so that two flipped bits are detected (instead of being wrongly corrected).

Each half of a byte (from the most significant one) is encoded as a codeword in a byte (whose most significant bit is
 the overall parity bit with Hamming(8,4), and 0 with Hamming(7,4)), hence each input byte gives two output bytes.
 Decoding silently corrects the single-bit errors ; with Hamming(8,4), the double-bit errors are reported (or, with a
 non-strict errors handling, replaced, dropped or left as is), as well as a trailing byte.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Hamming(7,4)
"""
from ..__common__ import *


__examples1__ = {
    'enc(hamming|hamming74|hamming-7-4|hamming_7_4)': {'\xb3': "3C", 'A': "Li", '\x00\xff': "\x00\x00\x7f\x7f"},
    'dec(hamming)': {'3C': "\xb3", '\x13C': "\xb3", '3B': "\xb3", '\xb3C': "\xb3", '3': None},
    'enc-dec(hamming)': ["", "@random{512}"],
}
__examples2__ = {
    'enc(hamming84|hamming-8-4|secded)': {'\xb3': "3\xc3", 'A': "\xcci", '\x00\xff': "\x00\x00\xff\xff"},
    'dec(hamming84)': {'3\xc3': "\xb3", '\x13\xc3': "\xb3", '\xb3\xc3': "\xb3", '\x03\xc3': None, '3': None},
    'enc-dec(hamming84)': ["", "@random{512}"],
}


def _codeword(nibble, extended):
    d1, d2, d3, d4 = (nibble >> 3) & 1, (nibble >> 2) & 1, (nibble >> 1) & 1, nibble & 1
    c = (d1 ^ d2 ^ d4) << 6 | (d1 ^ d3 ^ d4) << 5 | d1 << 4 | (d2 ^ d3 ^ d4) << 3 | d2 << 2 | d3 << 1 | d4
    # the overall parity bit (Hamming(8,4)) is the most significant bit of the byte
    return c | (bin(c).count("1") & 1) << 7 if extended else c


def _decoding(extended):
    """ Table of the decoded nibbles of the bytes, None for the uncorrectable errors. """
    table = []
    for byte in range(256):
        c = byte & 0x7f
        bits = [c >> (6 - i) & 1 for i in range(7)]
        # the syndrome is the position (from 1) of the flipped bit, 0 if none
        s = (bits[0] ^ bits[2] ^ bits[4] ^ bits[6]) | (bits[1] ^ bits[2] ^ bits[5] ^ bits[6]) << 1 | \
            (bits[3] ^ bits[4] ^ bits[5] ^ bits[6]) << 2
        # with the overall parity, an even number of flipped bits with a non-null syndrome is a double-bit error
        if extended and s and not bin(byte).count("1") & 1:
            table.append(None)
            continue
        if s:
            bits[s - 1] ^= 1
        table.append(bits[2] << 3 | bits[4] << 2 | bits[5] << 1 | bits[6])
    return table


def hamming_encode(extended):
    codewords = [_codeword(n, extended) for n in range(16)]
    def encode(text, errors="strict"):
        return bytes(codewords[x >> i & 15] for x in b(ensure_str(text)) for i in (4, 0)).decode("latin-1"), len(text)
    return encode


def hamming_decode(extended):
    ename, table = "hamming84" if extended else "hamming", _decoding(extended)
    def decode(text, errors="strict"):
        _h, data, r = handle_error(ename, errors, decode=True, kind="codewords"), b(ensure_str(text)), ""
        # a trailing byte is reported first, then (with a non-strict errors handling) replaced, dropped or left as is
        #  at the end
        trailing = _h(data[-1:].decode("latin-1"), len(data) - 1, r) if len(data) % 2 else ""
        for i in range(0, len(data) - 1, 2):
            hi, lo = table[data[i]], table[data[i+1]]
            r += _h(data[i:i+2].decode("latin-1"), i, r) if hi is None or lo is None else chr(hi << 4 | lo)
        return (r + trailing).encode("latin-1"), len(text)
    return decode


add("hamming", hamming_encode(False), hamming_decode(False), r"^hamming(?:[-_]?7[-_]?4)?$", examples=__examples1__)
add("hamming84", hamming_encode(True), hamming_decode(True), r"^(?:hamming[-_]?8[-_]?4|secded)$",
    examples=__examples2__)
