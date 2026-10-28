# -*- coding: UTF-8 -*-
"""Base1024 Codec - base1024 (Ecoji) content encoding.

Ecoji encodes the data with 1024 emojis, that is, 10 bits per emoji. The data is taken by blocks of 5 bytes (40 bits)
 giving 4 emojis. An incomplete last block is completed with the padding emoji U+2615 ; with 4 bytes, the last 2 bits
 are encoded with one of 4 special padding emojis.

Ecoji has two versions, with different sets of emojis (an emoji used by both versions has the same value in both):
- version 1 (Unicode 11 emojis) always pads the last block to 4 emojis
- version 2 (Unicode 14 emojis, default) only writes the first padding emoji

When decoding, both versions are supported (but cannot be mixed), whitespaces are ignored and encoded texts may be
 concatenated.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/keith-turner/ecoji
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base1024|ecoji|ecoji-v2|base1024_2)': {
        '': "",
        'a': "\U0001f455\u2615",
        'abcd': "\U0001f456\U0001f4f8\U0001f9c8\U0001f977",
        'Hello': "\U0001f3ef\U0001f529\U0001f697\U0001f337"},
    'enc(ecoji-v1|ecoji1|base-1024-v1)': {
        '': "",
        'a': "\U0001f455\u2615\u2615\u2615",
        'abcd': "\U0001f456\U0001f4f8\U0001f3a6\u269c",
        'Hello': "\U0001f3ef\U0001f529\U0001f697\U0001f337"},
    'dec(ecoji)': {
        '\U0001f455\u2615\u2615\u2615': "a",
        '\U0001f455\u2615': "a",
        # with version 2, encoded texts can be concatenated
        '\U0001f455\u2615\U0001f455\u2615': "aa",
        '\U0001f3ef\U0001f529\n\U0001f697\U0001f337': "Hello",
        # non-Ecoji character
        '\U0001f004!\u2615': None,
        # emojis of both versions
        '\U0001f170\u23f0\U0001f170\U0001f170': None,
        # padding first, special padding not last
        '\u2615\U0001f004\U0001f004\U0001f004': None,
        '\U0001f004\U0001f977\U0001f004\U0001f004': None,
        # non-padding emoji after padding with version 1
        '\U0001f170\u2615\U0001f004\U0001f004': None,
        # version 1 not padded to 4 emojis
        '\U0001f170\u2615': None,
    },
    'enc-dec(ecoji|ecoji-v1)': ["a", "ab", "abc", "abcd", "abcde", "\xff\xfe\xfd\xfc", "Hello, World!",
                                "@random{512,1024}"],
}
__guess__ = ["ecoji"]


# emojis as code points (hexadecimal, ranges being inclusive) in the order of their values, for both versions
EMOJIS = {
    1: "1f004 1f0cf 1f170-1f171 1f17e-1f17f 1f18e 1f191-1f19a 1f1e6-1f1ff 1f201-1f202 1f21a 1f22f 1f232-1f23a "
        "1f250-1f251 1f300-1f321 1f324-1f393 1f396-1f397 1f399-1f39b 1f39e-1f3cc 1f3ce-1f3f0 1f3f3-1f3f5 1f3f7-1f4d0 "
        "1f4d2-1f4fd 1f4ff-1f53d 1f549-1f54e 1f550-1f567 1f56f-1f570 1f573-1f57a 1f587 1f58a-1f58d 1f590 1f595-1f596 "
        "1f5a4-1f5a5 1f5a8 1f5b1-1f5b2 1f5bc 1f5c2-1f5c4 1f5d1-1f5d3 1f5dc-1f5de 1f5e1 1f5e3 1f5e8 1f5ef 1f5f3 "
        "1f5fa-1f64a 1f64c-1f64f 1f680-1f6c5 1f6cb-1f6d2 1f6e0-1f6e5 1f6e9 1f6eb-1f6ec 1f6f0 1f6f3-1f6f9 1f910-1f93a "
        "1f93c-1f93e 1f940-1f945 1f947-1f970 1f973-1f976 1f97a 1f97c-1f9a2 1f9b0-1f9b9 1f9c0-1f9c2 1f9d0-1f9d5",
    2: "1f004 1f0cf 23f0 23f3 2614 2648-2653 267f 2693 26a1 26bd-26be 26c4-26c5 26ce 26d4 26ea 26f2-26f3 26f5 26fa "
        "26fd 270a-270b 2728 2b50 1f6d5-1f6d7 1f6dd-1f6df 1f6fa 1f201 1f6fb 1f90c 1f90f 1f93f 1f971-1f972 1f978-1f979 "
        "1f97b 1f9a3-1f9a7 1f300-1f320 1f9a8-1f9af 1f9ba-1f9bb 1f32d-1f335 1f9bc 1f337-1f37c 1f9bd 1f37e-1f393 "
        "1f9be-1f9bf 1f9c3-1f9c7 1f3a0-1f3a5 1f9c8 1f3a7-1f3ca 1f9c9-1f9cb 1f3cf-1f3d3 1f9cc-1f9cf 1f9d6-1f9dd "
        "1f3e0-1f3e6 1f9de 1f3e8-1f3f0 1f9df 1f3f4 1f9e0 1f9e2 1f3f8-1f3fa 1f9e3-1f9e7 1f400-1f43e 1f9e8 1f440 1f9e9 "
        "1f442-1f4b8 1f9ea 1f4ba-1f4c0 1f9eb 1f4c2-1f4c4 1f9ec 1f4c6-1f4d0 1f4d2-1f4f3 1f9ed 1f4f5-1f4fc 1f9ee 1f4ff "
        "1f9ef-1f9f3 1f505-1f518 1f9f4-1f9ff 1f525-1f533 1fa70-1fa74 1fa78-1fa7c 1fa80-1fa81 1f54b-1f54e 1fa82-1fa86 "
        "1fa90-1faab 1f57a 1faac 1fab0-1fab4 1f595-1f596 1f5a4 1fab5-1faba 1fac0-1fac5 1fad0-1fad7 1f5fb-1f64a "
        "1f64c-1f64f 1f680-1f6c5 1fad8 1f6cc 1fad9 1fae0-1fae1 1f6d0-1f6d2 1fae2-1fae7 1faf0 1f6eb-1f6ec 1faf1-1faf2 "
        "1f6f4-1f6f9 1f910-1f93a 1f93c-1f93e 1f940-1f945 1f947-1f970 1f973-1f976 1f97a 1f97c-1f9a2 1faf3-1faf6 "
        "1f9b4-1f9b9 1f9c0-1f9c2 1f9d0-1f9d5",
}
# padding emoji (U+2615) and special padding emojis for the last 2 bits of a block of 4 bytes, for both versions
PADDING = "\u2615"
PADDING_LAST = {1: "\u269c\U0001f3cd\U0001f4d1\U0001f64b",
                2: "\U0001f977\U0001f6fc\U0001f4d1\U0001f64b"}
NONE, FILL, LAST = range(3)


def __emojis(ranges):
    return "".join(chr(c) for r in ranges.split() for a, b in [(r + "-" + r).split("-")[:2]]
                   for c in range(int(a, 16), int(b, 16) + 1))


EMOJIS = {v: __emojis(r) for v, r in EMOJIS.items()}
# emoji: (value, version (0 if used by both), padding type)
LOOKUP = {PADDING: (0, 0, FILL)}
for _v in (1, 2):
    for _i, _c in enumerate(EMOJIS[_v]):
        LOOKUP[_c] = (_i, 0 if _c in LOOKUP else _v, NONE)
    for _i, _c in enumerate(PADDING_LAST[_v]):
        LOOKUP[_c] = (_i << 8, 0 if _c in LOOKUP else _v, LAST)


def ecoji_encode(version=None):
    version = int(version or 2)
    emojis, last = EMOJIS[version], PADDING_LAST[version]
    def encode(text, errors="strict"):
        data, r = b(text), []
        for i in range(0, len(data), 5):
            block = data[i:i+5]
            n, v = len(block), int.from_bytes(block.ljust(5, b"\0"), "big")
            # a block of n < 4 bytes gives n emojis, 4 bytes give 3 emojis and a special padding emoji for the last
            #  2 bits, 5 bytes give 4 emojis
            r += [emojis[v >> s & 1023] for s in (30, 20, 10, 0)[:4 if n == 5 else min(n, 3)]]
            if n == 4:
                r.append(last[v >> 8 & 3])
            elif n < 4:
                # version 1 always pads to 4 emojis, version 2 only writes the first padding emoji
                r += [PADDING] * (4 - n if version == 1 else 1)
        return (s := "".join(r)), len(s)
    return encode


def ecoji_decode(version=None):
    def decode(text, errors="strict"):
        _h, text = handle_error("base1024", errors, decode=True, kind="emoji"), ensure_str(text)
        items = []
        for i, c in enumerate(text):
            if c in LOOKUP:
                items.append((i, c))
            elif not c.isspace():
                # a wrong character cannot be replaced in the binary stream, hence it is dropped
                _h(c, i)
        r, ver, k = bytearray(), 0, 0
        while k < len(items):
            group, padding, bad, start = [], 0, False, items[k][0]
            while len(group) < 4:
                if k == len(items):
                    # only version 2 does not pad to 4 emojis
                    if padding != 1 or ver == 1:
                        bad = True
                    break
                i, c = items[k]
                value, v, p = LOOKUP[c]
                # emojis used by only one version cannot be mixed
                if v and ver and v != ver:
                    bad = True
                    break
                ver = ver or v
                if p == NONE and padding > 0:
                    # with version 2, another encoded text may follow the first padding emoji
                    if padding != 1 or ver == 1:
                        bad = True
                    break
                # padding cannot start a block and the special padding emojis can only end it
                if p == FILL and len(group) == 0 or p == LAST and (len(group) != 3 or padding > 0):
                    bad = True
                    break
                group.append((value, p))
                padding += p == FILL
                k += 1
            if bad:
                # the decoding stops at the first error ; the rest of the text, from the faulty block, is handled as the
                #  faulty token
                r += b(_h(text[start:], start, bytes(r)))
                break
            group += [(0, FILL)] * (4 - len(group))
            v = sum(x << s for (x, _), s in zip(group, (30, 20, 10, 0)))
            n = 1 if group[1][1] == FILL else 2 if group[2][1] == FILL else 3 if group[3][1] == FILL else \
                4 if group[3][1] == LAST else 5
            r += v.to_bytes(5, "big")[:n]
        return bytes(r), len(r)
    return decode


add("base1024", ecoji_encode, ecoji_decode, r"^(?:base[-_]?1024|ecoji)(?:[-_]?v?([12]))?$", expansion_factor=.8)
main1024 = main(1024, "<https://github.com/keith-turner/ecoji>", inv=False, swap=False, wrap=False)
