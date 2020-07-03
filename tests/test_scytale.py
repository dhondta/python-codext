#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Scytale-N codecs tests.

"""
import os
from unittest import TestCase

from codext.__common__ import *


class TestCodecsScytale(TestCase):
    def test_codecs_scytale(self):
        STR = "this is a test"
        SC2 = "ti satshsi  et"
        SC5 = "tithsei ssat  "
        TFILE = "test-codec-scytale.txt"
        self.assertEqual(codecs.encode(STR, "scytale2"), SC2)
        self.assertEqual(codecs.encode(STR, "scytale-2"), SC2)
        self.assertEqual(codecs.encode(STR, "scytale_2"), SC2)
        self.assertEqual(codecs.encode(STR, "scytale-5"), SC5)
        self.assertEqual(codecs.encode(STR, "scytale_5"), SC5)
        self.assertEqual(codecs.decode(SC5, "scytale5"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "scytale0")
        self.assertRaises(LookupError, codecs.decode, STR, "scytale--10")
        self.assertRaises(LookupError, codecs.decode, STR, "scytale01")
        with codecs.open(TFILE, 'w', encoding="scytale-5") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read()
        self.assertEqual(SC5, r)
        with codecs.open(TFILE, encoding="scytale-5") as f:
            s = f.read()
        self.assertEqual(STR, ensure_str(s))
        os.remove(TFILE)

