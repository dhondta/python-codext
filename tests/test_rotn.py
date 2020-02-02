#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Rot-N codecs tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecsRotN(TestCase):
    def test_codecs_rotn(self):
        STR = "this is a test"
        RT1 = "uijt jt b uftu"
        RT3 = "wklv lv d whvw"
        TFILE = "test-codec-rotn.txt"
        self.assertTrue(isinstance(codecs.encode(STR, "rot12"), string_types))
        self.assertEqual(codecs.encode(STR, "rot1"), RT1)
        self.assertEqual(codecs.encode(STR, "rot-1"), RT1)
        self.assertEqual(codecs.encode(STR, "rot_1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT-1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT_1"), RT1)
        self.assertEqual(codecs.decode(RT1, "rot1"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "rot0")
        self.assertRaises(LookupError, codecs.decode, STR, "rot--10")
        self.assertRaises(LookupError, codecs.decode, STR, "rot100")
        s = STR
        for i in range(1, 26):
            old = s
            s = codecs.encode(s, "rot1")
            self.assertEqual(codecs.decode(s, "rot1"), old)
        self.assertTrue(not PY3 or
                        isinstance(codecs.encode(b(STR), "rot1"), binary_type))
        with codecs.open(TFILE, 'w', encoding="rot-3") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read().strip()
        self.assertEqual(RT3, r)
        with codecs.open(TFILE, encoding="rot-3") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        os.remove(TFILE)
