# -*- coding: UTF-8 -*-
"""Fibonacci Codec - Fibonacci content encoding.

This universal code writes positive integers as self-delimiting codewords, hence concatenated without separator: the
 Zeckendorf representation of the integer (sum of non-consecutive Fibonacci numbers 1, 2, 3, 5, 8, ...), from the least
 significant term, followed by an additional 1 (hence, each codeword ends with "11").

Each character of the text is encoded from its ordinal + 1 (as 0 cannot be encoded), the output being a string of
 bits ; when decoding, the whitespaces are ignored. With the "-integers" variant, the text holds integers (from 1) in
 decimal, separated by whitespaces or commas, and the decoded integers are separated by a space.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Fibonacci_coding
"""
from ._universal import *
from ..__common__ import *


__examples__ = {
    'enc(fibonacci|fibonacci-coding|fibonacci_code|fib)': {'A': "0010100011", 'Hi!': "000101001110100100011000000011"},
    'dec(fibonacci)':                                     {'0010100011': "A", '0101': None},
    'enc(fibonacci-int|fib_integers)':                    {'1': "11", '2': "011", '3': "0011", '4': "1011",
                                                           '11': "001011", '17': "1010011", '65': "0100100011",
                                                           '0': None},
    'dec(fibonacci-int)':                                 {'11 011 0011': "1 2 3", '0101': None},
    'enc-dec(fibonacci)':                                 TEXTS,
    'enc-dec(fibonacci-int)':                             ["", "1", INTEGERS],
}
__guess__ = []


def __fibs(n):
    """ Fibonacci numbers 1, 2, 3, 5, 8, ... up to n. """
    f = [1, 2]
    while f[-1] <= n:
        f.append(f[-1] + f[-2])
    return f


def fibonacci_enc(n):
    bits = []
    for f in __fibs(n)[::-1]:
        if f <= n:
            n -= f
            bits.append("1")
        elif bits:
            bits.append("0")
    return "".join(bits[::-1]) + "1"


def fibonacci_dec(bits, i):
    if (end := bits.find("11", i)) < 0:
        return None, None
    fibs = __fibs(1 << (end - i + 2))
    return sum(fibs[k] for k, c in enumerate(bits[i:end+1]) if c == "1"), end + 2


add("fibonacci", universal("fibonacci", fibonacci_enc, fibonacci_dec), universal("fibonacci", fibonacci_enc,
    fibonacci_dec, True), r"^fib(?:onacci(?:[-_]cod(?:e|ing))?)?" + PATTERN_INTEGERS, examples=__examples__,
    guess=__guess__)
