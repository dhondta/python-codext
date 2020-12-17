#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Codecs added assets' tests.

"""
import codecs
import codext
import random
import sys
from six import b, binary_type, text_type
from unittest import TestCase


PY3 = sys.version[0] == "3"


def dummy_encode(input, errors="strict"):
    return input, len(input)


def dummy_decode(input, errors="strict"):
    return input, len(input)


def dummy_errored_decode(useless):
    raise AttributeError
    def decode(input, errors="strict"):
        return input, len(input)
    return decode


def ensure_str(s, encoding='utf-8', errors='strict'):
    """ Similar to six.ensure_str. Adapted here to avoid messing up with six version errors. """
    if not PY3 and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif PY3 and isinstance(s, binary_type):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    return s


def getregentry(encoding):
    if encoding == "dummy3":
        return codecs.CodecInfo(name="dummy3", encode=dummy_encode, decode=dummy_decode)


class TestCommon(TestCase):
    def test_add_codec(self):
        self.assertRaises(ValueError, codext.add, "test")
        self.assertRaises(ValueError, codext.add, "test", "BAD")
        self.assertRaises(ValueError, codext.add, "test", lambda: None, "BAD")
        self.assertIsNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        ci = codext.lookup("dummy")
        for k in ["add_to_codecs", "category", "examples", "name", "pattern", "text"]:
            self.assertIn(k, ci.parameters.keys())
        self.assertIsNone(codext.add("dummy_errored", None, dummy_errored_decode, r"dummy_errored(\d+)$"))
        self.assertRaises(AttributeError, codext.lookup, "dummy_errored1")

    def test_add_map_codec(self):
        ENCMAP = [{'a': "A", 'b': "B", 'c': "C"}, {'d': "D", 'e': "E", 'f': "F"}, {'g': "G", 'h': "H", 'i': "I"}]
        self.assertIsNone(codext.add_map("dummy2", ENCMAP, pattern=r"^dummy2(?:[-_]?(\d))?$"))
        self.assertRaises(ValueError, codext.add_map, "dummy2", "BAD_ENCMAP")
        self.assertEqual(codext.encode("abc", "dummy2"), "ABC")
        self.assertEqual(codext.encode("abc", "dummy2-1"), "ABC")
        self.assertEqual(codext.encode("def", "dummy2-2"), "DEF")
        self.assertEqual(codext.encode("ghi", "dummy2-3"), "GHI")
        self.assertRaises(LookupError, codext.encode, "test", "dummy2-4")
        ENCMAP = {'': {'a': "A", 'b': "B"}, r'bad': {'a': "B", 'b': "A"}}
        self.assertIsNone(codext.add_map("dummy3", ENCMAP, pattern=r"^dummy3([-_]inverted)?$"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy3_inverted")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, ignore_case="BAD")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, intype="BAD")
        self.assertRaises(ValueError, codext.add_map, "dummy2", ENCMAP, outype="BAD")
        ci = codext.lookup("dummy2")
        for k in ["category", "encmap", "ignore_case", "intype", "no_error", "outype", "repl_char", "sep", "text"]:
            self.assertIn(k, ci.parameters.keys())
    
    def test_list_codecs(self):
        codext.reset()
        self.assertTrue(len(codext.list()) > 0)
        self.assertTrue(len(codext.list("other")) > 0)
        self.assertTrue(len(codext.list("native")) > 0)
        self.assertTrue(len(codext.list("non-native")) > 0)
        self.assertTrue(len(codext.list("native", "non-native", "crypto", "base")) > 0)
        self.assertTrue(len(codext.list("native", "language", "crypto")) > 0)
        self.assertEqual(set(codext.list()), set(codext.list("native") + codext.list("non-native")))
        self.assertRaises(ValueError, codext.list, "BAD_CATEGORY")
    
    def test_remove_codec(self):
        self.assertIsNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        self.assertIsNone(codext.remove("dummy"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy")
        # special case, when adding a new codec also to the native codecs registry, then it won't be possible to remove
        #  it afterwards
        self.assertIsNone(codecs.add("dummy2", dummy_encode, dummy_decode))
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
    
    def test_guess_decode(self):
        codext.reset()
        STR = "This is a test"
        self.assertEqual(STR, codext.guess("VGhpcyBpcyBhIHRlc3Q=", "a test", 1)[0])
        self.assertEqual(STR, codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "a test", found=["base62"])[0])
        self.assertEqual(STR, codext.guess("VGhpcyBpcyBhIHRlc3Q=", "a test", 1, "base")[0])
        self.assertIsNone(codext.guess("NOT THE ENCODED TEST STRING", "a test", 1)[0])
        self.assertRaises(ValueError, codext.guess, STR, max_depth=0)
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
                    found_dec, found_encodings = codext.guess(enc, "a test", 1, [c])
                    print(encoding, found_encodings)
                    self.assertEqual(ensure_str(STR).lower(), ensure_str(found_dec).lower())
                    if c != "base":
                        # do not check for base as the guessed encoding name can be different, e.g.:
                        #  actual:  base2
                        #  guessed: base2-generic
                        if "-icase" in encoding:
                            self.assertEqual(encoding.lower(), found_encodings[0].lower())
                        else:
                            self.assertEqual(encoding, found_encodings[0])

