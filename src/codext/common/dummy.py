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

from ..__common__ import *


def replace(pair, *args):
    def code(input, errors="strict"):
        return input.replace(pair[0], pair[1]), len(input)
    return code
add("replace", replace, replace, r"^replace[-_]?((?!.*(.).*\2)..)$", guess=None)
# important note:                                              ^
#                                           using "{2}" here instead will break the codec
#  this is due to the fact the codext.__common__.generate_string_from_regex DOES NOT handle ASSERT_NOT (?!) and will
#   fail to generate a valid instance in lookup(...) when an encoding name is to be generated to get the CodecInfo


def substitute(token, replacement):
    def code(input, errors="strict"):
        return input.replace(token, replacement), len(input)
    return code
add("substitute", substitute, substitute, r"^substitute[-_]?(.*?)/(.*?)$", guess=None)


reverse = lambda i, e="strict": (i[::-1], len(i))
add("reverse", reverse, reverse)

_revl = lambda i, wd=False: "".join((" ".join(w[::-1] for w in l.split()) if wd else l[::-1]) \
                                    if not re.match(r"(\r?\n)", l) else l for l in re.split(r"(\r?\n)", i))
line_reverse = lambda i, e="strict": (_revl(i), len(i))
add("reverse-lines", line_reverse, line_reverse, r"^reverse[-_]lines$")
word_reverse = lambda i, e="strict": (_revl(i, True), len(i))
add("reverse-words", word_reverse, word_reverse, r"^reverse[-_]words$")

strip_spaces = lambda i, e="strict": (i.replace(" ", ""), len(i))
add("strip-spaces", strip_spaces, strip_spaces, guess=None)

def tokenize(n):
    tlen = int(n[8:].lstrip("-_"))
    def code(input, errors="strict"):
        l = len(input)
        if tlen > l:
            raise LookupError("unknown encoding: %s" % n)
        return " ".join(input[i:i+tlen] for i in range(0, l, tlen)), l
    return code
add("tokenize", tokenize, tokenize, r"^(tokenize[-_]?[1-9][0-9]*)$", guess=None)

