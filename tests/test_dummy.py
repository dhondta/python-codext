#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dummy codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecDummy(TestCase):
    def test_codec_dummy_str_manips(self):
        STR = "this is a test"
        self.assertEqual(codecs.encode(STR, "lower"), STR)
        self.assertEqual(codecs.encode(b(STR), "uppercase"), b("THIS IS A TEST"))
        self.assertEqual(codecs.decode(STR, "reverse"), "tset a si siht")
        self.assertEqual(codecs.decode(STR, "reverse_words"), "siht si a tset")
        self.assertEqual(codecs.decode(STR.split()[0], "reverse"), codecs.decode(STR.split()[0], "reverse-words"))
        self.assertEqual(codecs.encode(STR, "capitalize"), "This is a test")
        self.assertEqual(codecs.decode(b(STR), "capitalize"), b(STR))
        self.assertEqual(codecs.encode(STR, "title"), "This Is A Test")
        self.assertEqual(codecs.decode(b(STR), "title"), b(STR))
        self.assertEqual(codecs.encode(b(STR), "swapcase"), b("THIS IS A TEST"))

