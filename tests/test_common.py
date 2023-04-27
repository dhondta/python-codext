#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Codecs added assets' tests.

"""
import codext
import json
import random
import sys
from codext.__common__ import *
from codext.__common__ import CODECS_OVERWRITTEN, PERS_MACROS, PERS_MACROS_FILE
from unittest import TestCase


def dummy_encode(input, errors="strict"):
    return input, len(input)


def dummy_decode(input, errors="strict"):
    return input, len(input)


def dummy_errored_decode(useless):
    raise AttributeError
    def decode(input, errors="strict"):
        return input, len(input)
    return decode


def getregentry(encoding):
    if encoding == "dummy3":
        return codecs.CodecInfo(name="dummy3", encode=dummy_encode, decode=dummy_decode)


class TestCommon(TestCase):
    def setUp(self):
        codext.reset()
    
    def test_add_codec(self):
        self.assertRaises(ValueError, codext.add, "test")
        self.assertRaises(ValueError, codext.add, "test", "BAD")
        self.assertRaises(ValueError, codext.add, "test", lambda: None, "BAD")
        self.assertIsNotNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        ci = codext.lookup("dummy")
        for k in ["add_to_codecs", "category", "examples", "name", "pattern", "text"]:
            self.assertIn(k, ci.parameters.keys())
        self.assertIsNotNone(codext.add("dummy_errored", None, dummy_errored_decode, r"dummy_errored(\d+)$"))
        self.assertRaises(AttributeError, codext.lookup, "dummy_errored1")

    def test_add_map_codec(self):
        ENCMAP = [{'a': "A", 'b': "B", 'c': "C"}, {'d': "D", 'e': "E", 'f': "F"}, {'g': "G", 'h': "H", 'i': "I"}]
        self.assertIsNotNone(codext.add_map("dummy2", ENCMAP, pattern=r"^dummy2(?:[-_]?(\d))?$"))
        self.assertRaises(ValueError, codext.add_map, "dummy2", "BAD_ENCMAP")
        self.assertEqual(codext.encode("abc", "dummy2"), "ABC")
        self.assertEqual(codext.encode("abc", "dummy2-1"), "ABC")
        self.assertEqual(codext.encode("def", "dummy2-2"), "DEF")
        self.assertEqual(codext.encode("ghi", "dummy2-3"), "GHI")
        self.assertRaises(LookupError, codext.encode, "test", "dummy2-4")
        ENCMAP = {'': {'a': "A", 'b': "B"}, r'bad': {'a': "B", 'b': "A"}}
        self.assertIsNotNone(codext.add_map("dummy3", ENCMAP, pattern=r"^dummy3([-_]inverted)?$"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy3_inverted")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, ignore_case="BAD")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, intype="BAD")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, outype="BAD")
        ci = codext.lookup("dummy2")
        for k in ["category", "encmap", "ignore_case", "intype", "no_error", "outype", "repl_char", "sep", "text"]:
            self.assertIn(k, ci.parameters.keys())
    
    def test_list_codecs(self):
        self.assertTrue(len(codext.list()) > 0)
        self.assertTrue(len(codext.list("other")) > 0)
        self.assertTrue(len(codext.list("native")) > 0)
        self.assertTrue(len(codext.list("non-native")) > 0)
        self.assertTrue(len(codext.list("native", "non-native", "crypto", "base")) > 0)
        self.assertTrue(len(codext.list("native", "language", "crypto")) > 0)
        self.assertTrue(len(codext.list("~crypto")) > 0)
        self.assertEqual(set(codext.list("~native")), set(codext.list("non-native")))
        self.assertEqual(set(codext.list()), set(codext.list("native") + codext.list("non-native")))
        self.assertRaises(ValueError, codext.list, "BAD_CATEGORY")
        self.assertTrue(codext.is_native("base64_codec"))
        self.assertFalse(codext.is_native("base64"))
    
    def test_remove_codec(self):
        self.assertIsNotNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        self.assertIsNone(codext.remove("dummy"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy")
        # special case, when adding a new codec also to the native codecs registry, then it won't be possible to remove
        #  it afterwards
        self.assertIsNotNone(codecs.add("dummy2", dummy_encode, dummy_decode))
        self.assertEqual(codecs.encode("test", "dummy2"), "test")
        self.assertIsNone(codecs.remove("dummy2"))
        self.assertEqual(codecs.encode("test", "dummy2"), "test")
        self.assertIsNone(codecs.register(getregentry))
        self.assertEqual(codecs.encode("test", "dummy3"), "test")
        self.assertIsNone(codecs.remove("dummy3"))
        self.assertEqual(codecs.encode("test", "dummy3"), "test")
    
    def test_clear_codecs(self):
        self.assertIsNotNone(codecs.encode("test", "morse"))
        self.assertIsNone(codecs.clear())
        self.assertRaises(LookupError, codecs.encode, "test", "morse")
    
    def test_reset_codecs(self):
        self.assertIsNone(codext.reset())
        self.assertIsNotNone(codext.encode("test", "morse"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy")
        self.assertTrue(len(CODECS_OVERWRITTEN) > 0)
        self.assertIsNotNone(str(CODECS_OVERWRITTEN[0]))
    
    def test_search_codecs(self):
        self.assertIsNotNone(codext.search("morse"))
        self.assertIsNotNone(codext.search("geohash"))
        self.assertIsNotNone(codext.examples("morse"))
        self.assertIsNotNone(codext.examples("cp"))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"[ab]{1,3}")))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"(?<=ab)cd")))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"(?<=-)\w+")))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"([^\s])\1")))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"[^\\]")))
        self.assertIsNotNone(list(codext.generate_strings_from_regex(r"[^a]")))
    
    def test_encode_multiple_rounds(self):
        s = "test"
        for i in range(3):
            s = codext.encode(s, "morse")
        self.assertEqual(s, codext.encode("test", "morse[3]"))
        self.assertIsNotNone(codext.encode("test", "base64[10]"))
    
    def test_guess_decode(self):
        self.assertIsNone(codext.stopfunc._reload_lang())
        self.assertIsNotNone(codext.stopfunc._validate("flag"))
        _l = lambda d: list(d.items())[0][1] if len(d) > 0 else None
        codext.add("test_codec", lambda x, e="strict": (x + "=", len(x)), lambda x, e="strict": (x[:-1], len(x)-1),
                   "^test(?:_codec)?$", padding_char="=", no_error=True, bonus_func=lambda *a: True, penalty=-.5)
        self.assertIn("test-codec", codext.list_encodings("test"))
        self.assertEqual(codext.decode("TEST=", "test"), "TEST")
        self.assertEqual(list(codext.guess("TEST=", codext.stopfunc.text, include="test", max_depth=2,
                                           scoring_heuristic=False).items())[0][1], "TEST")
        self.assertEqual(list(codext.guess("TEST=", codext.stopfunc.text, include=["test", "base"],
                                           max_depth=2).items())[0][1], "TEST")
        STR = "This is a test"
        self.assertEqual(STR, _l(codext.guess("VGhpcyBpcyBhIHRlc3Q=", "a test", max_depth=1)))
        self.assertEqual(STR, _l(codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "a test", found=["base62"])))
        self.assertEqual(STR, _l(codext.guess("VGhpcyBpcyBhIHRlc3Q=", "a test", 0, 1, "base", scoring_heuristic=True,
                                              exclude=["base100"])))
        self.assertEqual(STR, _l(codext.guess("VGhpcyBpcyBhIHRlc3Q=", "a test", 0, 1, ["base", "crypto"])))
        self.assertEqual(len(codext.guess("NOT THE ENCODED TEST STRING", "a test", max_depth=1, exclude=None)), 0)
        self.assertIn("F1@9", _l(codext.guess("VGVzdCBGMUA5ICE=", codext.stopfunc.flag, max_depth=1, stop=False,
                                              show=True)))
        self.assertEqual(len(codext.guess("VGhpcyBpcyBhIHRlc3Q=", " a test", max_depth=1, include="base",
                                          exclude=("base64", "base64-url"))), 0)
        self.assertEqual(len(codext.guess("VGhpcyBpcyBhIHRlc3Q=", " a test", max_depth=1, include="base",
                                          scoring_heuristic=True, exclude=("base64", "base64-url", "atbash"))), 0)
        self.assertRaises(ValueError, codext.guess, STR, max_depth=0)
        self.assertRaises(ValueError, codext.guess, STR, exclude=42)
        for c in ["base", "language", "native", "stegano"]:
            e = codext.list(c)
            random.shuffle(e)
            for ename in e[:10]:
                for encoding in codext.lookup(ename).parameters.get('guess', [ename])[:10]:
                    try:
                        enc = codext.encode(STR, encoding)
                    except (NotImplementedError, ValueError):
                        continue
                    except TypeError:
                        enc = codext.encode(b(STR), encoding)
                    if codext.decode(enc, encoding) == STR:
                        continue
                    for found_encodings, found_dec in codext.guess(enc, "a test", 0, 1, [c],
                                                                   scoring_heuristic=True, debug=True).items():
                        self.assertEqual(ensure_str(STR).lower(), ensure_str(found_dec).lower())
                        if c != "base":
                            # do not check for base as the guessed encoding name can be different, e.g.:
                            #  actual:  base2
                            #  guessed: base2-generic
                            if "-icase" in encoding:
                                self.assertEqual(encoding.lower(), found_encodings[0].lower())
                            else:
                                self.assertEqual(encoding, found_encodings[0])
        txt = "".join(chr(i) for i in range(256))
        b64 = codext.encode(txt, "base64")
        self.assertEqual(txt, _l(codext.guess(b64, "0123456789", max_depth=1, scoring_heuristic=True, include="base")))
        self.assertRaises(ValueError, codext.stopfunc._reload_lang, "DOES_NOT_EXIST")
    
    def test_rank_input(self):
        codext.remove("test_codec")
        self.assertRaises(LookupError, codext.encode, "TEST", "test")
        codext.add("test_codec", lambda x, e="strict": (x + "=", len(x)), lambda x, e="strict": (x[:-1], len(x)-1),
                   "^test(?:_codec)?$", padding_char="=", no_error=True, penalty=1.)
        STR = "This is a test string !"
        ENC = codext.encode(STR, "base64")
        self.assertTrue(len(codext.rank(ENC)) > 20)
        self.assertEqual(len(codext.rank(ENC, limit=20)), 20)
        self.assertIn(codext.rank(ENC, exclude=["rot"])[0][1], ["base64", "base64-url", "base64-inv"])
        self.assertEqual(codext.rank(ENC, include="base")[0][0][1], STR)
        self.assertEqual(codext.rank(ENC, include=["base"])[0][0][1], STR)
        self.assertIsNotNone(codext.rank(ENC, include=["base"], exclude=["does_not_exist"])[0][0][1], STR)
        self.assertIsNotNone(codext.rank("TEST=", include=["test", "base"])[0][0][1], "TEST")
    
    def test_handle_macros(self):
        MACRO = "test-macro-f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2"
        STR = "this is a test"
        ENC = "H4sIAMrbkmEC/0txzyhIrnQC4QxPj6CcZONAWwAMIDOIFAAAAA=="
        codext.remove(MACRO)
        l = codext.list_macros()
        self.assertTrue(len(l) > 0)
        cm = codext.lookup("example-macro")
        self.assertIsNotNone(cm)
        self.assertRaises(LookupError, codext.lookup, "example-macro", False)
        self.assertRaises(ValueError, codext.add_macro, "example-macro", "base64")
        self.assertRaises(ValueError, codext.add_macro, "base64", "base91")
        self.assertIsNotNone(repr(cm))
        self.assertTrue(hasattr(cm, "parameters"))
        self.assertRaises(LookupError, codext.lookup, MACRO)
        self.assertIsNone(codext.add_macro(MACRO, "base64", "gzip", "base64"))
        self.assertIn(MACRO, codext.list_macros())
        self.assertIsNotNone(codext.encode(STR, MACRO))
        self.assertEqual(codext.decode(ENC, MACRO), STR)
        # insert a bad entry for the list of encodings in the JSON file
        PERS_MACROS[MACRO] = "not a list or tuple..."
        with open(PERS_MACROS_FILE, 'w') as f:
            json.dump(PERS_MACROS, f)
        codext.reset()
        self.assertRaises(ValueError, codext.lookup, MACRO)
        self.assertIsNone(codext.remove(MACRO))
        self.assertRaises(LookupError, codext.lookup, MACRO)
        self.assertNotIn(MACRO, codext.list_macros())
        self.assertIsNone(codext.remove("THIS-MACRO-DOES-NOT-EXIST"))
        self.assertIsNone(codext.remove("VALID-MACRO"))
        self.assertIsNone(codext.add_macro("VALID-MACRO", "gzip", "base64"))
        self.assertIsNone(codext.remove("VALID-MACRO"))
        self.assertIsNone(codext.add_macro("VALID-MACRO", "lzma", "base64"))
        self.assertIsNone(codext.remove("VALID-MACRO"))
        self.assertRaises(ValueError, codext.add_macro, "SHALL-FAIL", "base26", "sms", "letter-indices")

