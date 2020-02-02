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
        return codecs.CodecInfo(
            name="dummy3",
            encode=dummy_encode,
            decode=dummy_decode,
        )


class TestCommon(TestCase):
    def test_add_codec(self):
        self.assertRaises(ValueError, codext.add, "test")
        self.assertRaises(ValueError, codext.add, "test", "BAD")
        self.assertRaises(ValueError, codext.add, "test", lambda: None, "BAD")
        self.assertIsNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
    
    def test_remove_codec(self):
        self.assertIsNone(codext.add("dummy", dummy_encode, dummy_decode))
        self.assertEqual(codext.encode("test", "dummy"), "test")
        self.assertIsNone(codext.remove("dummy"))
        self.assertRaises(LookupError, codext.encode, "test", "dummy")
        # special case, when adding a new codec also to the native codecs
        #  registry, then it won't be possible to remove it further
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
