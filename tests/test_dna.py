#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""DNA codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecDNA(TestCase):
    def test_codec_dna(self):
        STR = "this is a test"
        DNA = [
            "GTGAGCCAGCCGGTATACAAGCCGGTATACAAGCAGACAAGTGAGCGGGTATGTGA",
            "CTCACGGACGGCCTATAGAACGGCCTATAGAACGACAGAACTCACGCCCTATCTCA",
            "ACAGATTGATTAACGCGTGGATTAACGCGTGGATGAGTGGACAGATAAACGCACAG",
            "AGACATTCATTAAGCGCTCCATTAAGCGCTCCATCACTCCAGACATAAAGCGAGAC",
            "TCTGTAAGTAATTCGCGAGGTAATTCGCGAGGTAGTGAGGTCTGTATTTCGCTCTG",
            "TGTCTAACTAATTGCGCACCTAATTGCGCACCTACTCACCTGTCTATTTGCGTGTC",
            "GAGTGCCTGCCGGATATCTTGCCGGATATCTTGCTGTCTTGAGTGCGGGATAGAGT",
            "CACTCGGTCGGCCATATGTTCGGCCATATGTTCGTCTGTTCACTCGCCCATACACT",
        ]
        for i in range(8):
            enc = "dna-{}".format(i + 1)
            self.assertEqual(codecs.encode(STR, enc), DNA[i])
            self.assertEqual(codecs.encode(b(STR), enc), b(DNA[i]))
            self.assertEqual(codecs.decode(DNA[i], enc), STR)
            self.assertEqual(codecs.decode(b(DNA[i]), enc), b(STR))
            self.assertRaises(ValueError, codecs.decode, "ABC", enc)
        self.assertEqual(codecs.decode("ABC", "dna-2", errors="replace"),
                         "[00??01]")
        self.assertEqual(codecs.decode("ABC", "dna-1", errors="ignore"), "\x02")
        self.assertRaises(ValueError, codecs.decode, "B", "dna-8", errors="BAD")
