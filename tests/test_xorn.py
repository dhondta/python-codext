#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""XOR-N codecs tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecsXORN(TestCase):
    def test_codec_xorn(self):
        STR = "this is a test"
        XR3 = "wkjp#jp#b#wfpw"
        XR6 = "rnou&ou&g&rcur"
        TFILE = "test-codec-xorn.txt"
        self.assertTrue(isinstance(codecs.encode(STR, "xor200"), string_types))
        self.assertEqual(codecs.encode(STR, "xor3"), XR3)
        self.assertEqual(codecs.encode(STR, "xor-3"), XR3)
        self.assertEqual(codecs.encode(STR, "xor_3"), XR3)
        self.assertEqual(codecs.encode(STR, "XOR6"), XR6)
        self.assertEqual(codecs.encode(STR, "XOR-6"), XR6)
        self.assertEqual(codecs.encode(STR, "XOR_6"), XR6)
        self.assertEqual(codecs.decode(XR3, "xor3"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "xor0")
        self.assertRaises(LookupError, codecs.decode, STR, "xor--10")
        self.assertRaises(LookupError, codecs.decode, STR, "xor256")
        self.assertRaises(LookupError, codecs.decode, STR, "xor300")
        s = STR
        for i in range(1, 256):
            old = s
            s = codecs.encode(s, "xor1")
            self.assertEqual(codecs.decode(s, "xor1"), old)
        self.assertTrue(not PY3 or
                        isinstance(codecs.encode(b(STR), "xor1"), binary_type))
        if PY3:
            with open(TFILE, 'w', encoding="xor-3") as f:
                f.write(STR)
            with open(TFILE) as f:
                r = f.read().strip()
            self.assertEqual(XR3, r)
            with open(TFILE, encoding="xor-3") as f:
                s = f.read().strip()
            self.assertEqual(STR, s)
        with codecs.open(TFILE, 'w', encoding="xor-3") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read().strip()
        self.assertEqual(XR3, r)
        with codecs.open(TFILE, encoding="xor-3") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        os.remove(TFILE)
