#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Resistor codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecResistor(TestCase):
    def test_codec_resistor(self):
        STR = "1234"
        RES = "\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m"
        self.assertEqual(codecs.encode(STR, "resistor"), RES)
        self.assertEqual(codecs.encode(b(STR), "resistor_color"), b(RES))
        self.assertEqual(codecs.decode(RES, "resistor_color_code"), STR)
        self.assertEqual(codecs.decode(b(RES), "resistors-color-code"), b(STR))
        self.assertRaises(ValueError, codecs.encode, "NOT ENCODABLE", "resistor")
        self.assertRaises(ValueError, codecs.decode, "NOT DECODABLE", "resistors")
