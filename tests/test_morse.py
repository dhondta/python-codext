#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Morse codec tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecMorse(TestCase):
    def test_codec_morse(self):
        STR = "this is a test"
        STRB = STR + "#"
        MRS  = "- .... .. ... / .. ... / .- / - . ... -"
        MRSB = MRS + " .........."
        TFILE = "test-codec-morse.txt"
        self.assertTrue(isinstance(codecs.encode(STR, "morse"), string_types))
        self.assertEqual(codecs.encode(STR, "morse"), MRS)
        self.assertRaises(ValueError, codecs.encode, STRB, "morse")
        self.assertIsNotNone(codecs.encode(STRB, "morse", "replace"))
        self.assertIsNotNone(codecs.encode(STRB, "morse", "ignore"))
        self.assertRaises(ValueError, codecs.decode, MRSB, "morse")
        self.assertIsNotNone(codecs.decode(MRSB, "morse", "replace"))
        self.assertIsNotNone(codecs.decode(MRSB, "morse", "ignore"))
        self.assertIsNotNone(codecs.encode(STR, "morse", "BAD_ERRORS"))
        self.assertRaises(ValueError, codecs.encode, "#", "morse", "BAD_ERRORS")
        self.assertRaises(ValueError, codecs.decode, "#", "morse", "BAD_ERRORS")
        self.assertTrue(not PY3 or
                        isinstance(codecs.encode(b(STR), "morse"), binary_type))
        with codecs.open(TFILE, 'w', encoding="morse") as f:
            f.write(b(STR))
        with codecs.open(TFILE, encoding="morse") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        os.remove(TFILE)
