#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Markdown codec tests.

"""
import os
from six import binary_type, string_types
from unittest import TestCase

from codext.__common__ import *


class TestCodecMarkdown(TestCase):
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
