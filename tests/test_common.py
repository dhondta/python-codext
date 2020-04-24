#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Codecs added assets' tests.

"""
from unittest import TestCase

import codext
from codext.__common__ import *


def dummy_encode(input, errors="strict"):
    return input, len(input)


def dummy_decode(input, errors="strict"):
    return input, len(input)


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
    
    def test_remove_codec(self):
        self.assertIsNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        self.assertIsNone(codext.remove("dummy"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy")
        # special case, when adding a new codec also to the native codecs registry, then it won't be possible to remove
        #  it further
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
