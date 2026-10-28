# -*- coding: UTF-8 -*-
"""Run-Length Encoding Codec - RLE compression algorithm.

NB: Not an encoding properly speaking.

Each run of identical consecutive characters is replaced by its length followed by the character. Three variants are
 supported:
- textual (default): the length is written in decimal before the character (e.g. "AAAB" gives "3A1B") ; digits cannot
   be encoded, as they would be confused with the lengths
- compact: same as textual, except that a length of 1 is omitted (e.g. "AAAB" gives "3AB")
- suffix: the length is written after the character instead (e.g. "AAAB" gives "A3B1", or "A3B" if also compact)
- bytes: the length is written as a single character (code point 1 to 255) before the character, longer runs being
   split ; this variant can encode any input
- escape: single characters are kept as is, while a run is written as the character twice followed by the number of
   extra repeats as a single character (code point 0 to 255, e.g. "AAAAAB" gives "AA\x03B"), longer runs being split ;
   this variant can encode any input and does not expand text without repeats

When decoding the textual variants, a character without length is taken once, so that both forms are decoded.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Run-length_encoding
"""
import re
from itertools import groupby
from string import digits as DG

from ..__common__ import *


__examples__ = {
    'enc(rle|run-length|runlength|run_length_encoding)': {
        'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW': "12W1B12W3B24W1B14W"},
    'enc(rle-compact)':  {'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW': "12WB12W3B24WB14W"},
    'enc(rle)':          {'Room 101': None},
    'dec(rle)':          {'12WB3!': "WWWWWWWWWWWWB!!!", '3A0B': None, '3A2': None},
    'enc(rle-suffix|run-length-suffix)': {'AAABB C': "A3B2 1C1"},
    'enc(rle-compact-suffix)': {'AAABB C': "A3B2 C"},
    'dec(rle-suffix)':   {'W12B!3': "WWWWWWWWWWWWB!!!", 'A3B0': None, '2A3': None},
    'enc(rle-bytes)':    {'AAAB': "\x03A\x01B"},
    'dec(rle-bytes)':    {'\x03': None, '\x00A': None},
    'enc-dec(rle|rle-compact|rle-suffix|rle-compact-suffix)': ["", "AAAB", "Hello, World!", "  spaced   out  "],
    'enc(rle-escape|run-length-escape)': {'AAAAAB': "AA\x03B", 'AB': "AB", 'AABBB': "AA\x00BB\x01"},
    'dec(rle-escape)':   {'AA': None, 'AB\u0100': "AB\u0100", 'AA\u0100': None},
    'enc-dec(rle-bytes|rle-escape)': ["", "A" * 300, "A" * 514, "A" * 515, "Room 101", "@random"],
}


def rle_encode(binary=None, compact=None, suffix=None):
    def encode(text, errors="strict"):
        text, r = ensure_str(text), []
        if binary == "bytes":
            for c, run in groupby(text):
                n = len(list(run))
                # a length cannot exceed 255 in a single character ; longer runs are split
                r += [chr(255) + c] * (n // 255) + ([chr(n % 255) + c] if n % 255 else [])
        elif binary == "escape":
            for c, run in groupby(text):
                n = len(list(run))
                # a pair holds at most 2 + 255 characters ; longer runs are split, a remaining single character being
                #  kept as is
                r += [2 * c + chr(255)] * (n // 257) + ([] if (m := n % 257) == 0 else [c] if m == 1 else
                                                        [2 * c + chr(m - 2)])
        else:
            # digits would be confused with the lengths, hence they are handled as errors
            _h = handle_error("rle", errors)
            text = "".join(_h(c, i) if c in DG else c for i, c in enumerate(text))
            for c, run in groupby(text):
                n = len(list(run))
                n = "" if n == 1 and compact else str(n)
                r.append(c + n if suffix else n + c)
        return (s := "".join(r)), len(s)
    return encode


def rle_decode(binary=None, compact=None, suffix=None):
    # a character without length is taken once, so that the compact variants are decoded too ; digits that cannot be
    #  bound to a character (trailing ones with lengths first, leading ones with lengths last) are matched separately
    token = re.compile(r"([^0-9])([0-9]*)|([0-9]+)" if suffix else r"([0-9]*)([^0-9])|([0-9]+)")
    def decode(text, errors="strict"):
        text, r, _h = ensure_str(text), "", handle_error("rle", errors, decode=True)
        if binary == "bytes":
            for i in range(0, len(text), 2):
                if len(pair := text[i:i+2]) < 2 or not 0 < ord(pair[0]) < 256:
                    r += _h(pair, i, r)
                else:
                    r += pair[1] * ord(pair[0])
        elif binary == "escape":
            i = 0
            while i < len(text):
                if text[i+1:i+2] != text[i]:
                    r, i = r + text[i], i + 1
                    continue
                # a repeated character is followed by the number of extra repeats
                if len(run := text[i:i+3]) < 3 or ord(run[2]) > 255:
                    r += _h(run, i, r)
                else:
                    r += run[0] * (2 + ord(run[2]))
                i += 3
        else:
            for m in token.finditer(text):
                c, n = m.group(1, 2) if suffix else m.group(2, 1)
                if m.group(3) or n and int(n) == 0:
                    r += _h(m.group(), m.start(), r)
                else:
                    r += c * int(n or 1)
        return r, len(r)
    return decode


add("rle", rle_encode, rle_decode,
    r"^(?:rle|run[-_]?length(?:[-_]encoding)?)(?:[-_](bytes|escape)|(?:[-_](compact))?(?:[-_](suffix))?)$")
