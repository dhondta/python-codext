#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Manual codec tests.

"""
import os
import random
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *
from codext.binary.baudot import _check_alphabet


class ComplementaryTestCase(TestCase):
    def test_codec_baudot(self):
        self.assertRaises(ValueError, _check_alphabet, ["BAD_ALPHABET"])
    
    def test_codec_dna(self):
        self.assertEqual(codecs.decode("ABC", "dna-1", errors="ignore"), "\x02")
        self.assertEqual(codecs.decode("ABC", "dna-2", errors="replace"), "[00??01]")
    
    def test_codec_morse(self):
        self.assertRaises(LookupError, codecs.encode, "test", "morse-AAB")
    
    def test_codec_sms(self):
        self.assertEqual(codecs.decode("A-B-222-3-4-5", "sms", "leave"), "ABcdgj")


class ManualTestCase(TestCase):
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
    
    def test_codec_atbash(self):
        STR = "this is a test"
        ATB1 = "HTSIaSIa aHWIH"
        self.assertRaises(ValueError, codecs.encode, "test", "atbash-whatever")
        self.assertIsNotNone(codecs.encode("test", "atbash-whatevers"))
        # uses by default an alphabet with lowercase and uppercase
        self.assertEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-?l?u?s"))
        self.assertEqual(codecs.encode(STR, "atbash_cipher"), ATB1)
        self.assertEqual(codecs.encode(b(STR), "atbash-cipher"), b(ATB1))
        self.assertEqual(codecs.decode(ATB1, "atbash"), STR)
        self.assertEqual(codecs.decode(b(ATB1), "atbash"), b(STR))
        ATB2 = ".^]/a]/a a.{/."
        self.assertEqual(codecs.encode(STR, "atbash-?l?u?p?s"), ATB2)
        self.assertEqual(codecs.encode(b(STR), "atbash_cipher-?l?u?p?s"), b(ATB2))
        self.assertEqual(codecs.decode(ATB2, "atbash-?l?u?p?s"), STR)
        self.assertEqual(codecs.decode(b(ATB2), "atbash_cipher-?l?u?p?s"), b(STR))
        # trying to decode with a non-matching alphabet
        self.assertRaises(ValueError, codecs.decode, ATB2, "atbash")
    
    def test_codec_dummy_str_manips(self):
        STR = "this is a test"
        self.assertEqual(codecs.encode(STR, "lower"), STR)
        self.assertEqual(codecs.encode(b(STR), "uppercase"), b("THIS IS A TEST"))
        self.assertEqual(codecs.decode(STR, "reverse"), "tset a si siht")
        self.assertEqual(codecs.decode(STR, "reverse_words"), "siht si a tset")
        self.assertEqual(codecs.decode(STR.split()[0], "reverse"), codecs.decode(STR.split()[0], "reverse-words"))
        self.assertEqual(codecs.encode(STR, "capitalize"), "This is a test")
        self.assertEqual(codecs.decode(b(STR), "capitalize"), b(STR))
        self.assertEqual(codecs.encode(STR, "title"), "This Is A Test")
        self.assertEqual(codecs.decode(b(STR), "title"), b(STR))
        self.assertEqual(codecs.encode(b(STR), "swapcase"), b("THIS IS A TEST"))
    
    def test_codec_markdown(self):
        HTM = "<h1>Test title</h1>\n\n<p>Test paragraph</p>\n"
        MD  = "# Test title\n\nTest paragraph"
        TFILE = "test-codec-markdown.html"
        self.assertTrue(isinstance(codecs.encode(MD, "markdown"), string_types))
        self.assertTrue(not PY3 or isinstance(codecs.encode(b(MD), "markdown"), binary_type))
        self.assertEqual(codecs.encode(MD, "markdown"), HTM)
        self.assertRaises(NotImplementedError, codecs.decode, MD, "markdown")
        with codecs.open(TFILE, 'w', encoding="markdown") as f:
            f.write(b(MD))
        with codecs.open(TFILE) as f:
            s = f.read()
        self.assertEqual(HTM, ensure_str(s))
        os.remove(TFILE)
    
    def test_codec_whitespace_after_before(self):
        STR = "test"
        for i in range(100):
            c = "whitespace{}{}*after{}{}*before".format("-+"[random.randint(0, 1)], random.randint(1, 3),
                                                         "-+"[random.randint(0, 1)], random.randint(1, 3))
            self.assertEqual(codecs.decode("\n" + codecs.encode(STR, c) + "\n", c), STR)

