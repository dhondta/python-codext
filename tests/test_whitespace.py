#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Whitespace codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


if PY3:
    class TestCodecWhitespace(TestCase):
        def test_codec_whitespace(self):
            STR = "test"
            WSP1 = "\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t"
            WSP2 = " \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  "
            self.assertEqual(codecs.encode(STR, "whitespace"), WSP1)
            self.assertEqual(codecs.encode(b(STR), "whitespace"), b(WSP1))
            self.assertEqual(codecs.encode(STR, "whitespace-inv"), WSP2)
            self.assertEqual(codecs.encode(b(STR), "whitespace_inverted"), b(WSP2))
            self.assertEqual(codecs.decode(WSP1, "whitespace"), STR)
            self.assertEqual(codecs.decode(b(WSP1), "whitespace"), b(STR))
            self.assertEqual(codecs.decode(WSP2, "whitespace_inv"), STR)
            self.assertEqual(codecs.decode(b(WSP2), "whitespace-inverted"), b(STR))
