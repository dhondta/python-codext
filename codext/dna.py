# -*- coding: UTF-8 -*-
"""DNA Codec - dna content encoding.

This implements the 8 methods of ATGC nucleotides following the rule of
 complementary pairing, according the literature about coding and computing of
 DNA sequences.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from .__common__ import *


ENCMAP = {
    '00': "AAGCGCTT",
    '11': "TTCGCGAA",
    '01': "GCAATTGC",
    '10': "CGTTAACG",
}
DECMAP = [{v[i]: k for k, v in ENCMAP.items()} for i in range(8)]
REPLACE_CHAR = "?"


class DNAError(ValueError):
    pass


class DNADecodeError(DNAError):
    pass


def dna_encode(n):
    def encode(text, errors="strict"):
        r = ""
        for c in text:
            bs = "{:0>8}".format(bin(ord(c))[2:])
            for i in range(0, 8, 2):
                r += ENCMAP[bs[i:i+2]][n-1]
        return r, len(text)
    return encode


def dna_decode(n):
    def decode(text, errors="strict"):
        r = ""
        text = text.upper()
        for i in range(0, len(text), 4):
            bs = ""
            for j, c in enumerate(text[i:i+4]):
                try:
                    bs += DECMAP[n-1][c]
                except KeyError:
                    if errors == "strict":
                        raise DNADecodeError("'dna' codec can't decode "
                                             "character '{}' in position {}"
                                             .format(c, i + j))
                    elif errors == "replace":
                        bs += 2 * REPLACE_CHAR
                    elif errors == "ignore":
                        continue
                    else:
                        raise ValueError("Unsupported error handling {}"
                                         .format(errors))
            try:
                r += chr(int(bs, 2))
            except ValueError:
                if len(bs) > 0:
                    r += "[" + bs + "]"
        return r, len(text)
    return decode


add("dna", dna_encode, dna_decode, r"dna[-_]?([1-8])$")
