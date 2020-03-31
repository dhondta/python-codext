# -*- coding: UTF-8 -*-
"""Bacon's Cipher Codec - bacon content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Bacon%27s_cipher
"""
from ..__common__ import *


ENCMAP = {
    'A': "aaaaa",
}
REPLACE_CHAR = "?"

#FIXME
"""
VERSION 1

Letter 	Code 	Binary
A 	aaaaa 	00000
B 	aaaab 	00001
C 	aaaba 	00010
D 	aaabb 	00011
E 	aabaa 	00100
F 	aabab 	00101
G 	aabba 	00110
H 	aabbb 	00111
I, J 	abaaa 	01000
K 	abaab 	01001
L 	ababa 	01010
M 	ababb 	01011
	
Letter 	Code 	Binary
N 	abbaa 	01100
O 	abbab 	01101
P 	abbba 	01110
Q 	abbbb 	01111
R 	baaaa 	10000
S 	baaab 	10001
T 	baaba 	10010
U, V 	baabb 	10011
W 	babaa 	10100
X 	babab 	10101
Y 	babba 	10110
Z 	babbb 	10111 

Letter 	Code 	Binary
A 	aaaaa 	00000
B 	aaaab 	00001
C 	aaaba 	00010
D 	aaabb 	00011
E 	aabaa 	00100
F 	aabab 	00101
G 	aabba 	00110
H 	aabbb 	00111
I 	abaaa 	01000
J 	abaab 	01001
K 	ababa 	01010
L 	ababb 	01011
M 	abbaa 	01100

VERSION 2

Letter 	Code 	Binary
N 	abbab 	01101
O 	abbba 	01110
P 	abbbb 	01111
Q 	baaaa 	10000
R 	baaab 	10001
S 	baaba 	10010
T 	baabb 	10011
U 	babaa 	10100
V 	babab 	10101
W 	babba 	10110
X 	babbb 	10111
Y 	bbaaa 	11000
Z 	bbaab 	11001 
"""

class BaconError(ValueError):
    pass


class BaconDecodeError(BaconError):
    pass


class BaconEncodeError(BaconError):
    pass


def bacon_encode(code):
    def encode(text, errors="strict"):
        std0, stdn = [c for c in STD[0]], [c for c in STD[code]]
        spec0, specn = SPEC[0].split(), SPEC[code].split()
        mapping = {d: e for d, e in zip(std0 + spec0, stdn + specn)}
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += mapping[c]
            except KeyError:
                if errors == "strict":
                    raise BaconEncodeError("'bacon' codec can't encode"
                                            " character '{}' in position {}"
                                            .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)
    return encode


def bacon_decode(code):
    def decode(text, errors="strict"):
        std0, stdn = [c for c in STD[0]], [c for c in STD[code]]
        spec0, specn = SPEC[0].split(), SPEC[code].split()
        mapping = {e: d for d, e in zip(std0 + spec0, stdn + specn)}
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += mapping[c]
            except KeyError:
                if errors == "strict":
                    raise BaconDecodeError("'bacon' codec can't decode"
                                            " character '{}' in position {}"
                                            .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)
    return decode


# note: the integer behind "bacon" is captured for sending to the
#        parametrizable encode and decode functions "bacon_**code"
add("bacon", bacon_encode, bacon_decode, r"bacon(?:onian[-_]cipher)$")
