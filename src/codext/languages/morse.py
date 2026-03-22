# -*- coding: UTF-8 -*-
"""Morse Codec - morse content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(morse|morse/-.)': {'this is a test': "- .... .. ... / .. ... / .- / - . ... -"},
    'enc(morse-/AB)':      {'this is a test': "A BBBB BB BBB / BB BBB / BA / A B BBB A"},
    'enc(morse-01)':       {'this is a test': "0 1111 11 111 - 11 111 - 10 - 0 1 111 0"},
}
__guess__ = ["morse", "morse/_.", "morse-/01", "morse-01", "morse-/ab", "morse-ab", "morse-/AB", "morse-AB"]


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


add_map("morse", ENCMAP, "#", " ", ignore_case="encode", pattern=r"^morse([-_]?.{3})?$", printables_rate=1.,
        expansion_factor=(2.8, .6))

