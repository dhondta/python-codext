#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Baudot codec tests.

"""
from unittest import TestCase

from codext.__common__ import *
from codext.others.baudot import _check_alphabet


class TestCodecBaudot(TestCase):
    def test_codec_baudot(self):
        self.assertRaises(ValueError, _check_alphabet, ["BAD_ALPHABET"])
        STR = "TEST 1234"
        ENC = {
            'ccitt2_lsb': "00001100001010000001001001101111101110011000001010",
            'ita1':       "10101000101010010101100000100000001000100010000101",
            'ita2_msb':   "10000000010010110000001001101110111100110000101010",
            'ita2_us':    "10000000010010110000001001101110111100110000101010",
        }
        if PY3:
            ENC['ccitt1_lsb'] = "101010001010001101010100000100000100000100101"
            ENC['fr'] = "10101000101010010101100000100000001000100010000101"
            self.assertEqual(codecs.encode(STR, "baudot_ccitt1-lsb", "ignore"), ENC['ccitt1_lsb'])
        self.assertRaises(LookupError, codecs.encode, STR, "baudot_DOES_NOT_EXIST")
        self.assertEqual(codecs.encode("TEST ", "baudot_ccitt1", "ignore"), "10101010001000110101")
        self.assertEqual(codecs.encode("TEST ", "baudot_fr"), "1010100010101001010110000")
        self.assertRaises(ValueError, codecs.encode, "abc", "baudot")
        self.assertRaises(ValueError, codecs.encode, STR, "baudot_ccitt1-lsb")  # CCITT-1 does not support whitespace
        for code, result in ENC.items():
            if "ccitt1" in code:
                continue
            self.assertEqual(codecs.encode(STR, "baudot_" + code), result)
            self.assertEqual(codecs.encode(b(STR), "baudot_" + code), b(result))
            self.assertEqual(codecs.encode(STR + "test", "baudot_" + code, "ignore"), result)
            self.assertEqual(codecs.decode(result, "baudot_" + code), STR)
            self.assertEqual(codecs.decode(b(result), "baudot_" + code), b(STR))

    def test_codec_baudot_spaced(self):
        STR = "TEST 1234"
        ENC = {
            'ccitt2_lsb': "00001 10000 10100 00001 00100 11011 11101 11001 10000 01010",
            'ita1':       "10101 00010 10100 10101 10000 01000 00001 00010 00100 00101",
            'ita2_msb':   "10000 00001 00101 10000 00100 11011 10111 10011 00001 01010",
            'ita2_us':    "10000 00001 00101 10000 00100 11011 10111 10011 00001 01010",
        }
        if PY3:
            ENC['ccitt1_lsb'] = "10101 00010 10001 10101 01000 00100 00010 00001 00101"
            ENC['fr'] = "10101 00010 10100 10101 10000 01000 00001 00010 00100 00101"
        self.assertRaises(ValueError, codecs.encode, "abc", "baudot-spaced")
        self.assertRaises(ValueError, codecs.encode, STR, "baudot-spaced_ccitt1-lsb")
        for code, result in ENC.items():
            if "ccitt1" in code:
                continue
            self.assertEqual(codecs.encode(STR, "baudot-spaced_" + code), result)
            self.assertEqual(codecs.encode(b(STR), "baudot-spaced_" + code), b(result))
            self.assertEqual(codecs.encode(STR + "test", "baudot-spaced_" + code, "ignore"), result)
            self.assertEqual(codecs.decode(result, "baudot-spaced_" + code), STR)
            self.assertEqual(codecs.decode(b(result), "baudot-spaced_" + code), b(STR))
    
    def test_codec_baudot_tape(self):
        STR = "TEST 1234"
        ITA1_TAPE = "***.**\n* *. *\n   .* \n* *.  \n* *. *\n*  .  \n * .  \n   . *\n   .* \n  *.  \n  *. *"
        self.assertEqual(codecs.encode(STR, "baudot-tape_ita1"), ITA1_TAPE)
        self.assertEqual(codecs.decode(ITA1_TAPE, "baudot-tape_ita1"), STR)
        self.assertEqual(codecs.decode(ITA1_TAPE, "baudot-tape_ita1"), STR)
        self.assertEqual(codecs.decode(b(ITA1_TAPE), "baudot-tape_ita1"), b(STR))
        self.assertRaises(ValueError, codecs.decode, "BAD_TAPE\n", "baudot-tape_fr")
        self.assertRaises(ValueError, codecs.decode, "***.**\nBAD_TAPE\n", "baudot-tape_fr")
        self.assertRaises(ValueError, codecs.decode, "***.**\n   .* \n*  . *\n*  .  \n", "baudot_tape-ccitt1_lsb")

