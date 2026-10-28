# -*- coding: UTF-8 -*-
"""Chuck Norris Unary Codec - Chuck Norris unary content encoding.

Each character is written with the 7 bits of its ASCII code, then the resulting bit string is cut into runs of
 identical bits, each run being written as two blocks of zeros separated by a space: "0" for a run of 1s or "00" for a
 run of 0s, followed by as many zeros as bits in the run.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.codingame.com/training/easy/chuck-norris
"""
from itertools import groupby

from ..__common__ import *


__examples__ = {
    'enc(chuck-norris|chucknorris|chuck_norris_unary|chuck-norris-code)': {'C': "0 0 00 0000 0 00",
                                                                           'CC': "0 0 00 0000 0 000 00 0000 0 00",
                                                                           '%': "00 0 0 0 00 00 0 0 00 0 0 0",
                                                                           'é': None},
    'dec(chuck-norris)': {'0 0 00 0000 0 00': "C", '0 0\n00 0000  0 00': "C", '0 0 00 0000 0': None,
                          '000 0 00 0000 0 00': None, '0 01 00 0000 0 00': None, '0 0 00 0000 0 0': None},
    'enc-dec(chuck-norris)': ["", "\x00", "\x7f", "Hello, World!", "Chuck Norris can divide by zero."],
}
__guess__ = ["chuck-norris"]


def chucknorris_encode(text, errors="strict"):
    _h, bits = handle_error("chuck-norris", errors), ""
    for i, c in enumerate(ensure_str(text)):
        # only ASCII characters can be written with 7 bits ; with the "replace" mode, "?" is encoded instead
        for x in (c if ord(c) < 128 else _h(c, i)):
            bits += f"{ord(x):07b}" if ord(x) < 128 else ""
    return (s := " ".join(["00", "0"][int(b)] + " " + "0" * len(list(g)) for b, g in groupby(bits))), len(s)


def chucknorris_decode(text, errors="strict"):
    _h, blocks, bits, r = handle_error("chuck-norris", errors, decode=True, kind="block"), ensure_str(text).split(), \
                          "", ""
    for i in range(0, len(blocks), 2):
        # a pair of blocks is "0" (bits 1) or "00" (bits 0), followed by as many zeros as bits
        if blocks[i] in ("0", "00") and i + 1 < len(blocks) and set(blocks[i+1]) == {"0"}:
            bits += "10"[len(blocks[i]) - 1] * len(blocks[i+1])
        else:
            _h(" ".join(blocks[i:i+2]), i)
    for i in range(0, len(bits) - 6, 7):
        r += chr(int(bits[i:i+7], 2))
    # the bits must make complete characters
    if len(bits) % 7:
        r += _h(bits[len(bits) - len(bits) % 7:], len(bits) - len(bits) % 7, r)
    return r, len(r)


add("chuck-norris", chucknorris_encode, chucknorris_decode, r"^chuck[-_]?norris(?:[-_](?:unary|code))?$")
