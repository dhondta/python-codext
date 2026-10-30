#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Manual codec tests.

"""
import os
import random
from unittest import TestCase

from codext.__common__ import *


class ComplementaryTestCase(TestCase):
    def test_codec_baudot(self):
        from codext.binary.baudot import _check_alphabet
        self.assertRaises(ValueError, _check_alphabet, ["BAD_ALPHABET"])
    
    def test_codec_binhex(self):
        hqx = ":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!:"
        # in non-strict modes, CRCs are not checked and what is available from the data fork is returned
        self.assertEqual(codecs.decode(hqx[:-1], "binhex", "ignore"), "Hello")
        self.assertEqual(codecs.decode(hqx.replace("XE", "XF"), "binhex", "replace"), "Helpo")
        self.assertEqual(codecs.decode(hqx[:22] + ":", "binhex", "ignore"), "")
        self.assertEqual(codecs.decode("This is a test", "binhex", "ignore"), "")
        self.assertEqual(codecs.decode(":N!8:", "binhex", "ignore"), "")
    
    def test_codec_cow(self):
        # with a non-strict errors handling, other characters are comments and the program stops at a failing
        #  instruction
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Comment: MoO OOM then moo OOM", "cow", e), "1\n")
            self.assertEqual(codecs.decode("MoO Moo mOo Moo", "cow", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "MoO OOM comment", "cow")
        self.assertRaises(ValueError, codecs.decode, "MoO OOM comment", "cow", "BAD_ERRORS")
        from codext.esoteric.cow import cow_run
        # "MOO" with a non-null cell continues, then "moo" goes back to it forever (it skips the previous instruction,
        #  hence the "MMM" in the loop)
        self.assertRaises(ValueError, cow_run, [6, 7, 9, 0], max_steps=100)
        self.assertEqual(cow_run([6, 10, 4], max_steps=100), (b"1\n\x01", None))
    
    def test_codec_dna(self):
        self.assertEqual(codecs.decode("ABC", "dna-1", errors="ignore"), "\x02")
        self.assertEqual(codecs.decode("ABC", "dna-2", errors="replace"), "[00??01]")
    
    def test_codec_morse(self):
        self.assertRaises(LookupError, codecs.encode, "test", "morse-AAB")
    
    def test_codec_befunge(self):
        # with a non-strict errors handling, unsupported instructions are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode('"z"x,@', "befunge", e), "z")
        self.assertRaises(ValueError, codecs.decode, '"z"x,@', "befunge")
        from codext.esoteric.befunge import befunge_run
        self.assertRaises(ValueError, befunge_run, b">", max_steps=100)
        self.assertEqual(befunge_run(b"1.@", max_steps=100), b"1 ")
    
    def test_codec_brainfuck(self):
        # with a non-strict errors handling, other characters are comments and unmatched brackets are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Comment: ++. then +.]", "brainfuck", e), "\x02\x03")
            self.assertEqual(codecs.decode("+.[", "bf", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "+. comment", "brainfuck")
        self.assertRaises(ValueError, codecs.decode, "+. comment", "brainfuck", "BAD_ERRORS")
    
    def test_codec_lolcode(self):
        from codext.esoteric.lolcode import lolcode_run
        run = lambda body, **kw: lolcode_run(f"HAI 1.2\n{body}\nKTHXBYE", **kw)
        # leading and trailing newlines, a loop variable shadowing a variable, a unary function in a loop (with the
        #  syntax of the reference interpreter) and casts from and to NOOB
        self.assertEqual(lolcode_run("\n\nHAI\nVISIBLE 1\nKTHXBYE\n\n"), "1\n")
        self.assertEqual(run('I HAS A i ITZ "x"\nIM IN YR l UPPIN YR i TIL BOTH SAEM i AN 2\nIM OUTTA YR l\nVISIBLE i'),
                         "x\n")
        self.assertEqual(run("HOW IZ I inc YR x\nSUM OF x AN 1\nIF U SAY SO\nIM IN YR l I IZ inc YR i MKAY WILE "
                             "DIFFRINT i AN 3\nVISIBLE i!\nIM OUTTA YR l"), "012")
        self.assertEqual(run("VISIBLE MAEK NOOB NUMBR AN MAEK NOOB A NUMBAR\nI HAS AN x ITZ 1, x IS NOW A NOOB\n"
                             "BOTH SAEM x AN NOOB, VISIBLE IT"), "00.00\nWIN\n")
        # syntax and runtime errors
        for body in ['VISIBLE "a" ...\n\nVISIBLE "b"', "OBTW never closed", "OBTW x TLDR VISIBLE 1", 'VISIBLE "a"b',
                     "VISIBLE 1 ! 2", "I HAS A 1x", "MAEK 1 A BUKKIT", "VISIBLE", "SUM OF 1 AN", "WTF?\nOMG x\nOIC",
                     "WTF?\nOMG 1\nOMG 1\nOIC", "IM IN YR l I IZ f YR i\nIM OUTTA YR l", "VISIBLE SUM OF NOOB AN 1",
                     'VISIBLE ":(41"', 'VISIBLE ":(XYZ)"', 'VISIBLE ":[NOT A CHARACTER NAME]"', 'VISIBLE ":{x}"',
                     "I IZ f MKAY", "HOW IZ I f YR x\nIF U SAY SO\nI IZ f MKAY", "x R 1",
                     "HOW IZ I f\nI IZ f MKAY\nIF U SAY SO\nI IZ f MKAY", "VISIBLE " + "NOT " * 5000 + "WIN"]:
            self.assertRaises(ValueError, run, body)
        self.assertRaises(ValueError, lolcode_run, "HAI 1.2\nVISIBLE 1\n")
        self.assertRaises(ValueError, lolcode_run, "HAI 1.2\nVISIBLE 1\nKTHXBYE 2")
        self.assertRaises(ValueError, run, "IM IN YR l\nIM OUTTA YR l", max_steps=100)
    
    def test_codec_ook(self):
        # with a non-strict errors handling, other characters, an odd last word, "Ook? Ook?" and unmatched brackets are
        #  ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Ook. Ook. Ook! Ook. Ook? Ook? !? Ook. Ook. ?! Ook!", "ook", e), "\x01")
            self.assertEqual(codecs.decode("Comment: Ook. Ook. Ook! Ook.", "ook-short", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "Ook. Ook. Ook! Ook.!", "ook")
        self.assertRaises(ValueError, codecs.decode, "Ook? Ook?", "ook", "BAD_ERRORS")
    
    def test_codec_pikalang(self):
        # with a non-strict errors handling, unknown words and unmatched brackets are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("pi pi pikachu chu ka pikachu pika", "pikalang", e), "\x02\x01")
            self.assertEqual(codecs.decode("pi pikachu bad pi pikachu", "pikalang", e), "\x01\x02")
        self.assertRaises(ValueError, codecs.decode, "pi pika pikachu", "pikalang", "BAD_ERRORS")
        from codext.esoteric._brainfuck import bf_run
        self.assertRaises(ValueError, bf_run, "+[]", max_steps=100)
        self.assertEqual(bf_run("+[-]+.", max_steps=100), b"\x01")
    
    def test_codec_polybius(self):
        from codext.crypto.polybius import polybius_encode, polybius_decode
        self.assertRaises(LookupError, polybius_encode, "ABC")
        self.assertRaises(ValueError, polybius_decode(), "BAD_")
        self.assertRaises(ValueError, polybius_decode(), "441543441")
        self.assertEqual(codecs.decode("441543445", "polybius", "ignore"), "TEST")
    
    def test_codec_letter_indices(self):
        # bad characters are consumed when not raising an error (decoding used to loop forever)
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "ignore"), "BEC")
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "replace"), "BE?C")
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "leave"), "BE!C")
        # the errors handling applies to the encoded text too
        self.assertEqual(codecs.encode("Test!", "consonant-index", "ignore"), "16E1516")
        self.assertEqual(codecs.encode("Test!", "consonant-index", "replace"), "16E1516?")
    
    def test_codec_sms(self):
        self.assertEqual(codecs.decode("A-B-222-3-4-5", "sms", "leave"), "ABcdgj")


class ManualTestCase(TestCase):
    def test_codec_aer256(self):
        from codext.crypto._jsfloat import js_str as _js_str
        # numbers formatted as with JavaScript's String(...), as given by Node.js
        for x, r in [(0., "0"), (-0., "0"), (1e21, "1e+21"), (123456789012345680000., "123456789012345680000"),
                     (1e-6, "0.000001"), (1e-7, "1e-7"), (-1.2345e-7, "-1.2345e-7"), (2**60, "1152921504606847000"),
                     (float("nan"), "NaN"), (float("-inf"), "-Infinity"), (.1, "0.1")]:
            self.assertEqual(_js_str(x), r)
        # numbers that are not positive after decryption give no character, as with the original JavaScript
        self.assertEqual(codecs.decode("NaN, -1e+21, 175.10891089108912", "aer256-key"), "th")
        self.assertEqual(codecs.decode("x, 175.10891089108912", "aer256-key", "ignore"), "th")
        # with a long key, blocks exceed the precision of floats
        self.assertNotEqual(codecs.decode(codecs.encode("this is a test", k := "aer256-thisisaverylongkey"), k),
                            "this is a test")
        # with ARMON-64, numbers in exponent notation are not split on their "+"
        v = round((1e21 + 99) * 98 - 97)
        self.assertEqual(codecs.decode("1e+21", "armon64-abc"), bytes.fromhex(f"{v:x}").decode("latin-1"))
        self.assertEqual(codecs.decode("1e+21+1e+21", "armon64-abc"), 2 * codecs.decode("1e+21", "armon64-abc"))
    
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
    
    def test_codec_atom128(self):
        # the padding is fixed when not in strict mode (an incomplete last character being dropped)
        for s in ["0IHt0/C", "0IHt0/CCC", "0IHt0/C%"]:
            self.assertEqual(codecs.decode(s, "atom128", "ignore"), "test")
        self.assertEqual(codecs.decode("0IHt0/", "atom128", "replace"), "test")
    
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
    
    def test_codec_checksum_functions(self):
        from codext.checksums.crc import CRC
        for n, variants in CRC.items():
            for name, params in variants.items():
                enc = ("crc%d-%s" % (n, name) if isinstance(n, int) else "crc-%s" % name).rstrip("-")
                self.assertEqual(codecs.encode("123456789", enc), "%0{}x".format(round((n or 16)/4+.5)) % params[5])
        from codext.checksums.luhn import luhn
        for s, r in [("", ""), ("0", "0"), ("1", "8"), ("7992739871", "3")]:
            self.assertEqual(codecs.encode(s, "luhn"), r)
        self.assertEqual(codecs.encode("-", "luhn", errors="ignore"), "")
        # Fletcher, with the test vectors of Wikipedia ; the width defaults to 16
        for enc, vectors in {
            'fletcher|fletcher-16|fletcher_16|fletcher16': ["0000", "c8f0", "2057", "0627"],
            'fletcher32': ["00000000", "f04fc729", "56502d2a", "ebe19591"],
            'fletcher64': ["0000000000000000", "c8c6c527646362c6", "c8c72b276463c8c6", "312e2b28cccac8c6"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "abcde", "abcdef", "abcdefgh"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        self.assertRaises(LookupError, codecs.encode, "test", "fletcher8")
        self.assertRaises(NotImplementedError, codecs.decode, "c8f0", "fletcher")

    def test_codec_crc_bare_defaults(self):
        # a crc<width> used without a variant suffix must resolve to that family's default ;
        # width 16 and the crc-a family had no default and crashed with KeyError instead
        from codext.checksums.crc import CRC
        for n in CRC.keys():
            name = "crc%d" % n if isinstance(n, int) else "crc"
            expected = "%0{}x".format(round((n or 16)/4+.5)) % CRC[n][""][5]
            self.assertEqual(codecs.encode("123456789", name), expected)
            self.assertEqual(codecs.encode(b"123456789", name), b(expected))
        # bare crc-16 is CRC-16/ARC (poly 0x8005), the same as its arc/ibm/lha aliases
        for name in ["crc16", "crc-16", "crc_16", "crc16-arc", "crc16-ibm", "crc16-lha"]:
            self.assertEqual(codecs.encode("123456789", name), "bb3d")
        # bare crc is CRC-A, the same as the crca alias
        self.assertEqual(codecs.encode("123456789", "crc"), "bf05")
        self.assertEqual(codecs.encode("123456789", "crca"), "bf05")
        # adding a default must not make an unknown variant resolve
        self.assertRaises(LookupError, codecs.encode, "123456789", "crc16-bad")
        self.assertRaises(LookupError, codecs.encode, "123456789", "crc-bad")
    
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
        # FNV, with test vectors of the reference implementation ; the hash of an empty string is the offset basis,
        #  and the width defaults to 32
        for enc, vectors in {
            'fnv1|fnv-1|fnv_1-32|fnv1_32': ["811c9dc5", "050c5d7e", "31f0b262"],
            'fnv1-64': ["cbf29ce484222325", "af63bd4c8601b7be", "340d8765a4dda9c2"],
            'fnv1a|fnv-1a|fnv_1a-32|fnv1a_32': ["811c9dc5", "e40c292c", "bf9cf968"],
            'fnv1a-64': ["cbf29ce484222325", "af63dc4c8601ec8c", "85944171f73967e8"],
            'fnv1a-128': ["6c62272e07bb014262b821756295c58d"],
            'fnv1-256': ["dd268dbcaac550362d98c384c4e576ccc8b1536847b6bbb31023b4c8caee0535"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "a", "foobar"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        self.assertEqual(len(codecs.encode(STR, "fnv1a-1024")), 256)
        self.assertRaises(LookupError, codecs.encode, STR, "fnv1-16")
        self.assertRaises(LookupError, codecs.encode, STR, "fnv1a-2048")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "fnv1a")
        # SHA-0, Keccak (original padding) and MD6, with test vectors of the specifications and reference
        #  implementations
        for enc, vectors in {
            'sha0': ["f96cea198ad1dd5617ac084a3d92c6107708c0ef", "0164b8a914cd2a5e74c4f7ff082c4d97f1edf880"],
            'keccak|keccak256|keccak-256|keccak_256': [
                "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
                "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"],
            'keccak224': ["f71837502ba8e10837bdd8d365adb85591895602fc552b48b7390abd"],
            'keccak-384': ["2c23146a63a29acf99e73b88f8c24eaa7dc60aa771780ccc006afbfa8fe2479b"
                           "2dd2b21362337441ac12b515911957ff"],
            'keccak_512': ["0eab42de4c3ceb9235fc91acffe746b29c29a8c366b7c60e4e67c466f36a4304"
                           "c00fa9caf9d87976ba469bcbe06713b435f091ef2769fb160cdab33d3670680e"],
            'md6|md6256|md6-256|md6_256': ["bca38b24a804aa37d821d31af00f5598230122c5bbfc4c4ad5ed40e4258f04ca",
                                           "230637d4e6845cf0d092b558e87625f03881dd53a7439da34cf3b94ed0d8b2c5"],
            'md6-224': ["d2091aa2ad17f38c51ade2697f24cafc3894c617c77ffe10fdc7abcb",
                        "510c30e4202a5cdd8a4f2ae9beebb6f5988128897937615d52e6d228"],
            'md6-512': ["6b7f33821a2c060ecdd81aefddea2fd3c4720270e18654f4cb08ece49ccb469f"
                        "8beeee7c831206bd577f9f2630d9177979203a9489e47e04df4e6deaa0f8e0c0",
                        "00918245271e377a7ffb202b90f3bda5477d8feab12d8a3a8994ebc55fe6e74c"
                        "a8341520032eeea3fdef892f2882378f636212af4b2683ccf80bf025b7d9b457"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "abc"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        # MD6 over several levels of its tree (8192 bytes, i.e. 16 blocks, then 4, then 1)
        self.assertEqual(codecs.encode(bytes(i & 0xff for i in range(8192)), "md6"),
                         b"2a40338156df221b18b20e4003f51f61284cacd01935e9e87414e6ae40a6bd25")
        self.assertEqual(len(codecs.encode(STR, "md6-8")), 2)
        for e in ["keccak-128", "keccak_1024", "md6-0", "md6-12", "md6-520"]:
            self.assertRaises(LookupError, codecs.encode, STR, e)
        for e in ["sha0", "keccak", "md6"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # RIPEMD-160 and Whirlpool, with test vectors of the specifications, through hashlib when available, and in
        #  pure Python (forced by making hashlib fail as with OpenSSL 3 without its legacy provider)
        from contextlib import nullcontext
        from unittest.mock import patch
        from codext.hashing.ripemd import ripemd160
        from codext.hashing.whirlpool import whirlpool
        vectors = {
            'ripemd160|ripemd-160|rmd160': {
                '': "9c1185a5c5e9fc54612808977ee8f548b2258d31",
                'abc': "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc",
                'message digest': "5d0689ef49d2fae572b881b123a85ffa21595f36",
            },
            'whirlpool': {
                '': "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a7"
                    "3e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3",
                'abc': "4e2448a4c6f486bb16b6562c73b4020bf3043e3a731bce721ae1b303d97e6d4c"
                       "7181eebdb6c57e277d0e34957114cbd6c797fc9d95d8b582d225292076d4eef5",
                'The quick brown fox jumps over the lazy dog':
                    "b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8d88e75c4fa854df36725f"
                    "d2b52eb6544edcacd6f8beddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35",
            },
        }
        for unavailable in [False, True]:
            with patch("hashlib.new", side_effect=ValueError) if unavailable else nullcontext():
                for enc, v in vectors.items():
                    for e in enc.split("|"):
                        for s, r in v.items():
                            self.assertEqual(codecs.encode(s, e), r)
                            self.assertEqual(codecs.encode(b(s), e), b(r))
        # multi-block inputs, around the padding boundaries
        for n in [55, 56, 63, 64, 65, 1000]:
            self.assertEqual(ripemd160(b"a" * n), codecs.encode(b"a" * n, "ripemd160").decode())
        # reference value computed with OpenSSL (legacy provider)
        self.assertEqual(whirlpool(b"a" * 1000), "fe24b173807796fdac15ebcaf5769f661695601ffeb64490ec0eecd30bd5b2c3"
                                                 "773b36d4edaf3175378b8df114e9496c833ef13606e7ab3d455681e98ecc818f")
        for e in ["ripemd160", "whirlpool"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # MD4 (through hashlib when available, and in pure Python), the Windows LM and NT hashes (with a DES test vector
        #  of the pure Python implementation) and the MySQL password hashes
        from codext.hashing.md import md4
        from codext.hashing.windows import des_encrypt
        vectors = {
            'md4': {'': "31d6cfe0d16ae931b73c59d7e0c089c0", 'abc': "a448017aaf21d8525fc10ae87aa6729d",
                    'message digest': "d9130a8164549fe818874806e1c7014b"},
            'lm|lmhash|lm-hash': {'': "aad3b435b51404eeaad3b435b51404ee",
                                  'password': "e52cac67419a9a224a3b108f3fa6cb6d",
                                  'Password1234567890': "e52cac67419a9a22c41a0e2828864838"},
            'ntlm|nt|nthash|nt-hash': {'': "31d6cfe0d16ae931b73c59d7e0c089c0",
                                       'password': "8846f7eaee8fb117ad06bdd830b7586c"},
            'mysql323|mysql-3.23|mysql3': {'mypass': "6f8c114b58f2ce9e", 'pass word': "5d2e19393cc5ef67"},
            'mysql41|mysql-4.1|mysql4': {'password': "*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19"},
        }
        for unavailable in [False, True]:
            with patch("hashlib.new", side_effect=ValueError) if unavailable else nullcontext():
                for enc, v in vectors.items():
                    for e in enc.split("|"):
                        for s, r in v.items():
                            self.assertEqual(codecs.encode(s, e), r)
                            self.assertEqual(codecs.encode(b(s), e), b(r))
        for n in [55, 56, 63, 64, 65, 1000]:
            self.assertEqual(md4(b"a" * n), codecs.encode(b"a" * n, "md4").decode())
        self.assertEqual(des_encrypt(bytes.fromhex("133457799bbcdff1"), bytes.fromhex("0123456789abcdef")).hex(),
                         "85e813540f0ab405")
        for e in ["md4", "lm", "ntlm", "mysql323", "mysql41"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # bcrypt, with a test vector of OpenWall's crypt_blowfish (salt decoded from its base64 alphabet), through the
        #  bcrypt package when installed, and in pure Python (forced by making its import fail)
        import sys
        from codext.hashing.bcrypt import _b64, bcrypt, BCRYPT_B64
        salt = int("".join(f"{BCRYPT_B64.index(c):06b}" for c in "CCCCCCCCCCCCCCCCCCCCC."), 2) >> 4
        salt = salt.to_bytes(16, "big")
        self.assertEqual(_b64(salt), "CCCCCCCCCCCCCCCCCCCCC.")
        self.assertEqual(_b64(bcrypt("U*U", salt, 5)), "E5YPO9kmyuRGyh0XouQYb4YMJKvyOeW")
        for unavailable in [False, True]:
            with patch.dict(sys.modules, {'bcrypt': None}) if unavailable else nullcontext():
                for e, c in [("bcrypt-4", "04"), ("bcrypt_5", "05")]:
                    h = codecs.encode(STR.decode(), e)
                    self.assertRegex(h, rf"^\$2b\${c}\$[./A-Za-z0-9]{{53}}$")
                    self.assertNotEqual(h, codecs.encode(STR.decode(), e))
        for e in ["bcrypt-3", "bcrypt-32"]:
            self.assertRaises(LookupError, codecs.encode, STR, e)
        self.assertRaises(NotImplementedError, codecs.decode, STR, "bcrypt")
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
                self.assertIsNotNone(codecs.encode(STR, h := f"crypt-{m}"))
                self.assertRaises(NotImplementedError, codecs.decode, STR, h)
    
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
    
    def test_codec_tap(self):
        # with a non-strict errors handling, unsupported characters are replaced or ignored, and a word separator
        #  between the row and the column of a letter drops the letter
        self.assertEqual(codecs.encode("a!b", "tap", "replace"), ". .  ?  . ..")
        self.assertEqual(codecs.encode("a!b", "tap", "ignore"), ". .  . ..")
        self.assertEqual(codecs.decode(". / . ..", "tap", "ignore"), " b")
    
    def test_codec_unicode_tags(self):
        # decoding ignores the cover text, hence the hidden message can be inserted anywhere in it
        hidden = codecs.encode("ignore previous instructions", "unicode-tags")
        self.assertEqual(codecs.decode("Please summarize " + hidden + "this.", "unicode-tags"),
                         "ignore previous instructions")
        # the replacement character is hidden too, so that it survives decoding
        replaced = codecs.encode("Caf\u00e9!", "unicode-tags", "replace")
        self.assertEqual(codecs.decode(replaced, "unicode-tags"), "Caf?!")
        # the BEGIN and CANCEL tags are only stripped by the wrapped variant
        wrapped = codecs.encode("Hi", "unicode-tags-wrapped")
        self.assertEqual(codecs.decode(wrapped, "unicode-tags"), "\x01Hi\x7f")
        self.assertEqual(codecs.decode(wrapped, "unicode-tags-wrapped"), "Hi")

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
        # characters that no number of spaces can shift to a printable one (this used to loop forever)
        for c in ["\xff", chr(0x141)]:
            self.assertEqual(codecs.decode(codecs.encode("A" + c + "B", "whitespace+after-before", "ignore"),
                                           "whitespace+after-before"), "AB")
        self.assertRaises(ValueError, codecs.encode, "A\xff", "whitespace-2*after+3*before")
        # a division gives non-integer shifts (or divides by zero spaces), hence nothing can be encoded
        self.assertRaises(ValueError, codecs.encode, "A", "whitespace+2/after-before")
        # a line holding more than one character is not decoded at all
        self.assertEqual(codecs.decode(" A \nBC\n D", "whitespace+after-before", "ignore"),
                         codecs.decode(" A \n D", "whitespace+after-before"))

    def test_codec_zero_width(self):
        self.assertRaises(LookupError, codecs.encode, "test", "zero-width-4")
        # decoding ignores the cover text, hence the hidden message can be inserted anywhere in it
        hidden = codecs.encode("secret", "zero-width")
        self.assertEqual(codecs.decode("Nothing " + hidden + "to see here.", "zero-width"), "secret")
        # an invalid UTF-8 byte (0xff) followed by a valid message
        bad = chr(0x200c) * 8 + codecs.encode("ok", "zero-width")
        self.assertEqual(codecs.decode(bad, "zero-width", "replace"), "?ok")
        self.assertEqual(codecs.decode(bad, "zero-width", "ignore"), "ok")
        # code points above 5**7 cannot be encoded with the quinary variant
        STR = "A" + chr(0x1f600) + "B"
        self.assertEqual(codecs.encode(STR, "zero-width-full", "ignore"), codecs.encode("AB", "zero-width-full"))
        self.assertIn(chr(0x1f600), codecs.encode(STR, "zero-width-full", "leave"))
    
    def test_codec_xxencode(self):
        # a bad length character is reported, the number of bytes then being guessed from the length of the line
        self.assertEqual(codecs.decode("!Eq3o", "xx", "ignore"), "Cat")
        # an invalid group of 4 characters is handled as a whole (length "4" means 6 bytes)
        self.assertEqual(codecs.decode("4Eq!oEq3o", "xx", "replace"), "?Cat")
        self.assertEqual(codecs.decode("4Eq!oEq3o", "xx", "ignore"), "Cat")
