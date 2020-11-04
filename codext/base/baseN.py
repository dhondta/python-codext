# -*- coding: UTF-8 -*-
"""BaseN Codecs - base content encodings.

These codecs:
- en/decode strings from str to str
- en/decode strings from bytes to bytes
- decode file content to str (read)
- encode file content from str to bytes (write)
"""
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits

from ..__common__ import *
from ._base import base, base_generic
from ._base2n import base2n


B2 = {r'': "01", r'[-_]inv(erted)?': "10"}
base2n(B2, r"^(?:base[-_]?2|bin)(|[-_]inv(?:erted)?|[-_][a-zA-Z0-9]{2})$")


B3 = {r'': "123", r'[-_]inv(erted)?': "321"}
base(B3, r"^base[-_]?3(|[-_]inv(?:erted)?|[-_][a-zA-Z0-9]{3})$")


B4 = {r'': "1234", r'[-_]inv(erted)?': "4321"}
base2n(B4, r"^base[-_]?4(|[-_]inv(?:erted)?|[-_][a-zA-Z0-9]{4})$")


B8 = {r'': "abcdefgh", r'[-_]inv(erted)?': "hgfedcba"}
base2n(B8, r"^base[-_]?8(|[-_]inv(?:erted)?|[-_][a-zA-Z0-9]{8})$")


B16 = {'': digits + "ABCDEF", 'inv': "ABCDEF" + digits}
base2n(B16, r"^(?:base[-_]?16|hex)(|[-_]inv(?:erted)?)$")


B32 = {
    r'':                               upper + "234567",
    r'[-_]inv(erted)?$':               "234567" + upper,
    r'(?:[-_]ext(?:ended)?)?[-_]hex$': digits + upper[:22],
    r'[-_]geohash':                    digits + "bcdefghjkmnpqrstuvwxyz",
}
base2n(B32, r"^base[-_]?32(|[-_]inv(?:erted)?|(?:[-_]ext(?:ended)?)?[-_]hex|[-_]geohash)$")
ZB32 = {'': "ybndrfg8ejkmcpqxot1uwisza345h769"}
base2n(ZB32, r"^z[-_]?base[-_]?32$", name="zbase32")


B36 = {'': digits + upper, 'inv': upper + digits}
base(B36, r"^base[-_]?36(|[-_]inv(?:erted)?)$")


B58 = {
    r'(|[-_](bc|bitcoin))$':              "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
    r'[-_](rp|ripple)$':                  "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz",
    r'[-_](fl|flickr|short[-]?url|url)$': "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
}
base(B58, r"^base[-_]?58(|[-_](bc|bitcoin|rp|ripple|fl|flickr|short[-]?url|url))$")


B62 = {'': digits + upper + lower, 'inv': digits + lower + upper}
base(B62, r"^base[-_]?62(|[-_]inv(?:erted)?)$")


B64 = {
    r'':                        upper + lower + digits + "+/",
    r'[-_]inv(erted)?$':        lower + upper + digits + "+/",
    r'[-_]?(file|url)(safe)?$': upper + lower + digits + "-_",
}
base2n(B64, r"^base[-_]?64(|[-_]inv(?:erted)?|[-_]?(?:file|url)(?:safe)?)$")


# generic base encodings, to be added after all others as they have the precedence
base_generic()

