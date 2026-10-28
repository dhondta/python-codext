# -*- coding: UTF-8 -*-
"""Morse Codec - morse content encoding.

Morse code, developed by Samuel Morse and Alfred Vail for the electric telegraph in the 1830s-1840s, writes each
 character as a sequence of short and long signals (dots and dashes). This codec uses the International Morse Code for
 letters, digits and punctuation, the characters being separated by spaces and the words by "/" ; the word separator,
 the dash and the dot symbols can be replaced in the codec name (e.g. "morse-/AB" or "morse-01").

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Morse_code
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

