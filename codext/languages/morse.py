# -*- coding: UTF-8 -*-
"""Morse Codec - morse content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP = {
    # letters
    'a': ".-", 'b': "-...", 'c': "-.-.", 'd': "-..", 'e': ".", 'f': "..-.", 'g': "--.", 'h': "....",  'i': "..",
    'j': ".---", 'k': "-.-", 'l': ".-..", 'm': "--", 'n': "-.", 'o': "---", 'p': ".--.", 'q': "--.-", 'r': ".-.",
    's': "...", 't': "-", 'u': "..-", 'v': "...-", 'w': ".--", 'x': "-..-", 'y': "-.--", 'z': "--..",
    # digits
    '1': ".----", '2': "..---", '3': "...--", '4': "....-", '5': ".....", '6': "-....", '7': "--...", '8': "---..",
    '9': "----.", '0': "-----",
    # punctuation
    ',': "--..--", '.': ".-.-.-", ':' : "---...", '?': "..--..", '/': "-..-.", '-': "-....-", '=' : "-...-",
    '(': "-.--.", ')': "-.--.-", '@' : ".--.-.", '\'': ".----.", '_': "..--.-", '!': "-.-.--", '&': ".-...",
    '"': ".-..-.", ';': "-.-.-.", '$': "...-..-",
    # word separator
    ' ' : "/",
}


add_map("morse", ENCMAP, "#", " ", ignore_case="encode", pattern=r"^morse([-_]?.{3})?$")
