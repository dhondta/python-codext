# -*- coding: UTF-8 -*-
"""DNA Codec - dna content encoding.

This implements the 8 methods of ATGC nucleotides following the rule of complementary pairing, according the literature4
 about coding and computing of DNA sequences.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


SEQUENCES = {
    '00': "AAGCGCTT",
    '11': "TTCGCGAA",
    '01': "GCAATTGC",
    '10': "CGTTAACG",
}
ENCMAP = []
for i in range(8):
    ENCMAP.append({k: v[i] for k, v in SEQUENCES.items()})


add_map("dna", ENCMAP, binary=True, pattern=r"dna[-_]?([1-8])$")
