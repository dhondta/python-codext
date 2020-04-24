#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""URL codec tests.

"""
from unittest import TestCase

from codext.__common__ import *


if PY3:
    class TestCodecUrl(TestCase):
        def test_codec_urlencode(self):
            STR = "?=this/is-a_test/../"
            URL = "%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F"
            self.assertEqual(codecs.encode(STR, "url"), URL)
            self.assertEqual(codecs.encode(b(STR), "urlencode"), b(URL))
            self.assertEqual(codecs.decode(URL, "urlencode"), STR)
            self.assertEqual(codecs.decode(b(URL), "url"), b(STR))
