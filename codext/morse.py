# -*- coding: UTF-8 -*-
"""Morse Codec - morse content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from .__common__ import *


ENCMAP = {
    # letters
    'a': ".-", 'b': "-...", 'c': "-.-.", 'd': "-..", 'e': ".", 'f': "..-.",
    'g': "--.", 'h': "....",  'i': "..", 'j': ".---", 'k': "-.-", 'l': ".-..",
    'm': "--", 'n': "-.", 'o': "---", 'p': ".--.", 'q': "--.-", 'r': ".-.",
    's': "...", 't': "-", 'u': "..-", 'v': "...-", 'w': ".--", 'x': "-..-",
    'y': "-.--", 'z': "--..",
    # digits
    '1': ".----", '2': "..---", '3': "...--", '4': "....-", '5': ".....",
    '6': "-....", '7': "--...", '8': "---..", '9': "----.", '0': "-----",
    # punctuation
    ',': "--..--", '.': ".-.-.-", ':' : "---...", '?': "..--..", '/': "-..-.",
    '-': "-....-", '=' : "-...-", '(': "-.--.", ')': "-.--.-", '@' : ".--.-.",
    '\'': ".----.", '_': "..--.-", '!': "-.-.--", '&': ".-...", '"': ".-..-.",
    ';': "-.-.-.", '$': "...-..-",
    # word separator
    ' ' : "/",
}
DECMAP = {v: k for k, v in ENCMAP.items()}
REPLACE_CHAR = "#"


class MorseError(ValueError):
    pass


class MorseDecodeError(MorseError):
    pass


class MorseEncodeError(MorseError):
    pass


def morse_encode(text, errors="strict"):
    r = ""
    for i, c in enumerate(ensure_str(text)):
        try:
            r += ENCMAP[c] + " "
        except KeyError:
            if errors == "strict":
                raise MorseEncodeError("'morse' codec can't encode character "
                                       "'{}' in position {}".format(c, i))
            elif errors == "replace":
                r += REPLACE_CHAR + " "
            elif errors == "ignore":
                continue
            else:
                raise ValueError("Unsupported error handling {}".format(errors))
    return r[:-1], len(text)


def morse_decode(text, errors="strict"):
    r = ""
    for i, c in enumerate(ensure_str(text).split()):
        try:
            r += DECMAP[c]
        except KeyError:
            if errors == "strict":
                raise MorseDecodeError("'morse' codec can't decode character "
                                       "'{}' in position {}".format(c, i))
            elif errors == "replace":
                r += REPLACE_CHAR
            elif errors == "ignore":
                continue
            else:
                raise ValueError("Unsupported error handling {}".format(errors))
    return r, len(text)


add("morse", morse_encode, morse_decode)
