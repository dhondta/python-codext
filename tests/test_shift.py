#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Shift codecs tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecsShift(TestCase):
    def test_codec_shift(self):
        STR = "this is a test"
        SH1 = "uijt!jt!b!uftu"
        SH9 = "}qr|)r|)j)}n|}"
        TFILE = "test-codec-shift.txt"
        self.assertTrue(isinstance(codecs.encode(STR, "shift-200"), string_types))
        self.assertEqual(codecs.encode(STR, "shift_1"), codecs.decode(STR, "shift_255"))
        self.assertEqual(codecs.encode(STR, "ord-shift_1"), SH1)
        self.assertEqual(codecs.encode(STR, "ordinal_shift-1"), SH1)
        self.assertEqual(codecs.encode(STR, "shift1"), SH1)
        self.assertEqual(codecs.encode(STR, "ordshift1"), SH1)
        self.assertEqual(codecs.encode(STR, "ordinalshift1"), SH1)
        self.assertEqual(codecs.encode(STR, "shift_9"), SH9)
        self.assertEqual(codecs.encode(STR, "ord_shift_9"), SH9)
        self.assertEqual(codecs.encode(STR, "ord-shift-9"), SH9)
        self.assertEqual(codecs.decode(SH1, "shift1"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "shift0")
        self.assertRaises(LookupError, codecs.decode, STR, "shift--10")
        self.assertRaises(LookupError, codecs.decode, STR, "shift256")
        self.assertRaises(LookupError, codecs.decode, STR, "shift300")
        s = STR
        for i in range(1, 256):
            old = s
            s = codecs.encode(s, "shift1")
            self.assertEqual(codecs.decode(s, "shift1"), old)
        self.assertTrue(not PY3 or isinstance(codecs.encode(b(STR), "shift1"), binary_type))
        with codecs.open(TFILE, 'w', encoding="shift-1") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read()
        self.assertEqual(SH1, r)
        with codecs.open(TFILE, encoding="shift-1") as f:
            s = f.read()
        self.assertEqual(STR, ensure_str(s))
        os.remove(TFILE)
