#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Codecs added assets' tests.

"""
from unittest import TestCase

from codext.__common__ import *


class TestCommon(TestCase):
    def test_add_codec(self):
        f = lambda: None
        self.assertRaises(ValueError, codecs.add, "test")
        self.assertRaises(ValueError, codecs.add, "test", "BAD")
        self.assertRaises(ValueError, codecs.add, "test", f, "BAD")
