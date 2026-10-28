# -*- coding: UTF-8 -*-
"""Hexagram Codec - hexagram content encoding.

The 64 hexagrams of the I Ching (the Chinese Book of Changes) are figures of 6 broken or unbroken lines, hence they can
 hold 6 bits each. The data is first encoded in Base64, then each Base64 character is replaced by a hexagram (Unicode
 block U+4DC0-U+4DFF), the padding character "=" being replaced by the yin-yang symbol, as implemented by qntm's
 hexagram-encode.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/qntm/hexagram-encode
"""
from ..__common__ import *


__examples__ = {
    'dec(hexagram)':                          {'䷕䷞䷈䷇t': None},
    'enc(hexagram|iching|i-ching-hexagrams)': {'this is a test': "䷰䷭䷚䷔䷞䷺䷗䷔䷞䷺䷗䷚䷏䷊䷂䷕䷞䷈䷇☯"},
}

ENCMAP = {c1: c2 for c1, c2 in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
                                   "䷁䷗䷆䷒䷎䷣䷭䷊䷏䷲䷧䷵䷽䷶䷟䷡䷇䷂䷜䷻䷦䷾䷯䷄䷬䷐䷮䷹䷞䷰䷛䷪䷖䷚䷃䷨䷳䷕"
                                   "䷑䷙䷢䷔䷿䷥䷷䷝䷱䷍䷓䷩䷺䷼䷴䷤䷸䷈䷋䷘䷅䷉䷠䷌䷫䷀☯")}
DECMAP = {c2: c1 for c1, c2 in ENCMAP.items()}


def hexagram_encode(input, errors="strict"):
    return "".join(ENCMAP[c] for c in codecs.encode(input, "base64")), len(input)


def hexagram_decode(input, errors="strict"):
    r, _h = "", handle_error("hexagram", errors, decode=True)
    for i, c in enumerate(input):
        try:
            r += DECMAP[c]
        except KeyError:
            r += _h(c, i, r)
    return (r := codecs.decode(r, "base64")), len(r)


add("hexagram", hexagram_encode, hexagram_decode, printables_rate=0.,
    pattern=r"^(?:(?:i-ching-)?hexagrams?|i-?ching)$")

