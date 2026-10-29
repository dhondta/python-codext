# -*- coding: UTF-8 -*-
"""Base256 Codec - base256 content encoding.

Base256 writes each byte with one character of a set of 256 printable characters: "!", the ASCII characters from "#" to
 "~" (the double quote being excluded), then the Unicode characters from U+00A0 (no-break space) to U+0142 ("ł"). When
 decoding, ASCII whitespace is ignored.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/KvanTTT/BaseNcoding/blob/master/BaseNcoding/Base256.cs
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base256|base-256|base_256)': {'': "", '\x00': "!", '\x01': "#", ']': "\xa0", '\xff': "\u0142",
                                       'Hello': "j\xa8\xaf\xaf\xb2"},
    'dec(base256)':                   {'j\xa8\xaf\xaf\xb2': "Hello", 'j\xa8 \xaf\n\xaf\xb2': "Hello", '"': None,
                                       '\u0143': None},
    'enc-dec(base256)':               ["\xff", "Hello World!", "Caf\xe9 \U0001f600", "@random{512,1024}"],
}
__guess__ = ["base256"]


B256 = "!" + "".join(map(chr, range(0x23, 0x7f))) + "".join(map(chr, range(0xa0, 0x143)))
B256_DEC = {c: i for i, c in enumerate(B256)}


def base256_encode(text, errors="strict"):
    return (s := "".join(B256[x] for x in b(text))), len(s)


def base256_decode(text, errors="strict"):
    _h, r = handle_error("base256", errors, decode=True), bytearray()
    for i, c in enumerate(ensure_str(text)):
        # only ASCII whitespace is ignored, as the no-break space (U+00A0) belongs to the charset
        if c in " \t\r\n":
            continue
        try:
            r.append(B256_DEC[c])
        except KeyError:
            r.extend(b(_h(c, i, bytes(r))))
    return bytes(r), len(r)


add("base256", base256_encode, base256_decode, r"^base[-_]?256$", expansion_factor=1.)
main256 = main(256, "<https://github.com/KvanTTT/BaseNcoding>", inv=False, swap=False)
