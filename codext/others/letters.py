# -*- coding: UTF-8 -*-
"""Letters Codec - letter indices-related content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_uppercase

from ..__common__ import *


__examples__ = {
    'enc(consonant-index|consonants_indices)': {
        'This is a test': "166I15I15A16E1516",
        '\x00':           None,
        '\xff':           None,
    },
    'dec(consonant-index|consonants_indices)': {
        '166I15I15A16E1516': "THISISATEST",
        '\x00':              None,
        '\xff':              None,
    },
    'enc(vowel-index|vowels_indices)': {'This is a test':               "TH3S3S1T2ST"},
    'dec(vowel-index|vowels_indices)': {'TH3S3S1T2ST':                  "THISISATEST"},
    'enc(consonant-vowel_indices)':    {'This is a test':               "C16C6V3C15V3C15V1C16V2C15C16"},
    'dec(consonants_vowels-index)':    {'C16C6V3C15V3C15V1C16V2C15C16': "THISISATEST"},
}
__guess__ = ["consonant-index", "vowel-index", "consonants_vowels-index"]


VOWELS = "AEIOUY"


def __get_encmap(letters):
    if re.match(r"^consonants?$", letters):
        encmap = {c: str(i+1) for i, c in enumerate(sorted(set(ascii_uppercase) - set(VOWELS)))}
        for c in VOWELS:
            encmap[c] = c
    elif re.match(r"^vowels?$", letters):
        encmap = {c: c for c in ascii_uppercase}
        for i, c in enumerate(VOWELS):
            encmap[c] = str(i+1)
    elif re.match(r"^consonants?[-_]vowels?$", letters):
        encmap = {c: "C" + str(i+1) for i, c in enumerate(sorted(set(ascii_uppercase) - set(VOWELS)))}
        for i, c in enumerate(VOWELS):
            encmap[c] = "V" + str(i+1)
    for c in " ":
        encmap[c] = ""
    return encmap


def letters_encode(letters):
    encmap = __get_encmap(letters)
    def encode(text, errors="strict"):
        s = ""
        for i, c in enumerate(text.upper()):
            try:
                s += encmap[c]
            except KeyError:
                s += handle_error(letters + "_indices", errors)(c, i)
        return "".join(encmap.get(c.upper(), c) for c in text), len(text)
    return encode


def letters_decode(letters):
    decmap = {v: k for k, v in __get_encmap(letters).items()}
    maxlen = max(len(x) for x in decmap.keys())
    def decode(text, errors="strict"):
        s, i = "", 0
        while i < len(text):
            err = True
            for j in range(maxlen, 0, -1):
                try:
                    s += decmap[text[i:i+j]]
                    i += j
                    err = False
                    break
                except (IndexError, KeyError):
                    pass
            if err:
                s += handle_error(letters + "_indices", errors, decode=True)(text[i], i)
        return s, len(text)
    return decode


add("letter-indices", letters_encode, letters_decode, printables_rate=1.,
    pattern=r"^(consonants?|vowels?|consonants?[-_]vowels?)[-_]ind(?:ex|ices)$")

