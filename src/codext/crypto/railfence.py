# -*- coding: UTF-8 -*-
"""Rail Fence Cipher Codec - rail fence content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(rail_123|rail-2-123)':     {'this is a test': None},
    'enc(railfence|zigzag)':        {'this is a test': "t ashsi  etist"},
    'enc(rail-5|zigzag_5)':         {'this is a test': "tah  istsiet s"},
    'enc(rail_5-3|rail_5_3)':       {'this is a test': "it sss etiath "},
    'enc(rail-5-3-up|rail_5_3-up)': {'this is a test': "h tiats e ssit"},
    'enc(rail-7-4|rail_7_4)':       {'this is a test': "a  stiet shsti"},
    'dec(zigzag)':                  {'': ""},
}
__guess__ = ["railfence-%d" % i for i in range(1, 11)] + ["railfence-%d-up" % i for i in range(1, 11)]


def __build(text, rails, offset, up):
    l, rail = len(text), offset
    # set the starting rail and direction
    if up:
        dr = -1
        rail = rails - offset - 1
    else: 
        dr = 1
    # create rails
    f = [[None] * l for i in range(rails)]
    # now zig-zag between rails
    for x in range(l): 
        f[rail][x] = text[x]
        if rail >= rails - 1:
            dr = -1
        elif rail <= 0:
            dr = 1
        rail += dr
    return f


def __check(length, rails, offset):
    if rails > length:
        raise ParameterError("Bad parameter for encoding 'railfence': rails=%d (should be <= %d)" % (rails, length))
    if offset > rails:
        raise ParameterError("Bad parameter for encoding 'railfence': offset=%d (should be <= %d)" % (offset, rails))


def railfence_encode(rails, offset, up):
    rails, offset, up = int(rails or 3), int(offset or 0), up is not None and up != ""
    def encode(text, errors="strict"):
        r, l = "", len(text)
        __check(l, rails, offset)
        f = __build(text, rails, offset, up)
        for rail in range(rails): 
            for x in range(l):
                if f[rail][x] is not None: 
                    r += f[rail][x]
        return r, l
    return encode


def railfence_decode(rails, offset, up):
    rails, offset, up = int(rails or 3), int(offset or 0), up is not None and up != ""
    def decode(text, errors="strict"):
        # this if block is particularly useful with Python2 ; see codecs.py at line 492 in comparison with codecs.py
        #  from Python3 at line 501: in Python2, a last block can be read while empty while in Python3 not
        # as a consequence, in Python2, an error is triggered as an empty text cannot be decoded with Rail Fence with
        #  a rails parameter > 0 (see the __check(length, rails, offset)) function
        if text == "":
            return "", 0
        r, i, l = "", 0, len(text)
        __check(l, rails, offset)
        f = __build("." * len(text), rails, offset, up)
        # put the characters in the right place
        for rail in range(rails):
            for x in range(l):            
                if f[rail][x] == ".": 
                    f[rail][x] = text[i]
                    i += 1
        # read the characters in the right order
        for x in range(l): 
            for rail in range(rails):
                if f[rail][x] is not None: 
                    r += f[rail][x]
        return r, len(text)
    return decode


add("railfence", railfence_encode, railfence_decode,
    r"^(?:rail(?:[-_]?fence)?|zigzag)(?:[-_]([1-9]|[1-9]\d+)(?:[-_]([0-9]|[1-9]\d+))?(?:[-_](up))?)?$")

