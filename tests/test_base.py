#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Base codecs tests.

"""
import sys
from unittest import TestCase

from codext.__common__ import *
from codext.base._base import _generate_charset
from codext.base.baseN import base, main2, main32, main64url


class TestCodecsBase(TestCase):
    def setUp(self):
        global STR
        STR = "this is a test"
    
    def test_new_base_codec(self):
        for i in [0, 1, 256]:
            self.assertRaises(ValueError, _generate_charset, i)
        b10 = lambda *a: "0123456789"
        base(b10, "base10")
        B10 = "2361031878030638688519054699098996"
        self.assertEqual(codecs.encode(STR, "base10"), B10)
        self.assertEqual(codecs.encode(b(STR), "base10"), b(B10))
        self.assertEqual(codecs.decode(B10, "base10"), STR)
        self.assertEqual(codecs.decode(b(B10), "base10"), b(STR))
        self.assertRaises(ValueError, base, 1, "test")
        b11 = "0123456789a"
        base(b11, "base11")
        B11 = "113342054335735319526632a26972419"
        self.assertEqual(codecs.encode(STR, "base11"), B11)
        self.assertEqual(codecs.decode(B11, "base11"), STR)
        self.assertRaises(ValueError, base, object(), "test")
        self.assertIsNone(base({'': "01234"}, r"^base5(test)?$"))
        self.assertIsNotNone(codecs.encode(STR, "base5test"))
        self.assertRaises(ValueError, base, {'': "01234"}, "base5-test", pow2=True)
        self.assertEqual("", codecs.decode("", "base5test"))
    
    def test_codec_base1(self):
        C = "A"
        for i in range(3):
            self.assertIsNotNone(codecs.encode(i * C, "base1"))
        self.assertRaises(ValueError, codecs.encode, 4 * C, "unary")
        self.assertEqual(codecs.decode("AAAAA", "base1"), "\x05")
    
    def test_codec_base2(self):
        STR = "test"
        B2 = "01110100011001010111001101110100"
        self.assertEqual(codecs.encode(STR, "base2"), B2)
        self.assertEqual(codecs.encode(b(STR), "base2"), b(B2))
        self.assertEqual(codecs.decode(B2, "base2"), STR)
        self.assertEqual(codecs.decode(b(B2), "base2"), b(STR))
        B2 = "10001011100110101000110010001011"
        self.assertEqual(codecs.encode(STR, "base2-inv"), B2)
        self.assertEqual(codecs.decode(B2, "base2-inv"), STR)
        B2 = "abbbabaaabbaabababbbaabbabbbabaa"
        self.assertEqual(codecs.encode(STR, "base2-ab"), B2)
        self.assertEqual(codecs.decode(B2, "base2-ab"), STR)
        B2 = "CDDDCDCCCDDCCDCDCDDDCCDDCDDDCDCC"
        self.assertEqual(codecs.encode(STR, "base2-CD"), B2)
        self.assertEqual(codecs.decode(B2, "base2-CD"), STR)
        B2 = "34443433344334343444334434443433"
        self.assertEqual(codecs.encode(STR, "base2-34"), B2)
        self.assertEqual(codecs.decode(B2, "base2-34"), STR)
    
    def test_codec_base3(self):
        STR = "test"
        B3 = "23112113223321323322"
        self.assertEqual(codecs.encode(STR, "base3"), B3)
        self.assertEqual(codecs.encode(b(STR), "base3"), b(B3))
        self.assertEqual(codecs.decode(B3, "base3"), STR)
        self.assertEqual(codecs.decode(b(B3), "base3"), b(STR))
        B3 = "21332331221123121122"
        self.assertEqual(codecs.encode(STR, "base3-inv"), B3)
        self.assertEqual(codecs.decode(B3, "base3-inv"), STR)
        B3 = "bcaabaacbbccbacbccbb"
        self.assertEqual(codecs.encode(STR, "base3-abc"), B3)
        self.assertEqual(codecs.decode(B3, "base3-abc"), STR)
        self.assertRaises(LookupError, codecs.encode, "test", "base3-ab")
        self.assertRaises(LookupError, codecs.encode, "test", "base3-abcd")
    
    def test_codec_base4(self):
        STR = "test"
        B4 = "2421232224142421"
        self.assertEqual(codecs.encode(STR, "base4"), B4)
        self.assertEqual(codecs.encode(b(STR), "base4"), b(B4))
        self.assertEqual(codecs.decode(B4, "base4"), STR)
        self.assertEqual(codecs.decode(b(B4), "base4"), b(STR))
        B4 = "3134323331413134"
        self.assertEqual(codecs.encode(STR, "base4-inv"), B4)
        self.assertEqual(codecs.decode(B4, "base4-inv"), STR)
        B4 = "bdbabcbbbdadbdba"
        self.assertEqual(codecs.encode(STR, "base4-abcd"), B4)
        self.assertEqual(codecs.decode(B4, "base4-abcd"), STR)
        self.assertRaises(LookupError, codecs.encode, "test", "base4-abc")
        self.assertRaises(LookupError, codecs.encode, "test", "base4-abcde")
    
    def test_codec_base8(self):
        STR = "test"
        B8 = "dfagcfgddfa====="
        self.assertEqual(codecs.encode(STR, "base8"), B8)
        self.assertEqual(codecs.encode(b(STR), "base8"), b(B8))
        self.assertEqual(codecs.decode(B8, "base8"), STR)
        self.assertEqual(codecs.decode(b(B8), "base8"), b(STR))
        B8 = "echbfcbeech====="
        self.assertEqual(codecs.encode(STR, "base8-inv"), B8)
        self.assertEqual(codecs.decode(B8, "base8-inv"), STR)
        B8 = "35062563350====="
        self.assertEqual(codecs.encode(STR, "base8-01234567"), B8)
        self.assertEqual(codecs.decode(B8, "base8-01234567"), STR)
        self.assertRaises(LookupError, codecs.encode, "test", "base8-0123456")
        self.assertRaises(LookupError, codecs.encode, "test", "base8-012345678")
    
    def test_codec_base16(self):
        B16 = "7468697320697320612074657374"
        self.assertEqual(codecs.encode(STR, "base16"), B16)
        self.assertEqual(codecs.encode(b(STR), "base16"), b(B16))
        self.assertEqual(codecs.decode(B16, "base16"), STR)
        self.assertEqual(codecs.decode(b(B16), "base16"), b(STR))
        B16 += "?"
        self.assertRaises(ValueError, codecs.decode, B16, "base16")
        self.assertEqual(codecs.decode(B16, "base16", "ignore"), STR)
        self.assertEqual(codecs.decode(B16, "base16", "replace"), STR + "\x00")
        self.assertRaises(ValueError, codecs.decode, B16, "base16", "BAD")
        STR2 = "=:;"
        B16_1 = "3d3a3b"
        B16_2 = "3D3A3B"
        B16_3 = "3D3a3B"  # mixed case: should fail
        self.assertEqual(codecs.encode(STR2, "hex"), B16_2)
        self.assertEqual(codecs.decode(B16_1, "hex"), STR2)
        self.assertEqual(codecs.decode(B16_2, "hex"), STR2)
        self.assertRaises(ValueError, codecs.decode, B16_3, "hex")
    
    def test_codec_base32(self):
        for b32, enc in zip(["ORUGS4ZANFZSAYJAORSXG5A=", "qtwg1h3ypf31yajyqt1zg7y=", "EHK6ISP0D5PI0O90EHIN6T0=",
                             "fjn6kwt0e5tk0s90fjkr6x0=", "EHM6JWS0D5SJ0R90EHJQ6X0="],
                            ["base32", "zbase32", "base32-hex", "geohash", "crockford"]):
            self.assertEqual(codecs.encode(STR, enc), b32)
            self.assertEqual(codecs.encode(b(STR), enc), b(b32))
            self.assertEqual(codecs.decode(b32, enc), STR)
            self.assertEqual(codecs.decode(b(b32), enc), b(STR))
            self.assertRaises(ValueError, codecs.decode, b32.rstrip("="), enc)
            self.assertRaises(ValueError, codecs.decode, b32.rstrip("="), enc, "BAD")
    
    def test_codec_base36(self):
        B36 = "4WMHTK6UZL044O91NKCEB8"
        self.assertEqual(codecs.encode(STR, "base36"), B36)
        self.assertEqual(codecs.encode(b(STR), "base36"), b(B36))
        self.assertEqual(codecs.decode(B36, "base36"), STR)
        self.assertEqual(codecs.decode(b(B36), "base36"), b(STR))
        B36 = "E6WR3UG49VAEEYJBXUMOLI"
        self.assertEqual(codecs.encode(STR, "base36-inv"), B36)
        self.assertEqual(codecs.decode(B36, "base36-inv"), STR)
        self.assertRaises(ValueError, codecs.decode, B36 + "?", "base36-inv")
        self.assertRaises(ValueError, codecs.decode, B36 + "?", "base36", "BAD")
        self.assertEqual(codecs.decode(B36 + "?", "base36-inv", "ignore"), STR)
    
    def test_codec_base58(self):
        B58 = "jo91waLQA1NNeBmZKUF"
        self.assertEqual(codecs.encode(STR, "base58"), B58)
        self.assertEqual(codecs.encode(b(STR), "base58"), b(B58))
        self.assertEqual(codecs.decode(B58, "base58"), STR)
        self.assertEqual(codecs.decode(b(B58), "base58"), b(STR))
        B58 = "jo9rA2LQwr44eBmZK7E"
        self.assertEqual(codecs.encode(STR, "base58-ripple"), B58)
        self.assertEqual(codecs.decode(B58, "base58-rp"), STR)
        B58 = "JN91Wzkpa1nnDbLyjtf"
        self.assertEqual(codecs.encode(STR, "base58-flickr"), B58)
        self.assertEqual(codecs.encode(STR, "base58-shorturl"), B58)
        self.assertEqual(codecs.decode(B58, "base58-fl"), STR)
        self.assertEqual(codecs.encode(STR, "base58-short-url"), B58)
        self.assertEqual(codecs.encode(STR, "base58-url"), B58)
    
    def test_codec_base62(self):
        for b62, enc in zip(["CsoB4HQ5gmgMyCenF7E", "M2yLERaFqwqW8MoxPHO"], ["base62", "base62-inv"]):
            self.assertEqual(codecs.encode(STR, enc), b62)
            self.assertEqual(codecs.encode(b(STR), enc), b(b62))
            self.assertEqual(codecs.decode(b62, enc), STR)
            self.assertEqual(codecs.decode(b(b62), enc), b(STR))
    
    def test_codec_base64(self):
        for b64, enc in zip(["dGhpcyBpcyBhIHRlc3Q=", "T6XfSo1fSo1X87HbStG="], ["base64", "base64-inv"]):
            self.assertEqual(codecs.encode(STR, enc), b64)
            self.assertEqual(codecs.encode(b(STR), enc), b(b64))
            self.assertEqual(codecs.decode(b64, enc), STR)
            self.assertEqual(codecs.decode(b(b64), enc), b(STR))
    
    def test_codec_base91(self):
        for b91, enc in zip([",X,<:WRT%yxth90oZB", ",N,<:MHJ%onjXzqeP1", "Jx&[jv4S3Wg>,71@Jk", "yJy^\\IDFsdc?Tof:L#"],
                            ["base91", "base91-inv", "base91-alt", "base91-alt-inv"]):
            self.assertEqual(codecs.encode(STR, enc), b91)
            self.assertEqual(codecs.encode(b(STR), enc), b(b91))
            self.assertEqual(codecs.decode(b91, enc), STR)
            self.assertEqual(codecs.decode(b(b91), enc), b(STR))
        self.assertIsNotNone(codecs.encode("\x00\x00", "base91"))
        self.assertIsNotNone(codecs.decode("abc", "base91"))
        self.assertIsNotNone(codecs.decode("AD", "base91"))
        self.assertRaises(ValueError, codecs.decode, "\xff", "base91")
        self.assertRaises(ValueError, codecs.decode, "a\xff", "base91")
        self.assertIsNotNone(codecs.encode("\x00\x00", "base91-alt"))
    
    def test_codec_base100(self):
        B100 = "\U0001f46b\U0001f45f\U0001f460\U0001f46a\U0001f417\U0001f460\U0001f46a\U0001f417\U0001f458\U0001f417" \
               "\U0001f46b\U0001f45c\U0001f46a\U0001f46b"
        self.assertEqual(codecs.encode(STR, "base100"), B100)
        self.assertEqual(codecs.encode(b(STR), "base100"), b(B100))
        self.assertEqual(codecs.decode(B100, "base100"), STR)
        self.assertEqual(codecs.decode(b(B100), "base100"), b(STR))
        self.assertRaises(ValueError, codecs.decode, b(B100)[1:], "base100")
        self.assertIsNotNone(codecs.decode(b(B100) + b"\n", "base100", "ignore"))
    
    def test_codec_base_generic(self):
        for n in range(2, 255):
            bn = "base{}_generic".format(n)
            self.assertEqual(codecs.decode(codecs.encode(STR, bn), bn), STR)
        self.assertRaises(LookupError, codecs.decode, "test", "base0-generic")
        self.assertRaises(LookupError, codecs.decode, "test", "base1-generic")
        self.assertRaises(LookupError, codecs.decode, "test", "base256-generic")
    
    def test_base_main(self):
        tmp = sys.argv[:]
        tfile = "test-base-main.txt"
        with open(tfile, 'w') as f:
            f.write("This is a long test string for the sake of causing line wrapping based on default parameters.")
        for swap_arg in [[], ["-s"]]:
            sys.argv = [tmp[0], tfile] + swap_arg
            for m in main32, main64url:
                self.assertEqual(m(), 0)
            sys.argv = [tmp[0], tfile, "-d"] + swap_arg
            self.assertEqual(main2(), 1)
        os.remove(tfile)
        sys.argv[:] = tmp

