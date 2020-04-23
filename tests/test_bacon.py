#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bacon codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecBaconianCipher(TestCase):
    def test_codec_bacon(self):
        STR = "this is a test"
        BCN1 = "baaba aabbb abaaa baaab  abaaa baaab  aaaaa  baaba aabaa baaab baaba"
        BCN2 = "10010 00111 01000 10001  01000 10001  00000  10010 00100 10001 10010"
        self.assertEqual(codecs.encode(b(STR), "bacon"), b(BCN1))
        self.assertEqual(codecs.encode(b(STR), "bacon-ab"), b(BCN1))
        self.assertEqual(codecs.encode(b(STR), "bacon-AB"), b(BCN1.upper()))
        self.assertEqual(codecs.encode(b(STR), "bacon-01"), b(BCN2))
        self.assertRaises(ValueError, codecs.encode, "\r", "bacon")
        self.assertRaises(ValueError, codecs.decode, "\r", "bacon-AB")
        self.assertRaises(ValueError, codecs.decode, BCN1, "bacon-01")
        self.assertEqual(codecs.decode(b(BCN2), "bacon-01"), b(STR.upper()))
        self.assertIsNotNone(codecs.encode("test\r", "bacon_cipher", "replace"))
        self.assertIsNotNone(codecs.decode("test\r", "baconian-cipher", "replace"))
        self.assertIsNotNone(codecs.encode("test\r", "bacon_cipher", "ignore"))
        self.assertIsNotNone(codecs.decode("test\r", "baconian-cipher", "ignore"))
        self.assertRaises(ValueError, codecs.encode, "\r", "baconian-cipher", "BAD")
