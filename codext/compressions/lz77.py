# -*- coding: UTF-8 -*-
"""LZ77 Codec - Lempel-Ziv 1977 compression algorithm.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Inspired from: https://github.com/manassra/LZ77-Compressor
"""
from ..__common__ import *


__examples__ = {'enc-dec(lz77)': ["test", "This is a test", "@random{512,1024,2048}"]}


_B2b = lambda B: bin(B if isinstance(B, int) else ord(B))[2:].zfill(8)
_b2B = lambda bt: "".join(chr(int(bt[i:i+8], 2)) for i in range(0, len(bt), 8))
WINDOW_SIZE = 20


def _find_longest_match(data, pos):
    """ Finds the longest match to a substring starting at the current position (pos) in the lookahead buffer from
         the history window. """
    eob, bmd, bml = min(pos + 15, len(data) + 1), -1, -1
    for j in range(pos + 2, eob):
        start = max(0, pos - WINDOW_SIZE)
        substr = data[pos:j]
        l = len(substr)
        for i in range(start, pos):
            n, r = l // (pos - i), l % (pos - i)
            if data[i:pos] * n + data[i:i+r] == substr and l > bml:
                bmd, bml = pos - i, l
    if bmd > 0 and bml > 0:
        return bmd, bml


def lz77_compress(input, errors="strict"):
    """ Compresses the given data by applying LZ77 compression algorithm. """
    i, l, bits = 0, len(input), ""
    while i < l:
        try:
            bmd, bml = _find_longest_match(input, i)
            bits += "1" + _B2b(bmd >> 4) + _B2b(((bmd & 0xf) << 4) | bml)
            i += bml
        except TypeError:
            bits += "0" + _B2b(input[i])
            i += 1
    bits += "0" * ((8 - (len(bits) % 8)) % 8)
    return _b2B(bits), l


def lz77_decompress(input, errors="strict"):
    """ Decompresses the given data. """
    out, d = "", "".join(_B2b(c) for c in input)
    while len(d) >= 9:
        flag, d = d[0], d[1:]
        if flag == "0":
            out += _b2B(d[:8])
            d = d[8:]
        else:
            B1, B2 = int(d[:8], 2), int(d[8:16], 2)
            d = d[16:]
            dist = (B1 << 4) | (B2 >> 4)
            for i in range(B2 & 0xf):
                out += out[-dist]
    return out, len(out)


add("lz77", lz77_compress, lz77_decompress, entropy=7.9)

