# -*- coding: UTF-8 -*-
"""Citrix Codec - citrix password encoding.

Citrix CTX1 is the reversible obfuscation used by Citrix products (e.g. in ICA files or the NetScaler configuration) to
 store passwords. Each byte is XORed with 0xA5 and with the previous encoded value, then written as two uppercase
 letters, one per nibble (the nibble added to "A"), hence an expansion factor of 2.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(citrix-ctx0)':                 None,
    'enc(citrix|citrix-1|citrix_ctx1)': {'this is a test': "NBBMNAAGIDEPJJBMNIFNIMEMJKEL"},
}
__guess__ = ["citrix-ctx1"]


_dec = lambda g: ((ord(g[0]) - 0x41) & 0xf) ^ ((((ord(g[1]) - 0x41) & 0xf) << 4) & 0xf0)
_enc = lambda o: chr(((o >> 4) & 0xf) + 0x41) + chr((o & 0xf) + 0x41)


def citrix_encode(t):
    def encode(text, errors="strict"):
        l = len(text)
        r, x = "", 0
        for c in text:
            x = ord(c) ^ 0xa5 ^ x
            r += _enc(x)
        return r, l
    return encode


def citrix_decode(t):
    def decode(text, errors="strict"):
        l = len(text)
        text = text[::-1]
        r = ""
        for i in range(0, l, 2):
            x = 0 if i + 2 >= l else _dec(text[i+2:i+4])
            x ^= _dec(text[i:i+2]) ^ 0xa5
            r += chr(x)
        return r[::-1], l
    return decode


add("citrix", citrix_encode, citrix_decode, r"citrix(|[-_]?(?:ctx)?1)$", entropy=4., printables_rate=1.,
    expansion_factor=2.)

