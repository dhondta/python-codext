#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Nokia codecs tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecNokia(TestCase):
    def test_codec_nokia3310(self):
        STR = "this is a test"
        NOK = "8-44-444-7777-0-444-7777-0-2-0-8-33-7777-8"
        self.assertEqual(codecs.encode(STR, "nokia3310"), NOK)
        self.assertEqual(codecs.encode(STR, "nokia-3310"), NOK)
        self.assertEqual(codecs.encode(STR, "nokia_3310"), NOK)
        self.assertEqual(codecs.encode(b(STR), "nokia3310"), b(NOK))
        self.assertEqual(codecs.decode(NOK, "nokia3310"), STR)
        self.assertEqual(codecs.decode(b(NOK), "nokia3310"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "ABCD", "nokia3310")
        self.assertEqual(codecs.decode("A", "nokia3310", errors="replace"), "?")
        self.assertEqual(codecs.decode("A", "nokia3310", errors="ignore"), "")
        self.assertRaises(ValueError, codecs.decode, "B", "nokia3310",
                          errors="BAD")
