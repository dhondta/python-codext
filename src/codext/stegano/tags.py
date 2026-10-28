# -*- coding: UTF-8 -*-
"""Unicode Tags Codec - Unicode tag characters content encoding.

This codec hides ASCII text in the invisible characters of the Unicode Tags block (U+E0000 to U+E007F), each ASCII
 character being shifted by 0xE0000. This technique, also called ASCII smuggling, is used to hide instructions in the
 input of language models. The encoded string can be inserted anywhere in a cover text as, when decoding, every
 character out of the Tags block is ignored.

The wrapped variant surrounds the encoded text with the BEGIN tag (U+E0001) and the CANCEL TAG (U+E007F).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/
"""
from ..__common__ import *


__examples__ = {
    'enc(unicode-tags|unicode_tag|unicodetags|tags|tag-smuggling)': {'Hi!': "\U000e0048\U000e0069\U000e0021"},
    'enc(unicode-tags-wrapped|tags_wrapped)':                       {'Hi!': "\U000e0001\U000e0048\U000e0069\U000e0021"
                                                                            "\U000e007f"},
    'enc(unicode-tags)':                                            {'Caf\u00e9': None},
    'dec(unicode-tags)':                                            {'Hello \U000e0048\U000e0069 World': "Hi"},
    'dec(unicode-tags-wrapped)':                                    {'Hello \U000e0001\U000e0048\U000e0069\U000e007f'
                                                                     ' World': "Hi"},
    'enc-dec(unicode-tags)':                                        ["Hello, World!", "tab\tnew\nline\x01\x7f"],
    'enc-dec(unicode-tags-wrapped)':                                ["Hello, World!", "\x01wrapped\x7f"],
}
__guess__ = ["unicode-tags", "unicode-tags-wrapped"]


OFFSET, BEGIN, CANCEL = 0xe0000, "\U000e0001", "\U000e007f"


def tags_encode(wrapped=""):
    def encode(text, errors="strict"):
        # the replacement character is also hidden, so that it is kept when decoding
        r, _h = [], handle_error("unicode-tags", errors, repl_char=chr(OFFSET + ord("?")))
        for i, c in enumerate(ensure_str(text)):
            r.append(chr(OFFSET + ord(c)) if ord(c) < 128 else _h(c, i))
        if wrapped:
            r = [BEGIN] + r + [CANCEL]
        return (s := "".join(r)), len(s)
    return encode


def tags_decode(wrapped=""):
    def decode(text, errors="strict"):
        # characters out of the Tags block belong to the cover text, hence they are ignored
        t = "".join(c for c in ensure_str(text) if OFFSET <= ord(c) < OFFSET + 128)
        if wrapped:
            t = t[t.startswith(BEGIN):len(t)-t.endswith(CANCEL)]
        return (s := "".join(chr(ord(c) - OFFSET) for c in t)), len(s)
    return decode


add("unicode-tags", tags_encode, tags_decode,
    r"^(?:unicode[-_]?tags?|tags|tag[-_]smuggling)([-_]wrapped)?$")
