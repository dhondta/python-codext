#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Leetspeak codec tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecLeetspeak(TestCase):
    def test_codec_leetspeak(self):
        STR = "this is a test"
        LTS = "7H15 15 4 7357"
        TFILE = "test-codec-leetspeak.txt"
        self.assertTrue(isinstance(codecs.encode(STR, "leet"), string_types))
        self.assertEqual(codecs.encode(STR, "leet").upper(), LTS)
        self.assertEqual(codecs.encode(STR, "1337").upper(), LTS)
        self.assertEqual(codecs.encode(STR, "leetspeak").upper(), LTS)
        self.assertTrue(not PY3 or isinstance(codecs.encode(b(LTS), "leet"), binary_type))
        with codecs.open(TFILE, 'w', encoding="leet") as f:
            f.write(b(STR))
        with codecs.open(TFILE, encoding="leet") as f:
            s = f.read().strip()
        self.assertEqual(STR.upper(), ensure_str(s.upper()))
        os.remove(TFILE)
