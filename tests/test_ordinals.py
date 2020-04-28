#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Ordinals codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecOrdinals(TestCase):
    def test_codec_ordinals(self):
        STR = "this is a test"
        ORD = "116 104 105 115 32 105 115 32 97 32 116 101 115 116"
        self.assertEqual(codecs.encode(STR, "ordinal"), ORD)
        self.assertEqual(codecs.encode(b(STR), "ordinals"), b(ORD))
        self.assertEqual(codecs.decode(ORD, "ordinals"), STR)
        self.assertEqual(codecs.decode(b(ORD), "ordinal"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "bad ord string", "ordinal")
