# -*- coding: UTF-8 -*-
"""Cisco Type 7 Codec - Cisco type 7 password encoding.

Cisco type 7 is the reversible obfuscation used by Cisco IOS to store passwords in the device configuration (with
 "service password-encryption"). Each byte is XORed with a byte of a fixed key, starting at an offset (the salt, from 0
 to 15) and wrapping around the key ; the result is the salt as two decimal digits followed by the XORed bytes in
 uppercase hexadecimal. The salt can be given with the codec name (e.g. "cisco-type7-8") and defaults to 0 ; decoding
 reads it from the input.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/theevilbit/ciscot7
"""
from string import hexdigits

from ..__common__ import *


__examples__ = {
    'enc(cisco-type7-16|cisco7-99)':                 None,
    'enc(cisco-type7-8|cisco7_8|cisco_type_7-08)':   {'cisco': "0822455D0A16"},
    'enc(cisco-type7|type7)':                        {'this is a test': "00101B0F171B02154F200C5A0C0A11"},
    'dec(cisco-type7)':                              {'0822455D0A16': "cisco", '0822455d0a16': "cisco",
                                                      '082': None, '0822455D0A1G': None, '5322455D0A16': None},
    'enc-dec(cisco-type7|cisco-type7-1|cisco-type7-15)': ["", "cisco", "This is a test !"],
}
__guess__ = ["cisco-type7"]


KEY = b"dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87"


def cisco7_encode(salt=None):
    salt = int(salt or 0)
    if salt > 15:
        raise LookupError("Bad parameter for encoding 'cisco-type7': salt must be from 0 to 15")
    def encode(text, errors="strict"):
        t = b(text)
        r = "%02d" % salt + "".join("%02X" % (c ^ KEY[(salt + i) % len(KEY)]) for i, c in enumerate(t))
        return r, len(t)
    return encode


def cisco7_decode(salt=None):
    def decode(text, errors="strict"):
        t, _h = ensure_str(text), handle_error("cisco-type7", errors, decode=True)
        if len(t) % 2 or not t[:2].isdigit() or int(t[:2]) >= len(KEY):
            return _h(t[:2], 0), len(t)
        r, s = b"", int(t[:2])
        for i in range(2, len(t), 2):
            g = t[i:i+2]
            if all(c in hexdigits for c in g):
                r += bytes([int(g, 16) ^ KEY[(s + i // 2 - 1) % len(KEY)]])
            else:
                r += b(_h(g, i))
        return r, len(t)
    return decode


add("cisco-type7", cisco7_encode, cisco7_decode, r"^(?:cisco[-_]?(?:type[-_]?)?|type[-_]?)7(?:[-_](\d{1,2}))?$",
    entropy=4., printables_rate=1., expansion_factor=2.)
