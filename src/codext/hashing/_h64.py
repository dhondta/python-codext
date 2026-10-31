# -*- coding: UTF-8 -*-
"""Hash64 encoding, shared by the password hashes that write their digests with the "./0-9A-Za-z" alphabet of crypt(3)
 (the DES-based hashes, phpass and the Cisco PIX/ASA hashes).

Two conventions coexist: the "little-endian" one of the modular crypt format (bytes taken by groups of 3, each group
 giving 4 characters from its least significant bits) and the "big-endian" one of the DES-based hashes (integers
 written from their most significant bits). Both use the same alphabet.
"""
ALPHABET = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_IDX = {c: i for i, c in enumerate(ALPHABET)}


def encode_bytes(data):
    """ Encode bytes like the modular crypt format (groups of 3 bytes, least significant bits first). """
    r = ""
    for i in range(0, len(data), 3):
        g = data[i:i+3]
        v = g[0] | (g[1] << 8 if len(g) > 1 else 0) | (g[2] << 16 if len(g) > 2 else 0)
        for _ in range(len(g) + 1):
            r += ALPHABET[v & 63]
            v >>= 6
    return r


def encode_transposed(data, offsets):
    """ Encode the bytes of the data taken in the given order (as the Sun MD5 crypt hash does). """
    return encode_bytes(bytes(data[o] for o in offsets))


def encode_int_big(value, nchars):
    """ Encode an integer on the given number of characters, most significant bits first. """
    return "".join(ALPHABET[(value >> (6 * (nchars - 1 - i))) & 63] for i in range(nchars))


def encode_int64(value):
    """ Encode a 64-bit integer on 11 characters, most significant bits first (as the DES-based hashes do). """
    return encode_int_big(value << 2, 11)


def encode_int24(value):
    """ Encode a 24-bit integer on 4 characters, least significant bits first (as BSDi crypt does for its rounds). """
    return "".join(ALPHABET[(value >> (6 * i)) & 63] for i in range(4))


def decode_int12(s):
    """ Decode 2 characters to a 12-bit integer, least significant bits first. """
    return _IDX[s[0]] + _IDX[s[1]] * 64


def decode_int24(s):
    """ Decode 4 characters to a 24-bit integer, least significant bits first. """
    return sum(_IDX[s[i]] * 64 ** i for i in range(4))
