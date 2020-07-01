#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""HTML entities codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCodecHtmlEntities(TestCase):
    def test_codec_html_entities(self):
        STR = "<This\tis\na test>"
        ENC = "&lt;This&Tab;is&NewLine;a test&gt;"
        self.assertEqual(codecs.encode(STR, "html_entities"), ENC)
        self.assertEqual(codecs.encode(b(STR), "html"), b(ENC))
        self.assertEqual(codecs.encode(" ", "html-entity"), " ")
        self.assertEqual(codecs.decode("&nbsp;", "html-entity"), " ")
        self.assertRaises(ValueError, codecs.decode, "&DoesNotExist;", "html")
        self.assertEqual(codecs.decode("&DoesNotExist;test", "html", "replace"), "?test")
        if PY3:
            self.assertEqual(codecs.encode("\u1234", "html_entity"), "&1234;")
            self.assertEqual(codecs.decode("&1234;", "html_entity"), "\u1234")

