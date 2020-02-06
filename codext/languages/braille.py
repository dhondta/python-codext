# -*- coding: UTF-8 -*-
"""Braille Codec - braille content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


if PY3:
    ENCMAP = {
        # digits
        '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖',
        '7': '⠶', '8': '⠦', '9': '⠔',
        # letters
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛',
        'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝',
        'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥',
        'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
        # punctuation
        ' ': '⠀', '!': '⠮', '"': '⠐', '#': '⠼', '$': '⠫', '%': '⠩', '&': '⠯',
        ':': '⠱', ';': '⠰', '<': '⠣', '=': '⠿', '>': '⠜', '?': '⠹', '@': '⠈',
        "'": '⠄', '(': '⠷', ')': '⠾', '*': '⠡', '+': '⠬', ',': '⠠', '-': '⠤',
        '.': '⠨', '/': '⠌', '[': '⠪', '\\': '⠳', ']': '⠻', '^': '⠘',
        '_': '⠸',
    }
    DECMAP = {v: k for k, v in ENCMAP.items()}
    REPLACE_CHAR = "?"


    class BrailleError(ValueError):
        pass


    class BrailleDecodeError(BrailleError):
        pass


    class BrailleEncodeError(BrailleError):
        pass


    def braille_encode(text, errors="strict"):
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += ENCMAP[c]
            except KeyError:
                if errors == "strict":
                    raise BrailleEncodeError("'braille' codec can't encode "
                                             "character '{}' in position {}"
                                             .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)


    def braille_decode(text, errors="strict"):
        r = ""
        for i, c in enumerate(ensure_str(text)):
            try:
                r += DECMAP[c]
            except KeyError:
                if errors == "strict":
                    raise BrailleDecodeError("'braille' codec can't decode "
                                             "character '{}' in position {}"
                                             .format(c, i))
                elif errors == "replace":
                    r += REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        return r, len(text)


    add("braille", braille_encode, braille_decode)
