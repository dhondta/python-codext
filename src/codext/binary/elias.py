# -*- coding: UTF-8 -*-
"""Elias Codes - Elias gamma and Elias delta content encodings.

These universal codes write positive integers as self-delimiting codewords, hence concatenated without separator:
- Elias gamma: N zeros followed by the N+1 bits of the integer (N being the number of bits after the leading 1)
- Elias delta: the Elias gamma codeword of the number of bits of the integer, followed by its bits without the leading
   1

Each character of the text is encoded from its ordinal + 1 (as 0 cannot be encoded), the output being a string of
 bits ; when decoding, the whitespaces are ignored. With the "-integers" variant, the text holds integers (from 1) in
 decimal, separated by whitespaces or commas, and the decoded integers are separated by a space.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Elias_gamma_coding
           https://en.wikipedia.org/wiki/Elias_delta_coding
"""
from ._universal import *
from ..__common__ import *


__examples1__ = {
    'enc(elias-gamma|elias_gamma|eliasgamma|gamma)': {'A': "0000001000010", '\x00': "1",
                                                      'Hi!': "0000001001001000000110101000000100010"},
    'dec(elias-gamma)':                              {'0000001000010 1': "A\x00", '0010': None, '12': None,
                                                      # 0x110001 is out of the range of the Unicode characters
                                                      "0" * 20 + "100010000000000000010": None},
    'enc(elias-gamma-int|gamma_integers)':           {'1': "1", '2': "010", '3': "011", '4': "00100",
                                                      '17': "000010001", '1 2,3': "1010011", '0': None, 'a': None},
    'dec(elias-gamma-int)':                          {'1010 011': "1 2 3", '0010': None, '12': None},
    'enc-dec(elias-gamma)':                          TEXTS,
    'enc-dec(elias-gamma-int)':                      ["", "1", INTEGERS],
}
__examples2__ = {
    'enc(elias-delta|elias_delta|eliasdelta|delta)': {'A': "00111000010", 'Hi!': "00111001001001111010100011000010"},
    'dec(elias-delta)':                              {'00111000010': "A", '0100 01': None},
    'enc(elias-delta-int|delta_integers)':           {'1': "1", '2': "0100", '3': "0101", '4': "01100",
                                                      '17': "001010001", '-1': None},
    'dec(elias-delta-int)':                          {'10100 0101': "1 2 3", '0100 01': None, '00111': None},
    'enc-dec(elias-delta)':                          TEXTS,
    'enc-dec(elias-delta-int)':                      ["", "1", INTEGERS],
}
__guess1__ = __guess2__ = []


def gamma_enc(n):
    return "0" * (n.bit_length() - 1) + f"{n:b}"


def delta_enc(n):
    return gamma_enc(n.bit_length()) + f"{n:b}"[1:]


def gamma_dec(bits, i):
    """ Decode the codeword starting at index i ; return the integer and the index of the next codeword (None if the
         codeword is incomplete). """
    z = i
    while z < len(bits) and bits[z] == "0":
        z += 1
    end = 2 * z - i + 1
    return (int(bits[z:end], 2), end) if end <= len(bits) else (None, None)


def delta_dec(bits, i):
    l, i = gamma_dec(bits, i)
    if l is None or i + l - 1 > len(bits):
        return None, None
    return int("1" + bits[i:i+l-1], 2), i + l - 1


add("elias-gamma", universal("elias-gamma", gamma_enc, gamma_dec), universal("elias-gamma", gamma_enc, gamma_dec, True),
    r"^(?:elias[-_]?)?gamma" + PATTERN_INTEGERS, examples=__examples1__, guess=__guess1__)
add("elias-delta", universal("elias-delta", delta_enc, delta_dec), universal("elias-delta", delta_enc, delta_dec, True),
    r"^(?:elias[-_]?)?delta" + PATTERN_INTEGERS, examples=__examples2__, guess=__guess2__)
