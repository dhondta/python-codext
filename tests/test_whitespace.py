#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Whitespace codec tests.

"""
import random
from unittest import TestCase

from codext.__common__ import *


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
    
    def test_codec_whitespace_after_before(self):
        STR = "test"
        for i in range(100):
            c = "whitespace{}{}*after{}{}*before".format("-+"[random.randint(0, 1)], random.randint(1, 3),
                                                         "-+"[random.randint(0, 1)], random.randint(1, 3))
            self.assertEqual(codecs.decode("\n" + codecs.encode(STR, c) + "\n", c), STR)

