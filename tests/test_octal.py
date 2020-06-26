#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Octal codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecOctal(TestCase):
    def test_codec_octal(self):
        STR = "this is a test"
        OCT1 = "164150151163040151163040141040164145163164"
        OCT2 = "164 150 151 163 40 151 163 40 141 40 164 145 163 164"
        self.assertEqual(codecs.encode(STR, "octal"), OCT1)
        self.assertEqual(codecs.encode(b(STR), "octals"), b(OCT1))
        self.assertEqual(codecs.decode(OCT1, "octals"), STR)
        self.assertEqual(codecs.decode(b(OCT1), "octal"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "bad oct string", "octal")
        self.assertEqual(codecs.encode(STR, "octal-spaced"), OCT2)
        self.assertEqual(codecs.encode(b(STR), "octals-spaced"), b(OCT2))
        self.assertEqual(codecs.decode(OCT2, "octals-spaced"), STR)
        self.assertEqual(codecs.decode(b(OCT2), "octal-spaced"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "bad oct string", "octal-spaced")

