# -*- coding: UTF-8 -*-
"""BaseXX Codecs - base16/32/64/85/100 content encodings.

Notes:
- base64:  compared to the original base64_codec (available in the built-in
           encodings), it allows to en/decode from str for avoiding the annoying
           TypeError exception in Python3
- base100: strongly inspired from https://github.com/MasterGroosha/pybase100

These codecs:
- en/decode strings from str to str
- en/decode strings from bytes to bytes
- decode file content to str (read)
- encode file content from str to bytes (write)
"""
import base64

from .__common__ import *

# BASE16
def base16_encode(input, errors='strict'):
    return base64.b16encode(b(input)), len(input)

def base16_decode(input, errors='strict'):
    return base64.b16decode(b(input)), len(input)

add("base16", base16_encode, base16_decode, r"(?i)^base[-_]?16$")

# BASE32
def base32_encode(input, errors='strict'):
    return base64.b32encode(b(input)), len(input)

def base32_decode(input, errors='strict'):
    return base64.b32decode(b(input)), len(input)

add("base32", base32_encode, base32_decode, r"(?i)^base[-_]?32$")

# BASE64
def base64_encode(input, errors='strict'):
    return base64.b64encode(b(input)), len(input)

def base64_decode(input, errors='strict'):
    return base64.b64decode(b(input)), len(input)

add("base64", base64_encode, base64_decode, r"(?i)^base[-_]?64$")


if PY3:
    # BASE85
    def base85_encode(input, errors='strict'):
        return base64.b85encode(b(input)), len(input)

    def base85_decode(input, errors='strict'):
        return base64.b85decode(b(input)), len(input)

    add("base85", base85_encode, base85_decode, r"(?i)^base[-_]?85$")
    
    # BASE100
    class Base100Error(ValueError):
        pass

    class Base100DecodeError(Base100Error):
        pass
    
    def base100_encode(input, errors='strict'):
        input = b(input)
        r = [240, 159, 0, 0] * len(input)
        for i, c in enumerate(input):
            r[4*i+2] = (c + 55) // 64 + 143
            r[4*i+3] = (c + 55) % 64 + 128
        return bytes(r), len(input)

    def base100_decode(input, errors='strict'):
        input = b(input)
        print(input)
        if len(input) % 4 != 0:
            raise Base100DecodeError("Bad input (length should be multiple of"
                                     " 4)")
        r = [None] * (len(input) // 4)
        for i, c in enumerate(input):
            if i % 4 == 2:
                tmp = ((c - 143) * 64) % 256
            elif i % 4 == 3:
                r[i//4] = (c - 128 + tmp - 55) & 0xff
        return bytes(r), len(input)

    add("base100", base100_encode, base100_decode,
        r"(?i)^(?:base[-_]?100|emoji)$")
