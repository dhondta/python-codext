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


__examples__ = {
    'enc(dna0|dna9)': None,
    'enc(dna1)':      {'this is a test': "GTGAGCCAGCCGGTATACAAGCCGGTATACAAGCAGACAAGTGAGCGGGTATGTGA"},
    'enc(dna-2)':     {'this is a test': "CTCACGGACGGCCTATAGAACGGCCTATAGAACGACAGAACTCACGCCCTATCTCA"},
    'enc(dna_3)':     {'this is a test': "ACAGATTGATTAACGCGTGGATTAACGCGTGGATGAGTGGACAGATAAACGCACAG"},
    'enc(dna4)':      {'this is a test': "AGACATTCATTAAGCGCTCCATTAAGCGCTCCATCACTCCAGACATAAAGCGAGAC"},
    'enc(dna-5)':     {'this is a test': "TCTGTAAGTAATTCGCGAGGTAATTCGCGAGGTAGTGAGGTCTGTATTTCGCTCTG"},
    'enc(dna_6)':     {'this is a test': "TGTCTAACTAATTGCGCACCTAATTGCGCACCTACTCACCTGTCTATTTGCGTGTC"},
    'enc(dna7)':      {'this is a test': "GAGTGCCTGCCGGATATCTTGCCGGATATCTTGCTGTCTTGAGTGCGGGATAGAGT"},
    'enc(dna-8)':     {'this is a test': "CACTCGGTCGGCCATATGTTCGGCCATATGTTCGTCTGTTCACTCGCCCATACACT"},
}


SEQUENCES = {
    '00': "AAGCGCTT",
    '11': "TTCGCGAA",
    '01': "GCAATTGC",
    '10': "CGTTAACG",
}
ENCMAP = []
for i in range(8):
    ENCMAP.append({k: v[i] for k, v in SEQUENCES.items()})


add_map("dna", ENCMAP, intype="bin", pattern=r"dna[-_]?([1-8])$")

