# -*- coding: UTF-8 -*-
"""Markdown Codec - markdown content conversion to HTML.

Markdown, created by John Gruber and Aaron Swartz in 2004, is a lightweight markup language for writing formatted text
 in plain text. This codec converts Markdown to HTML (one-way), relying on the markdown2 package (only available when it
 is installed).

This codec:
- encodes strings from str to str
- encodes strings from bytes to bytes
- encodes file content from str to bytes (write)

Reference: https://daringfireball.net/projects/markdown/
"""
from ..__common__ import *


__guess__ = []


try:
    from markdown2 import markdown as md2html
    # note: the group is NOT captured so that the pattern is only used to match the name of the codec and not to
    #        dynamically bind to a parametrizable encode function
    add("markdown", lambda md, error="strict": (md2html(md), len(md)), pattern=r"^(?:markdown|Markdown|md)$")
except ImportError:
    pass

