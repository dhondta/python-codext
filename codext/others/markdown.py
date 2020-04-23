# -*- coding: UTF-8 -*-
"""Markdown Codec - markdown content conversion to HTML.

This codec:
- encodes strings from str to str
- encodes strings from bytes to bytes
- encodes file content from str to bytes (write)
"""
from markdown2 import markdown

from ..__common__ import *


def markdown_encode(mdtext, errors="strict"):
    return markdown(mdtext), len(mdtext)


# note: the group is NOT captured so that the pattern is only used to match the name of the codec and not to dynamically
#        bind to a parametrizable encode function
add("markdown", markdown_encode, pattern=r"^(?:markdown|Markdown|md)$")
