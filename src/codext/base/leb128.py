# -*- coding: UTF-8 -*-
"""LEB128 Codec - leb128 (varint) content encoding.

LEB128 (Little Endian Base 128), also known as varint, writes integers with 7 bits per byte, least significant group
 first, the most significant bit of each byte being set except for the last one. The signed variant (SLEB128) writes
 the integers in two's complement, its last byte being sign-extended.

When encoding, the text holds the integers in decimal, separated by whitespaces or commas ; when decoding, the
 integers are separated by a space.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/LEB128
"""
from ..__common__ import *


__examples1__ = {
    'enc(leb128|uleb128|varint|leb-128)': {'0': "\x00", '127': "\x7f", '128': "\x80\x01", '300': "\xac\x02",
                                           '624485': "\xe5\x8e\x26", '1 2, 3': "\x01\x02\x03", '-1': None, 'a': None},
    'dec(leb128)':                        {'\xe5\x8e\x26\xac\x02': "624485 300", '\x80\x00': "0", '\x80': None},
    'enc-dec(leb128)':                    ["", "0", "1 127 128 16383 16384 18446744073709551615"],
}
__examples2__ = {
    'enc(sleb128|leb128-signed|sleb-128)': {'0': "\x00", '-1': "\x7f", '63': "\x3f", '64': "\xc0\x00", '-64': "\x40",
                                            '-65': "\xbf\x7f", '-123456': "\xc0\xbb\x78", '1.5': None},
    'dec(sleb128)':                        {'\xc0\xbb\x78\x7f': "-123456 -1", '\xc0': None},
    'enc-dec(sleb128)':                    ["", "0", "-1 63 64 -64 -65 -123456 9223372036854775807"],
}
__guess1__ = __guess2__ = []


def __leb128(signed=False, decode=False):
    ename = ["leb128", "sleb128"][signed]
    def _code(text, errors="strict"):
        _h, r = handle_error(ename, errors, decode=decode, kind="token" if not decode else "byte"), []
        if decode:
            v, k, start = 0, 0, 0
            for i, x in enumerate(b(text)):
                v, k, start = v | (x & 0x7f) << k, k + 7, start if k else i
                if x < 0x80:
                    # the last byte holds the sign bit (0x40) for the signed variant
                    r.append(str(v - (1 << k) if signed and x & 0x40 else v))
                    v, k = 0, 0
            if k:
                # an incomplete integer (most significant bit set in its last byte) cannot be decoded
                r.append(_h(ensure_str(b(text)[start:]), start, " ".join(r)))
            return (s := " ".join(x for x in r if x != "")), len(s)
        for m in re.finditer(r"[^\s,]+", ensure_str(text)):
            t = m.group()
            if not re.match(r"^[-+]?\d+$", t) or not signed and int(t) < 0:
                r.append(_h(t, m.start()))
            else:
                v, out = int(t), []
                while True:
                    x, v = v & 0x7f, v >> 7
                    # with the signed variant, the encoding stops when the remaining bits are a sign extension
                    if (v == 0 and not (signed and x & 0x40)) or (signed and v == -1 and x & 0x40):
                        out.append(x)
                        break
                    out.append(x | 0x80)
                r.append("".join(map(chr, out)))
        return (s := "".join(r)), len(s)
    return _code


for _n, _s, _p, _ex, _gs in [("leb128", False, r"^(?:u?leb[-_]?128|varint)$", __examples1__, __guess1__),
                             ("sleb128", True, r"^(?:sleb[-_]?128|leb[-_]?128[-_]signed)$", __examples2__, __guess2__)]:
    add(_n, __leb128(_s), __leb128(_s, True), _p, examples=_ex, guess=_gs)
