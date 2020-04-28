#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Affine codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecAffine(TestCase):
    def test_codec_affine(self):
        STR = "this is a test"
        AFF1 = "vjkubkubcbvguv"
        self.assertRaises(LookupError, codecs.encode, STR, "affine-BAD")
        self.assertRaises(LookupError, codecs.encode, STR, "affine-?l?u-BAD")
        # uses by default an alphabet with lowercase, uppercase, whitespace and parameters a=1 and b=2
        self.assertEqual(codecs.encode(STR, "affine"), codecs.encode(STR, "affine-?l?u?s-1,2"))
        self.assertEqual(codecs.encode(STR, "affine"), AFF1)
        self.assertEqual(codecs.encode(b(STR), "affine"), b(AFF1))
        self.assertEqual(codecs.decode(AFF1, "affine"), STR)
        self.assertEqual(codecs.decode(b(AFF1), "affine"), b(STR))
        AFF2 = "ORWJdWJdidOCJO"
        self.assertEqual(codecs.encode(STR, "affine-?l?u?d?s-5,8"), AFF2)
        self.assertEqual(codecs.encode(b(STR), "affine-?l?u?d?s-5,8"), b(AFF2))
        self.assertEqual(codecs.decode(AFF2, "affine-?l?u?d?s-5,8"), STR)
        self.assertEqual(codecs.decode(b(AFF2), "affine-?l?u?d?s-5,8"), b(STR))
        AFF3 = "QsuOcuOcecQmOQ"
        self.assertEqual(codecs.encode(STR, "affine-?l?u?d?s-2,4"), AFF3)
        self.assertEqual(codecs.encode(b(STR), "affine-?l?u?d?s-2,4"), b(AFF3))
        self.assertEqual(codecs.decode(AFF3, "affine-?l?u?d?s-2,4"), STR)
        self.assertEqual(codecs.decode(b(AFF3), "affine-?l?u?d?s-2,4"), b(STR))
        self.assertRaises(ValueError, codecs.decode, ".BAD.", "affine-?l?u?d?s-2,4")
        self.assertIsNotNone(codecs.encode("TEST", "affine_?u-1,2"))
        # example of parameters that cause mapping collisions
        self.assertRaises(LookupError, codecs.encode, STR, "affine-?l?u?d?s-6,8")
