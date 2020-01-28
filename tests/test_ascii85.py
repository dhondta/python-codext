#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Ascii85 codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecAscii85(TestCase):
    def test_codec_ascii85(self):
        if PY3:
            STR = "this is a test"
            A85 = "FD,B0+DGm>@3BZ'F*%"
            self.assertEqual(codecs.encode(STR, "ascii85"), A85)
            self.assertEqual(codecs.encode(b(STR), "ascii85"), b(A85))
            self.assertEqual(codecs.decode(A85, "ascii85"), STR)
            self.assertEqual(codecs.decode(b(A85), "ascii85"), b(STR))
