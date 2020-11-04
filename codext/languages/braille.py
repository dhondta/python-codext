# -*- coding: UTF-8 -*-
"""Braille Codec - braille content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(braille)': {'this is a test': "⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞"},
}


ENCMAP = {
    # digits
    '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
    # letters
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅',
    'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧',
    'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    # punctuation
    ' ': '⠀', '!': '⠮', '"': '⠐', '#': '⠼', '$': '⠫', '%': '⠩', '&': '⠯', ':': '⠱', ';': '⠰', '<': '⠣', '=': '⠿',
    '>': '⠜', '?': '⠹', '@': '⠈', "'": '⠄', '(': '⠷', ')': '⠾', '*': '⠡', '+': '⠬', ',': '⠠', '-': '⠤', '.': '⠨',
    '/': '⠌', '[': '⠪', '\\': '⠳', ']': '⠻', '^': '⠘', '_': '⠸',
}


if PY3:
    add_map("braille", ENCMAP, ignore_case="encode")

