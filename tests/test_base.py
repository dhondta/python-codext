#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Base codecs tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecsBase(TestCase):
    def setUp(self):
        global STR
        STR = "this is a test"
    
    def test_codec_base16(self):
        B16 = "7468697320697320612074657374"
        self.assertEqual(codecs.encode(STR, "base16"), B16)
        self.assertEqual(codecs.encode(b(STR), "base16"), b(B16))
        self.assertEqual(codecs.decode(B16, "base16"), STR)
        self.assertEqual(codecs.decode(b(B16), "base16"), b(STR))
    
    def test_codec_base32(self):
        B32 = "ORUGS4ZANFZSAYJAORSXG5A="
        self.assertEqual(codecs.encode(STR, "base32"), B32)
        self.assertEqual(codecs.encode(b(STR), "base32"), b(B32))
        self.assertEqual(codecs.decode(B32, "base32"), STR)
        self.assertEqual(codecs.decode(b(B32), "base32"), b(STR))
    
    def test_codec_base64(self):
        B64 = "dGhpcyBpcyBhIHRlc3Q="
        self.assertEqual(codecs.encode(STR, "base64"), B64)
        self.assertEqual(codecs.encode(b(STR), "base64"), b(B64))
        self.assertEqual(codecs.decode(B64, "base64"), STR)
        self.assertEqual(codecs.decode(b(B64), "base64"), b(STR))
    
    def test_codec_base85(self):
        if PY3:
            B85 = "bZBXFAZc?TVIXv6b94"
            self.assertEqual(codecs.encode(STR, "base85"), B85)
            self.assertEqual(codecs.encode(b(STR), "base85"), b(B85))
            self.assertEqual(codecs.decode(B85, "base85"), STR)
            self.assertEqual(codecs.decode(b(B85), "base85"), b(STR))
    
    def test_codec_base100(self):
        if PY3:
            B100 = "\U0001f46b\U0001f45f\U0001f460\U0001f46a\U0001f417" \
                   "\U0001f460\U0001f46a\U0001f417\U0001f458\U0001f417" \
                   "\U0001f46b\U0001f45c\U0001f46a\U0001f46b"
            self.assertEqual(codecs.encode(STR, "base100"), B100)
            self.assertEqual(codecs.encode(b(STR), "base100"), b(B100))
            self.assertEqual(codecs.decode(B100, "base100"), STR)
            self.assertEqual(codecs.decode(b(B100), "base100"), b(STR))
            self.assertRaises(ValueError, codecs.decode, b(B100)[1:], "base100")
