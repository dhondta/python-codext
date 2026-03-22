# -*- coding: UTF-8 -*-
"""Hexagram Codec - hexagram content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(hexagram|iching|i-ching-hexagrams)': {'this is a test': "䷰䷭䷚䷔䷞䷺䷗䷔䷞䷺䷗䷚䷏䷊䷂䷕䷞䷈䷇☯"},
}

ENCMAP = {c1: c2 for c1, c2 in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
                                   "䷁䷗䷆䷒䷎䷣䷭䷊䷏䷲䷧䷵䷽䷶䷟䷡䷇䷂䷜䷻䷦䷾䷯䷄䷬䷐䷮䷹䷞䷰䷛䷪䷖䷚䷃䷨䷳䷕"
                                   "䷑䷙䷢䷔䷿䷥䷷䷝䷱䷍䷓䷩䷺䷼䷴䷤䷸䷈䷋䷘䷅䷉䷠䷌䷫䷀☯")}
DECMAP = {c2: c1 for c1, c2 in ENCMAP.items()}


def hexagram_encode(input, errors="strict"):
    return "".join(ENCMAP[c] for c in codecs.encode(input, "base64")), len(input)


def hexagram_decode(input, errors="strict"):
    r, ehandler = "", handle_error("hexagram", errors, decode=True)
    for i, c in enumerate(input):
        try:
            r += DECMAP[c]
        except KeyError:
            r += ehandler(c, i, r)
    return codecs.decode(r, "base64"), len(input)


add("hexagram", hexagram_encode, hexagram_decode, printables_rate=0.,
    pattern=r"^(?:(?:i-ching-)?hexagrams?|i-?ching)$")

