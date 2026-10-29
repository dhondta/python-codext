# -*- coding: UTF-8 -*-
"""Base128-Latin1 Codec - base128-latin1 content encoding.

This Base128 encoding, unlike the "base128" codec (relying on the ASCII charset, hence holding control characters), uses
 a set of 128 printable characters (digits, letters and Latin-1 characters). The data is taken by
 chunks of 7 bytes, each chunk being split into 8 groups of 7 bits written with 1 character each ; the bits of a last
 incomplete chunk are split the same way, those of its last group being right-aligned. A last character gives the length
 of the last chunk (0 when it is complete). Whitespace is ignored when decoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/rpuntaie/base128
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base128-latin1|base128_latin1|base-128-latin-1)': {
        '': "0", '\x00' * 7: "000000000", '\xff' * 7: "ÿ" * 8 + "0", '\x01': "011", '\xff': "ÿ11",
        'Hello World!': "aPjÃây·ÕtÚÊÃX15",
    },
    'dec(base128-latin1)': {
        'aPjÃây·ÕtÚÊÃX15': "Hello World!", '011': "\x01", '0': "", '': None, '7': None, '1': None, '01': None,
        '0111': None, '021': None, '01!1': None, '0000000000': None, '0000000001': None,
    },
    'enc-dec(base128-latin1)': ["\xff", "\xff\xfe\xfd\xfc\xfb\xfa", "\xff\xfe\xfd\xfc\xfb\xfa\xf9",
                                "@random{512,1024}"],
}
__guess__ = ["base128-latin1"]


B128 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzµ¶" \
       "·¼½¾ÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖ×ØÙÚÛÜÝÞßáâãäåæçèéêëìíîïñòóôõö÷øùúûüýþÿ"


def base128_latin1_encode(text, errors="strict"):
    t, r = b(text), []
    for i in range(0, len(t), 7):
        chunk = t[i:i+7]
        n, v = 8 * len(chunk), int.from_bytes(chunk, "big")
        # groups of 7 bits from the most significant ones, the last group of an incomplete chunk being right-aligned
        for k in range(n - 7, -7, -7):
            r.append(B128[v >> k & 0x7f if k >= 0 else v & (1 << (k + 7)) - 1])
    r.append(B128[len(t) % 7])
    return (s := "".join(r)), len(s)


def base128_latin1_decode(text, errors="strict"):
    _h, text, r = handle_error("base128-latin1", errors, decode=True), "".join(ensure_str(text).split()), b""
    # a wrong character cannot be replaced in a chunk, hence it is dropped
    t = "".join(c if c in B128 else _h(c, i) and "" for i, c in enumerate(text))
    if len(t) == 0 or (m := B128.index(t[-1])) > 6:
        return b(_h(t[-1:], len(t) - 1)), len(text)
    # the last character gives the length of the last chunk of data (m bytes, encoded with ceil(8m/7) characters)
    t = t[:-1]
    if m and len(t) == 0:
        return b(_h(text, 0)), len(text)
    for i in range(0, len(t), 8):
        chunk, n = t[i:i+8], m if m and i + 8 >= len(t) else 7
        groups = [B128.index(c) for c in chunk]
        # the last group of an incomplete chunk only holds the remaining bits, right-aligned
        rbits = 8 * n - 7 * (len(chunk) - 1)
        if len(chunk) != (8 if n == 7 else -(-8 * m // 7)) or groups[-1] >> rbits:
            r += b(_h(chunk, i, r))
            continue
        v = 0
        for g in groups[:-1]:
            v = v << 7 | g
        r += (v << rbits | groups[-1]).to_bytes(n, "big")
    return r, len(r)


add("base128-latin1", base128_latin1_encode, base128_latin1_decode, r"^base[-_]?128[-_]latin[-_]?1$",
    expansion_factor=8 / 7)
main128latin1 = main(128, "<https://github.com/rpuntaie/base128>", "latin1", inv=False, swap=False)
