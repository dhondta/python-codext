# -*- coding: UTF-8 -*-
"""Case Codecs - simple string case manipulations.

These are case-related codecs for manipulating strings, for use with other codecs in encoding/decoding chains.

These codecs:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import re

from ..__common__ import add


pascal = lambda i, e="strict": ("".join(x.capitalize() for x in re.findall(r"[0-9a-z]+", i.lower())), len(i))
add("camel", lambda i, e: uncapitalize(pascal(i, e)[0]), None, r"^camel(?:[-_]?case)?$")
add("pascal", pascal, None, r"^pascal(?:[-_]?case)?$")

capitalize = lambda i, e="strict": (i.capitalize(), len(i))
uncapitalize = lambda i, e="strict": (i[0].lower() + i[1:] if len(i) > 0 else "", len(i))
add("capitalize", capitalize, uncapitalize)

lowercase = lambda i, e="strict": (i.lower(), len(i))
uppercase = lambda i, e="strict": (i.upper(), len(i))
add("uppercase", uppercase, lowercase, r"^upper(?:case)?$")
add("lowercase", lowercase, uppercase, r"^lower(?:case)?$")

slugify = lambda i, e="strict", d="-": (re.sub(r"[^0-9a-z]+", d, i.lower()).strip(d), len(i))
add("slugify", lambda i, e: slugify(i, e), None, r"^(?:slug(?:ify)?|kebab(?:[-_]?case)?)$")
add("snake", lambda i, e: slugify(i, e, "_"), None, r"^snake(?:[-_]?case)$")

swapcase = lambda i, e="strict": (i.swapcase(), len(i))
add("swapcase", swapcase, swapcase, r"^swap(?:[-_]?case)?$")

title = lambda i, e="strict": (i.title(), len(i))
untitle = lambda i, e="strict": (" ".join(w[0].lower() + w[1:] if len(w) > 0 else "" for w in i.split()), len(i))
add("title", title, untitle)

