#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Barbie codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecBarbie(TestCase):
    def test_codec_barbie(self):
        STR = "this is a test"
        BRB = ["hstf tf i hafh", "sfhp hp t sips", "fpsu su h ftuf",
               "pufq fq s phqp"]
        self.assertRaises(LookupError, codecs.encode, STR, "barbie")
        for i in range(4):
            self.assertEqual(codecs.encode(STR, "barbie{}".format(i+1)), BRB[i])
        self.assertEqual(codecs.encode(b(STR), "barbie_1"), b(BRB[0]))
        self.assertEqual(codecs.encode(b(STR), "barbie-2"), b(BRB[1]))
        self.assertRaises(ValueError, codecs.encode, "\r", "barbie-2")
        self.assertRaises(ValueError, codecs.decode, "\r", "barbie-4")
        self.assertIsNotNone(codecs.encode("test\r", "barbie-3", "replace"))
        self.assertIsNotNone(codecs.decode("test\r", "barbie-1", "replace"))
        self.assertIsNotNone(codecs.encode("test\r", "barbie-3", "ignore"))
        self.assertIsNotNone(codecs.decode("test\r", "barbie-1", "ignore"))
        self.assertRaises(ValueError, codecs.encode, "\r", "barbie-2", "BAD")
        self.assertRaises(ValueError, codecs.decode, "\r", "barbie-4", "BAD")
