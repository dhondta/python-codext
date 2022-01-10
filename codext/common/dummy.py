# -*- coding: UTF-8 -*-
"""Dummy Codecs - simple string manipulations.

These are dummy codecs for manipulating strings, for use with other codecs in encoding/decoding chains.

These codecs:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import re

from ..__common__ import add


def replace(pair, *args):
    def code(input, error="strict"):
        return input.replace(pair[0], pair[1]), len(input)
    return code
add("replace", replace, replace, r"^replace[-_]?((?!.*(.).*\2)..)$", guess=None)
# important note:                                              ^
#                                           using "{2}" here instead will break the codec
#  this is due to the fact the codext.__common__.generate_string_from_regex DOES NOT handle ASSERT_NOT (?!) and will
#   faill to generate a valid instance in lookup(...) when an encoding name is to be generated to get the CodecInfo


def substitute(token, replacement):
    def code(input, error="strict"):
        return input.replace(token, replacement), len(input)
    return code
add("substitute", substitute, substitute, r"^substitute[-_]?(.*?)/(.*?)$", guess=None)


reverse = lambda i, e="strict": (i[::-1], len(i))
add("reverse", reverse, reverse)

word_reverse = lambda i, e="strict": (" ".join(w[::-1] for w in i.split()), len(i))
add("reverse-words", word_reverse, word_reverse, r"^reverse[-_]words$")

strip_spaces = lambda i, e="strict": (i.replace(" ", ""), len(i))
add("strip-spaces", strip_spaces, strip_spaces, guess=None)

