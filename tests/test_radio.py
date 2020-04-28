#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Radio codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecRadio(TestCase):
    def test_codec_radio(self):
        STR = "FOOBAR"
        RAD = "foxtrot oscar oscar bravo alpha romeo"
        self.assertEqual(codecs.encode(STR, "nato_phonetic_alphabet"), RAD)
        self.assertEqual(codecs.encode(b(STR), "military_alphabet"), b(RAD))
        self.assertEqual(codecs.decode(RAD.title(), "nato_alphabet"), STR)
        self.assertEqual(codecs.decode(b(RAD.upper()), "radio-alphabet"), b(STR))
