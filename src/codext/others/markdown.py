# -*- coding: UTF-8 -*-
"""Markdown Codec - markdown content conversion to HTML.

This codec:
- encodes strings from str to str
- encodes strings from bytes to bytes
- encodes file content from str to bytes (write)
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

