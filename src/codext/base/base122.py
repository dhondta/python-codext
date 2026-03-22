# -*- coding: UTF-8 -*-
"""Base122 Codec - base122 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base122|base-122)': {
        'this is a test': ":\x1aʗ\x19\x01Rs\x10\x18$\x07#\x15ft",
        b'This is another longer test string with d1g1t5 and sp3c141 characters !\n': \
            b"*\x1a\xca\x97\x19\x01Rs\x10\x18-f{QPe9\x08\xcb\x86{9Ne9\x08\x0eF+Mh 9]\x0e\xd3\x8b"
            b"9N ;Z.FA\x01H13L.C)\x01Bn2\x08\x0e7\x01MF1\x1a\x0c$\x06\x1b!Br0XnF+If \x10B@"
    },
    'enc-dec(base_122)': ["@random"],
}


_BAD = [0, 10, 13, 34, 38, 92]
_i = lambda c: c if isinstance(c, int) else ord(c)


# inspired from: https://github.com/kevinAlbs/Base122/blob/master/base122.js
def base122_encode(input, errors="strict"):
    idx, bit, r, l = 0, 0, [], len(input)
    
    def _get_7bits(idx, bit):
        if idx >= l:
            return idx, bit, False
        B1 = _i(input[idx])
        p1 = (((254 >> bit) & B1) << bit) >> 1
        bit += 7
        if bit < 8:
            return idx, bit, p1
        bit -= 8
        idx += 1
        if idx >= l:
            return idx, bit, p1
        B2 = _i(input[idx])
        p2 = (((65280 >> bit) & B2) & 255) >> (8 - bit)
        return idx, bit, (p1 | p2)
    
    while True:
        if idx >= l:
            break
        # get seven bits of input data
        idx, bit, B = _get_7bits(idx, bit)
        # check for illegal chars
        try:
            bad_idx = _BAD.index(B)
        except ValueError:
            r.append(B)
            continue
        idx, bit, nB = _get_7bits(idx, bit)
        if nB is False:
            nB, bad_idx = B, 7
        B1, B2 = 194, 128
        B1 |= (7 & bad_idx) << 2
        B1 |= int((nB & 64) > 0)
        B2 |= nB & 63
        r.extend([B1, B2])
    return "".join(map(chr, r)).encode("latin-1"), len(input)


# inspired from: https://github.com/kevinAlbs/Base122/blob/master/base122.js
def base122_decode(input, errors="strict"):
    currB, bob, r, input = 0, 0, [], list(map(ord, input))
    
    def _get_7bits(currB, bob, B, decoded):
        B <<= 1
        currB |= (B % 0x100000000) >> bob
        bob += 7
        if bob >= 8:
            decoded += [currB]
            bob -= 8
        return (B << (7 - bob)) & 255, bob

    for i in range(len(input)):
        if input[i] >= 128:
            try:
                currB, bob = _get_7bits(currB, bob, _BAD[(input[i] >> 8) & 7], r)
            except IndexError:
                pass
            currB, bob = _get_7bits(currB, bob, input[i] & 127, r)
        else:
            currB, bob = _get_7bits(currB, bob, input[i], r)
    return "".join(map(chr, r)).rstrip("\0"), len(input)


add("base122", base122_encode, base122_decode, r"^base[-_]?122$", expansion_factor=1.085)
main122 = main(122, "<http://blog.kevinalbs.com/base122>", wrap=False)

