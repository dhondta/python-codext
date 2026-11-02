# -*- coding: UTF-8 -*-
"""Base58 Monero Codec - base58-monero content encoding.

Monero (after CryptoNote) uses the Bitcoin alphabet of Base58, but encodes the input by blocks of 8 bytes instead of as
 a whole: each block is read as a big-endian integer and written with 11 characters, left-padded with the first
 character of the alphabet ("1"), a last block of N bytes (N < 8) being written with 0, 2, 3, 5, 6, 7, 9 or 10
 characters (for N from 0 to 7). The length of the output is thus fixed by the length of the input, unlike Bitcoin's
 Base58. When decoding, a last block of another length (1, 4 or 8 characters) and a block whose value overflows its
 number of bytes are invalid.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/monero-project/monero/blob/master/src/common/base58.cpp
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base58-monero|base58_monero|base58monero|base58-xmr|base58-cryptonote)': {
        '\x00': "11", '\x39': "1z", '\xff': "5Q", '\x00\x39': "11z", '\xff\xff': "LUv", '\xff\xff\xff': "2UzHL",
        '\xff' * 7: "Ahg1opVcGW", '\xff' * 8: "jpXCZedGfVQ", '\x00' * 9: "1111111111111",
        '\x06\x15\x60\x13\x76\x28\x79\xf7\xff\xff\xff\xff\xff': "22222222222VtB5VXc",
    },
    'dec(base58-monero)': {
        '': "", '5Q': "\xff", '1Ahg1opVcGW': "\x00\xff\xff\xff\xff\xff\xff\xff", 'jpXCZedGfVQ5Q': "\xff" * 9,
        'jpXCZedGfVQ\n5Q': "\xff" * 9,
        # invalid lengths of the last block, overflowing blocks and characters out of the alphabet
        '1': None, '1111': None, '11111111': None, '123456789AB1': None, '5R': None, 'zz': None, 'jpXCZedGfVR': None,
        '01111111111': None, 'I1111111111': None, 'O1111111111': None, 'l1111111111': None, '_1111111111': None,
    },
    'enc-dec(base58-monero)': ["test", "This is a test", "@random{512,1024,2048}"],
}
__guess__ = ["base58-monero"]


B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B58_VALUES = {c: i for i, c in enumerate(B58)}
# number of characters of an encoded block, by number of bytes of the block
ENCODED_SIZES = [0, 2, 3, 5, 6, 7, 9, 10, 11]
DECODED_SIZES = {n: i for i, n in enumerate(ENCODED_SIZES)}


def base58monero_encode(text, errors="strict"):
    t, r = b(text), []
    for i in range(0, len(t), 8):
        block = t[i:i+8]
        n, s = int.from_bytes(block, "big"), ""
        while n > 0:
            n, d = divmod(n, 58)
            s = B58[d] + s
        r.append(s.rjust(ENCODED_SIZES[len(block)], B58[0]))
    return "".join(r), len(t)


def base58monero_decode(text, errors="strict"):
    t = ensure_str(_stripl(text, True, True))
    _h = handle_error("base58-monero", errors, decode=True, kind="block")
    # characters out of the alphabet are errors (only skipped if errors are not handled strictly)
    chars, r = [], bytearray()
    for i, c in enumerate(t):
        if c in B58_VALUES:
            chars.append(c)
        else:
            _h(c, i, bytes(r))
    for i in range(0, len(chars), 11):
        block = chars[i:i+11]
        size, n = DECODED_SIZES.get(len(block), 0), 0
        for c in block:
            n = n * 58 + B58_VALUES[c]
        # a block must have a valid length and its value must fit in its number of bytes
        if size == 0 or n >= 256 ** size:
            _h("".join(block), i, bytes(r))
            continue
        r.extend(n.to_bytes(size, "big"))
    return bytes(r), len(text)


add("base58-monero", base58monero_encode, base58monero_decode, r"^base[-_]?58[-_]?(?:monero|xmr|cryptonote)$",
    entropy=5.858, expansion_factor=(11 / 8, .15), len_charset=58, printables_rate=1.)
main58xmr = main(58, "<https://github.com/monero-project/monero/blob/master/src/common/base58.cpp>", "monero",
                 inv=False)
