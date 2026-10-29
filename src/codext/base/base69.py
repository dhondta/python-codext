# -*- coding: UTF-8 -*-
"""Base69 Codec - base69 content encoding.

Base69, designed by Preet Shihn, is a Base64-like encoding with a set of 69 characters. The data is taken by chunks of
 7 bytes (the last one being padded with null bytes), each chunk being split into 8 groups of 7 bits ; each group is
 written with 2 characters, its value modulo 69 then its value divided by 69. When the data was padded, the last 2
 characters are replaced by the number of padding bytes followed by "=". Whitespace is ignored when decoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/pshihn/base69
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base69|base-69|base_69)': {'': "", '\x00' * 7: "A" * 16, '\xff' * 7: "6B" * 8, '\x01': "AA-AAAAAAAAAAA6=",
                                    'Hello World!': "kAZAtABBeB8A-ASB3AXBIBBBhAEAAA2="},
    'dec(base69)':                 {'kAZAtABBeB8A-ASB3AXBIBBBhAEAAA2=': "Hello World!",
                                    'kAZAtABBeB8A-AS\nB3AXBIBBBhAEAAA2=': "Hello World!", 'AA-AAAAAAAAAAA6=': "\x01",
                                    'AA-AAAAAAAAAAA7=': None, 'AA-AAAAAAAAAAA0=': None, 'AA-AAAAAAAAAAAA=': None,
                                    'AA-AAAAAAAAAAA': None, '6C' * 8: None, '!' + "A" * 16: None},
    'enc-dec(base69)':             ["\xff", "\xff\xfe\xfd\xfc\xfb\xfa", "\xff\xfe\xfd\xfc\xfb\xfa\xf9",
                                    "@random{512,1024}"],
}
__guess__ = ["base69"]


B69 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-*<>|"


def base69_encode(text, errors="strict"):
    t, r = b(text), []
    pad = -len(t) % 7
    t += b"\x00" * pad
    for i in range(0, len(t), 7):
        v = int.from_bytes(t[i:i+7], "big")
        for k in range(49, -1, -7):
            q, m = divmod(v >> k & 0x7f, 69)
            r.append(B69[m] + B69[q])
    if pad:
        # the last group only holds bits of a padding byte, hence it can be replaced by the number of padding bytes
        r[-1] = f"{pad}="
    return (s := "".join(r)), len(s)


def base69_decode(text, errors="strict"):
    _h, text, r = handle_error("base69", errors, decode=True), "".join(ensure_str(text).split()), b""
    # the number of padding bytes, then the characters of the chunks ; a wrong character cannot be replaced in a chunk,
    #  hence it is dropped
    pad, t = 0, text
    if text.endswith("="):
        pad = int(text[-2]) if len(text) >= 16 and text[-2] in "123456" else _h(text[-2:], len(text) - 2) and 0
        t = text[:-2] + "AA"
    t = "".join(c if c in B69 else _h(c, i) and "" for i, c in enumerate(t))
    for i in range(0, len(t), 16):
        chunk = t[i:i+16]
        groups = [B69.index(chunk[j]) + 69 * B69.index(chunk[j+1]) for j in range(0, len(chunk) - 1, 2)]
        # a chunk must hold 8 groups of 7 bits
        if len(groups) != 8 or any(g > 0x7f for g in groups):
            r += b(_h(chunk, i, r))
            continue
        r += sum(g << (49 - 7 * k) for k, g in enumerate(groups)).to_bytes(7, "big")
    return r[:len(r) - pad], len(r)


add("base69", base69_encode, base69_decode, r"^base[-_]?69$", expansion_factor=16 / 7, padding_char="=")
main69 = main(69, "<https://github.com/pshihn/base69>", inv=False, swap=False)
