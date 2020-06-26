#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Ordinal codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecOrdinal(TestCase):
    def test_codec_ordinal(self):
        STR = "this is a test"
        ORD1 = "116104105115032105115032097032116101115116"
        ORD2 = "116 104 105 115 32 105 115 32 97 32 116 101 115 116"
        self.assertEqual(codecs.encode(STR, "ordinal"), ORD1)
        self.assertEqual(codecs.encode(b(STR), "ordinals"), b(ORD1))
        self.assertEqual(codecs.decode(ORD1, "ordinals"), STR)
        self.assertEqual(codecs.decode(b(ORD1), "ordinal"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "bad ord string", "ordinal")
        self.assertEqual(codecs.encode(STR, "ordinal-spaced"), ORD2)
        self.assertEqual(codecs.encode(b(STR), "ordinals-spaced"), b(ORD2))
        self.assertEqual(codecs.decode(ORD2, "ordinals-spaced"), STR)
        self.assertEqual(codecs.decode(b(ORD2), "ordinal-spaced"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "bad ord string", "ordinal-spaced")

