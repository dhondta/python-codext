# -*- coding: UTF-8 -*-
"""Base38 Codec - base38 content encoding.

Base38 is the encoding of the payloads of the Matter (smart home standard) setup QR codes. The data is taken by chunks
 of 3 bytes, each chunk being read as a little-endian integer and written with the least significant digit first, in
 the alphabet "0-9A-Z-.". A chunk of 3 bytes gives 5 characters, a last chunk of 2 bytes gives 4 characters and a last
 chunk of 1 byte gives 2 characters.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/project-chip/connectedhomeip/blob/master/src/setup_payload/Base38Encode.cpp
"""
from ._base import main
from ..__common__ import *


# test vectors from https://github.com/project-chip/connectedhomeip/blob/master/src/setup_payload/tests/TestQRCode.cpp
__examples__ = {
    'enc(base38|base-38|base_38)': {'': "", '\n': "A0", '\n\n': "OT10", '\n\n\n': "-N.B0", '\n\n\x00': "OT100",
                                    '\n\n(': "Y6V91", '\n\n)': "KL0B1", '\n\n\xff': "Q-M08", '#': "Z0",
                                    '\xff\x00': "R600", '.\x00\x00': "81000", '\xff': "R6", '\xff\xff': "NE71",
                                    '\xff\xff\xff': "PLS18",
                                    'Hello World!': "KKHF3W2S013OPM3EJX11"},
    'dec(base38)':                 {'KKHF3W2S013OPM3EJX11': "Hello World!", 'A0': "\n", 'S600': "\x00\x01",
                                    'OE710': "\x00\x00\x01", 'S6': None, 'OE71': None, 'QLS18': None, ' 0': None,
                                    '[0': None, '0\x01': None, 'A': None, 'KKHF3W': None},
    'enc-dec(base38)':             ["\xff", "\xff\xfe", "\xff\xfe\xfd", "\xff\xfe\xfd\xfc", "@random{512,1024}"],
}
__guess__ = ["base38"]


B38, CHUNKS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-.", {1: 2, 2: 4, 3: 5}


def base38_encode(text, errors="strict"):
    t, r = b(text), []
    for i in range(0, len(t), 3):
        v = int.from_bytes(t[i:i+3], "little")
        for _ in range(CHUNKS[len(t[i:i+3])]):
            v, d = divmod(v, 38)
            r.append(B38[d])
    return (s := "".join(r)), len(s)


def base38_decode(text, errors="strict"):
    _h, text, r = handle_error("base38", errors, decode=True), ensure_str(text), b""
    # a wrong character cannot be replaced in a chunk, hence it is dropped
    t = "".join(c if c in B38 else _h(c, i) and "" for i, c in enumerate(text))
    for i in range(0, len(t), 5):
        chunk = t[i:i+5]
        n, v = {2: 1, 4: 2, 5: 3}.get(len(chunk), 0), sum(B38.index(c) * 38 ** k for k, c in enumerate(chunk))
        # a last chunk of 1 or 3 characters cannot be decoded and the value of a chunk must fit in its number of bytes
        r += v.to_bytes(n, "little") if n and v < 256 ** n else b(_h(chunk, i, r))
    return r, len(r)


add("base38", base38_encode, base38_decode, r"^base[-_]?38$", expansion_factor=5 / 3)
main38 = main(38, "<https://github.com/project-chip/connectedhomeip>", inv=False, swap=False)
