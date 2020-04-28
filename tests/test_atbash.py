#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Atbash codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecAtbash(TestCase):
    def test_codec_atbash(self):
        STR = "this is a test"
        ATB1 = "HTSIaSIa aHWIH"
        self.assertRaises(ValueError, codecs.encode, "test", "atbash-whatever")
        self.assertIsNotNone(codecs.encode("test", "atbash-whatevers"))
        # uses by default an alphabet with lowercase and uppercase
        self.assertEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-?l?u?s"))
        self.assertEqual(codecs.encode(STR, "atbash_cipher"), ATB1)
        self.assertEqual(codecs.encode(b(STR), "atbash-cipher"), b(ATB1))
        self.assertEqual(codecs.decode(ATB1, "atbash"), STR)
        self.assertEqual(codecs.decode(b(ATB1), "atbash"), b(STR))
        ATB2 = ".^]/a]/a a.{/."
        self.assertEqual(codecs.encode(STR, "atbash-?l?u?p?s"), ATB2)
        self.assertEqual(codecs.encode(b(STR), "atbash_cipher-?l?u?p?s"), b(ATB2))
        self.assertEqual(codecs.decode(ATB2, "atbash-?l?u?p?s"), STR)
        self.assertEqual(codecs.decode(b(ATB2), "atbash_cipher-?l?u?p?s"), b(STR))
        # trying to decode with a non-matching alphabet
        self.assertRaises(ValueError, codecs.decode, ATB2, "atbash")
