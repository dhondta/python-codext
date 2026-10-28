# -*- coding: UTF-8 -*-
"""Braille Codec - braille content encoding.

Braille, created by Louis Braille in 1824, writes characters as cells of 6 raised dots read by touch. This codec writes
 each character with the Unicode braille pattern of the Braille ASCII correspondence (uncontracted letters, digits as
 lower-cell patterns and punctuation), a space being written as the blank braille pattern U+2800.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Braille_ASCII
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


add_map("braille", ENCMAP, ignore_case="encode")

