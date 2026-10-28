# -*- coding: UTF-8 -*-
"""Base2048/Base32768/Base65536 Codecs - base2048, base32768 and base65536 content encodings.

These encodings, designed by qntm, write the data with 11, 15 or 16 bits per character, using repertoires of Unicode
 characters that are safe to transmit (no whitespace, no punctuation, no control or combining characters, ...):
- Base2048 is optimised for Twitter (which counts most of these characters as 1)
- Base32768 is optimised for UTF-16 (all its characters are in the Basic Multilingual Plane)
- Base65536 is optimised for UTF-32 (2 bytes per character)

The bits are taken most significant first. The final bits are padded with 1s up to the size of the main repertoire or
 of a smaller final repertoire (3 bits for Base2048, 7 bits for Base32768 and 8 bits for Base65536) ; a character of
 the final repertoire can only end the encoded text. When decoding, whitespaces are ignored.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/qntm/base2048
           https://github.com/qntm/base32768
           https://github.com/qntm/base65536
"""
from ._base import main
from ..__common__ import *


# NB: short random strings may be valid UTF-8 once converted to bytes, then read as text by codext ; hence, fixed
#      strings holding "\xff" are used for the round trips
__examples1__ = {
    'enc(base2048|base-2048|base_2048)': {'': "", '\x00': "F", '\xff': "\u1055", 'Hello': "\u050b\u03e0\u0272\u0db9"},
    'dec(base2048)':     {'\u050b\u03e0\u0272\u0db9': "Hello", '\u050b\u03e0\n\u0272 \u0db9': "Hello",
                          'F!': None, '0F': None, 'A': None},
    'enc-dec(base2048)': ["\xff", "\xff\xfe", "A\xff\x80", "\xffbcd", "\xff" * 11, "Hello, World!",
                          "@random{512,1024}"],
}
__examples2__ = {
    'enc(base32768|base-32768|base_32768)': {'': "", '\x00': "\u06bf", '\xff': "\ua85f", 'Hello': "\u4a72\u817b\u343f"},
    'dec(base32768)':     {'\u4a72\u817b\u343f': "Hello", '\u06bf!': None, '\u0180\u06bf': None, '\u04a0': None},
    'enc-dec(base32768)': ["\xff", "\xff\xfe", "A\xff\x80", "\xffbcd", "\xff" * 11, "Hello, World!",
                           "@random{512,1024}"],
}
__examples3__ = {
    'enc(base65536|base-65536|base_65536)': {'': "", '\x00': "\u1500", '\xff': "\u15ff", 'Hello': "\u9a48\ua36c\u156f"},
    'dec(base65536)':     {'\u9a48\ua36c\u156f': "Hello", '\u1500!': None, '\u1500\u9a48': None},
    'enc-dec(base65536)': ["\xff", "\xff\xfe", "A\xff\x80", "\xffbcd", "\xff" * 11, "Hello, World!",
                           "@random{512,1024}"],
}
__guess1__, __guess2__, __guess3__ = ["base2048"], ["base32768"], ["base65536"]


# repertoires as inclusive ranges of code points (hexadecimal), for the main and the final characters
REPERTOIRES = {
    2048:  ("38-39 41-5a 61-7a c6-c6 d0-d0 d8-d8 de-df e6-e6 f0-f0 f8-f8 fe-fe 110-111 126-127 131-131 138-138 141-142 "
            "14a-14b 152-153 166-167 180-19f 1a2-1ae 1b1-1c3 1dd-1dd 1e4-1e5 1f6-1f7 21c-21d 220-225 234-2af 370-373 "
            "376-377 37b-37d 37f-37f 391-3a1 3a3-3a9 3b1-3c9 3cf-3cf 3d7-3ef 3f3-3f3 3f7-3f8 3fa-3ff 402-402 404-406 "
            "408-40b 40f-418 41a-438 43a-44f 452-452 454-456 458-45b 45f-475 478-481 48a-4c0 4c3-4cf 4d4-4d5 4d8-4d9 "
            "4e0-4e1 4e8-4e9 4f6-4f7 4fa-52f 531-556 561-586 5d0-5ea 5f0-5f2 620-621 627-63f 641-64a 660-669 66e-66f "
            "671-674 679-6bf 6c1-6c1 6c3-6d2 6d5-6d5 6ee-6fc 6ff-6ff 710-710 712-72f 74d-7a5 7b1-7b1 7c0-7ea 800-815 "
            "840-858 860-86a 8a0-8b4 8b6-8bd 904-928 92a-930 932-933 935-939 93d-93d 950-950 960-961 966-96f 972-980 "
            "985-98c 98f-990 993-9a8 9aa-9b0 9b2-9b2 9b6-9b9 9bd-9bd 9ce-9ce 9e0-9e1 9e6-9f1 9f4-9f9 9fc-9fc a05-a0a "
            "a0f-a10 a13-a28 a2a-a30 a32-a32 a35-a35 a38-a39 a5c-a5c a66-a6f a72-a74 a85-a8d a8f-a91 a93-aa8 aaa-ab0 "
            "ab2-ab3 ab5-ab9 abd-abd ad0-ad0 ae0-ae1 ae6-aef af9-af9 b05-b0c b0f-b10 b13-b28 b2a-b30 b32-b33 b35-b39 "
            "b3d-b3d b5f-b61 b66-b6f b71-b77 b83-b83 b85-b8a b8e-b90 b92-b93 b95-b95 b99-b9a b9c-b9c b9e-b9f ba3-ba4 "
            "ba8-baa bae-bb9 bd0-bd0 be6-bf2 c05-c0c c0e-c10 c12-c28 c2a-c39 c3d-c3d c58-c5a c60-c61 c66-c6f c78-c7e "
            "c80-c80 c85-c8c c8e-c90 c92-ca8 caa-cb3 cb5-cb9 cbd-cbd cde-cde ce0-ce1 ce6-cef cf1-cf2 d05-d0c d0e-d10 "
            "d12-d3a d3d-d3d d4e-d4e d54-d56 d58-d61 d66-d78 d7a-d7f d85-d96 d9a-db1 db3-dbb dbd-dbd dc0-dc6 de6-def "
            "e01-e30 e32-e32 e40-e45 e50-e59 e81-e82 e84-e84 e87-e88 e8a-e8a e8d-e8d e94-e97 e99-e9f ea1-ea3 ea5-ea5 "
            "ea7-ea7 eaa-eab ead-eb0 eb2-eb2 ebd-ebd ec0-ec4 ed0-ed9 ede-edf f00-f00 f20-f33 f40-f42 f44-f47 f49-f4c "
            "f4e-f51 f53-f56 f58-f5b f5d-f68 f6a-f6c f88-f8c 1000-1025 1027-102a 103f-1049 1050-1055",
            "30-37"),
    32768: ("4a0-4bf 500-51f 680-6bf 760-79f 7c0-7df 1000-101f 10a0-10bf 1100-115f 1180-119f 11e0-123f 1260-127f "
            "12e0-12ff 1320-133f 13a0-13df 1420-165f 16a0-16df 1780-179f 1820-185f 18c0-18df 1980-199f 19e0-19ff "
            "1a20-1a3f 1bc0-1bdf 1c00-1c1f 1d00-1d1f 21e0-21ff 22c0-22df 2340-23df 2400-241f 2500-275f 2780-27bf "
            "2800-297f 29a0-29bf 2a20-2a5f 2a80-2abf 2ae0-2b5f 2c00-2c1f 2c80-2cdf 2d00-2d1f 2d40-2d5f 2ea0-2edf "
            "31c0-31df 3400-4d9f 4dc0-9fbf a000-a47f a4a0-a4bf a500-a5ff a640-a65f a6a0-a6df a700-a75f a780-a79f "
            "a840-a85f",
            "180-19f 240-29f"),
    65536: ("3400-4cff 4e00-9eff a100-a3ff a500-a5ff 10600-106ff 12000-122ff 13000-133ff 14400-145ff 16800-169ff "
            "20000-285ff",
            "1500-15ff"),
}


def __repertoire(ranges):
    return "".join(chr(c) for r in ranges.split() for a, b in [r.split("-")] for c in range(int(a, 16), int(b, 16) + 1))


def __base(n):
    nbits = n.bit_length() - 1
    main, final = map(__repertoire, REPERTOIRES[n])
    fbits = len(final).bit_length() - 1
    if n == 65536:
        # Base65536 was originally designed with the bytes of each pair in the wrong order
        main = "".join(main[(z & 255) << 8 | z >> 8] for z in range(n))
    lookup = {c: (fbits, z) for z, c in enumerate(final)}
    lookup.update({c: (nbits, z) for z, c in enumerate(main)})
    
    def encode(text, errors="strict"):
        r, z, k = [], 0, 0
        for x in b(text):
            z, k = z << 8 | x, k + 8
            if k >= nbits:
                k -= nbits
                r.append(main[z >> k])
                z &= (1 << k) - 1
        if k > 0:
            # the final bits are padded with 1s up to the size of the final repertoire, or of the main one if too many
            p = (fbits if k <= fbits else nbits) - k
            r.append((final if k <= fbits else main)[z << p | (1 << p) - 1])
        return (s := "".join(r)), len(s)
    
    def decode(text, errors="strict"):
        _h, text = handle_error(f"base{n}", errors, decode=True), ensure_str(text)
        chars, r, z, k = [], bytearray(), 0, 0
        for i, c in enumerate(text):
            if c in lookup:
                chars.append((i, c))
            elif not c.isspace():
                # a wrong character cannot be replaced in the binary stream, hence it is dropped
                _h(c, i)
        for j, (i, c) in enumerate(chars):
            m, v = lookup[c]
            if m == nbits or j == len(chars) - 1:
                z, k = z << m | v, k + m
                while k >= 8:
                    k -= 8
                    r.append(z >> k & 255)
                z &= (1 << k) - 1
            else:
                # a character of the final repertoire can only end the encoded text
                _h(c, i)
        if z != (1 << k) - 1 and errors == "strict":
            handle_error(f"base{n}", errors, decode=True, kind="padding")(f"{z:0{k}b}", len(text))
        return bytes(r), len(r)
    
    return encode, decode


for _n, _ex, _gs in [(2048, __examples1__, __guess1__), (32768, __examples2__, __guess2__),
                     (65536, __examples3__, __guess3__)]:
    add(f"base{_n}", *__base(_n), rf"^base[-_]?{_n}$", examples=_ex, guess=_gs,
        expansion_factor=8 / (_n.bit_length() - 1))
main2048 = main(2048, "<https://github.com/qntm/base2048>", inv=False, swap=False, wrap=False)
main32768 = main(32768, "<https://github.com/qntm/base32768>", inv=False, swap=False, wrap=False)
main65536 = main(65536, "<https://github.com/qntm/base65536>", inv=False, swap=False, wrap=False)
