#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Braille codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


if PY3:
    class TestCodecBraille(TestCase):
        def test_codec_braille(self):
            STR = "this is a test"
            BRA = "⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞"
            self.assertEqual(codecs.encode(STR, "braille"), BRA)
            self.assertEqual(codecs.encode(STR, "braille"), codecs.encode(STR.upper(), "braille"))
            self.assertEqual(codecs.encode(b(STR), "braille"), b(BRA))
            self.assertEqual(codecs.decode(BRA, "braille"), STR)
            self.assertEqual(codecs.decode(b(BRA), "braille"), b(STR))
