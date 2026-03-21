#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Manual codec tests.

"""
import os
import random
from unittest import TestCase

from codext.__common__ import *
from codext.binary.baudot import _check_alphabet
from codext.hashing.checksums import CRC


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
        STR = "This is a test"
        ATB1 = "Gsrh rh z gvhg"
        self.assertIsNotNone(codecs.encode("test", "atbash-whatevers"))
        # uses by default an alphabet with lowercase and uppercase
        self.assertEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-?l?u"))
        self.assertNotEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-[?l?u]"))
        self.assertEqual(codecs.encode(STR, "atbash_cipher"), ATB1)
        self.assertEqual(codecs.encode(b(STR), "atbash-cipher"), b(ATB1))
        self.assertEqual(codecs.decode(ATB1, "atbash"), STR)
        self.assertEqual(codecs.decode(b(ATB1), "atbash"), b(STR))
        ATB2 = "N^]/a]/a a.{/."
        self.assertEqual(codecs.encode(STR, "atbash-[?l?u?p?s]"), ATB2)
        self.assertEqual(codecs.encode(b(STR), "atbash_cipher-[?l?u?p?s]"), b(ATB2))
        self.assertEqual(codecs.decode(ATB2, "atbash-[?l?u?p?s]"), STR)
        self.assertEqual(codecs.decode(b(ATB2), "atbash_cipher-[?l?u?p?s]"), b(STR))
    
    def test_codec_case_related_manips(self):
        STR = "This is a test"
        self.assertEqual(codecs.encode(STR, "lower"), "this is a test")
        self.assertEqual(codecs.encode(b(STR), "uppercase"), b("THIS IS A TEST"))
        self.assertEqual(codecs.encode(STR, "capitalize"), "This is a test")
        self.assertEqual(codecs.decode(b(STR), "capitalize"), b("this is a test"))
        self.assertEqual(codecs.encode(STR, "title"), "This Is A Test")
        self.assertEqual(codecs.decode(b(STR), "title"), b("this is a test"))
        self.assertEqual(codecs.encode(b(STR), "swapcase"), b("tHIS IS A TEST"))
        self.assertEqual(codecs.encode(b(STR), "camelcase"), b("thisIsATest"))
        self.assertEqual(codecs.encode(b(STR), "kebabcase"), b("this-is-a-test"))
        self.assertEqual(codecs.encode(b(STR), "pascalcase"), b("ThisIsATest"))
        self.assertEqual(codecs.encode(b(STR), "slugify"), b("this-is-a-test"))
        self.assertEqual(codecs.encode(b(STR), "snakecase"), b("this_is_a_test"))
        self.assertRaises(NotImplementedError, codecs.decode, STR, "camel")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "pascal")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "slug")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "snake")
    
    def test_codec_dummy_str_manips(self):
        STR = "this is a test"
        self.assertEqual(codecs.decode(STR, "reverse"), "tset a si siht")
        self.assertEqual(codecs.decode(STR, "reverse_words"), "siht si a tset")
        self.assertEqual(codecs.decode(STR.split()[0], "reverse"), codecs.decode(STR.split()[0], "reverse-words"))
        self.assertEqual(codecs.encode(STR, "replace-i1"), STR.replace("i", "1"))
        self.assertEqual(codecs.decode(STR.replace("i", "1"), "replace-1i"), STR)
        self.assertEqual(codecs.encode(STR, "substitute-this/that"), STR.replace("this", "that"))
        self.assertEqual(codecs.decode(STR.replace("this", "that"), "substitute-that/this"), STR)
        self.assertEqual(codecs.encode(STR, "tokenize-2"), "th is  i s  a  te st")
        self.assertRaises(LookupError, codecs.encode, STR, "tokenize-200")
    
    def test_codec_hash_functions(self):
        STR = b"This is a test string!"
        for h in ["adler32", "md2", "md5", "sha1", "sha224", "sha256", "sha384", "sha512"]:
            self.assertIsNotNone(codecs.encode(STR, h))
            self.assertRaises(NotImplementedError, codecs.decode, STR, h)
        self.assertEqual(len(codecs.encode(STR, "blake2b_64")), 128)
        self.assertRaises(LookupError, codecs.encode, STR, "blake2b_0")
        self.assertRaises(LookupError, codecs.encode, STR, "blake2b-65")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "blake2b")
        self.assertEqual(len(codecs.encode(STR, "blake2s_32")), 64)
        self.assertRaises(LookupError, codecs.encode, STR, "blake2s_0")
        self.assertRaises(LookupError, codecs.encode, STR, "blake2s-33")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "blake2s")
        self.assertIsNotNone(codecs.encode(STR, "shake128"))
        self.assertRaises(LookupError, codecs.encode, STR, "shake128_0")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "shake128")
        self.assertIsNotNone(codecs.encode(STR, "shake256"))
        self.assertRaises(LookupError, codecs.encode, STR, "shake256-0")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "shake256")
        for h in ["sha3_224", "sha3_256", "sha3_384", "sha3_512"]:
            self.assertIsNotNone(codecs.encode(STR, h))
            self.assertRaises(NotImplementedError, codecs.decode, STR, h)
        if UNIX:
            try:
                import crypt
            except ImportError:
                try:
                    import legacycrypt as crypt
                except ImportError:
                    crypt = None
            METHODS = [x[7:].lower() for x in crypt.__dict__ if x.startswith("METHOD_")] \
                      if crypt is not None else []
            for m in METHODS:
                h = "crypt-" + m
                self.assertIsNotNone(codecs.encode(STR, h))
                self.assertRaises(NotImplementedError, codecs.decode, STR, h)
        # CRC checks
        STR = "123456789"
        for n, variants in CRC.items():
            for name, params in variants.items():
                enc = ("crc%d-%s" % (n, name) if isinstance(n, int) else "crc-%s" % name).rstrip("-")
                print(enc)
                self.assertEqual(codecs.encode(STR, enc), "%0{}x".format(round((n or 16)/4+.5)) % params[5])
    
    def test_codec_markdown(self):
        HTM = "<h1>Test title</h1>\n\n<p>Test paragraph</p>\n"
        MD  = "# Test title\n\nTest paragraph"
        TFILE = "test-codec-markdown.html"
        self.assertTrue(isinstance(codecs.encode(MD, "markdown"), str))
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
        # in this special case, the whitespaces between words cannot be encoded because:
        # - ord(" ") == 32
        # - the next minimal value in the printable characters excluding the latest 6 is ord("!") == 33
        # and therefore ord(" ")-random(0,20)-random(0,20) will never fall into the valid ordinals !
        self.assertRaises(ValueError, codecs.encode, "this is a test", "whitespace-after-before")
        self.assertIn("\x00", codecs.encode("this is a test", "whitespace-after-before", "replace"))

    def test_codec_vigenere(self):
        STR = "attack at dawn"
        ENC = "lxfopv ef rnhr"
        self.assertEqual(codecs.encode(STR, "vigenere-lemon"), ENC)
        self.assertEqual(codecs.encode(b(STR), "vigenere-lemon"), b(ENC))
        self.assertEqual(codecs.decode(ENC, "vigenere-lemon"), STR)
        self.assertEqual(codecs.decode(b(ENC), "vigenere-lemon"), b(STR))
        # test with uppercase input
        STR2 = "Attack At Dawn"
        ENC2 = "Lxfopv Ef Rnhr"
        self.assertEqual(codecs.encode(STR2, "vigenere-lemon"), ENC2)
        self.assertEqual(codecs.decode(ENC2, "vigenere-lemon"), STR2)
        # key case should not matter
        self.assertEqual(codecs.encode(STR, "vigenere-LEMON"), ENC)
        self.assertEqual(codecs.encode(STR, "vigenere-Lemon"), ENC)
        # test roundtrip with another key
        self.assertEqual(codecs.decode(codecs.encode(STR, "vigenere-key"), "vigenere-key"), STR)

    def test_codec_polybius(self):
        STR = "this is a test"
        ENC = "44 23 24 43 / 24 43 / 11 / 44 15 43 44"
        self.assertEqual(codecs.encode(STR, "polybius"), ENC)
        self.assertEqual(codecs.encode(b(STR), "polybius"), b(ENC))
        self.assertEqual(codecs.decode(ENC, "polybius"), STR)
        self.assertEqual(codecs.decode(b(ENC), "polybius"), b(STR))
        # test alias
        self.assertEqual(codecs.encode(STR, "polybius-square"), ENC)
        # I and J share the same code
        self.assertEqual(codecs.encode("i", "polybius"), codecs.encode("j", "polybius"))
        # test uppercase input
        self.assertEqual(codecs.encode("THIS", "polybius"), codecs.encode("this", "polybius"))

    def test_codec_multitap(self):
        STR = "this is a test"
        ENC = "8-44-444-7777 / 444-7777 / 2 / 8-33-7777-8"
        self.assertEqual(codecs.encode(STR, "multitap"), ENC)
        self.assertEqual(codecs.encode(b(STR), "multitap"), b(ENC))
        self.assertEqual(codecs.decode(ENC, "multitap"), STR)
        self.assertEqual(codecs.decode(b(ENC), "multitap"), b(STR))
        # test alias
        self.assertEqual(codecs.encode(STR, "multi-tap"), ENC)
        # uppercase should produce same codes as lowercase
        self.assertEqual(codecs.encode("THIS", "multitap"), codecs.encode("this", "multitap"))

    def test_codec_quoted_printable(self):
        STR = "Subject: =?UTF-8?"
        ENC = "Subject: =3D?UTF-8?"
        self.assertEqual(codecs.encode(STR, "quoted-printable"), ENC)
        self.assertEqual(codecs.decode(ENC, "quoted-printable"), STR)
        # test aliases
        self.assertIsNotNone(codecs.encode(STR, "qp"))
        self.assertIsNotNone(codecs.encode(STR, "quopri"))
        # plain ASCII roundtrip
        self.assertEqual(codecs.decode(codecs.encode("hello world", "qp"), "qp"), "hello world")

