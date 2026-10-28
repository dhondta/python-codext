# -*- coding: UTF-8 -*-
"""Resistor Codec - resistor color codes content encoding.

The electronic color code (IEC 60062) marks the values of resistors and capacitors with colored bands, one per digit:
 black (0), brown, red, orange, yellow, green, blue, violet, grey and white (9). Each character is replaced by the
 colors of the digits of its ordinal, displayed as colored blocks using ANSI escape sequences (hence for terminals).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Electronic_color_code
"""
from ..__common__ import *


__examples__ = {
    'enc(resistor|resistor_color|condensator_color_code|condensators-color-code)': {
        'Test': "\x1b[48;5;232m \x1b[0;00m\x1b[48;5;245m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m\x1b[48;5;130m "
                "\x1b[0;00m\x1b[48;5;232m \x1b[0;00m\x1b[48;5;130m \x1b[0;00m\x1b[48;5;130m \x1b[0;00m\x1b[48;5;130m "
                "\x1b[0;00m\x1b[48;5;2m \x1b[0;00m\x1b[48;5;130m \x1b[0;00m\x1b[48;5;130m \x1b[0;00m\x1b[48;5;4m "
                "\x1b[0;00m"
    },
}


ENCMAP = {i: "\033[48;5;%dm \033[0;00m" % c for i, c in zip("0123456789", [232, 130, 1, 214, 11, 2, 4, 129, 245, 231])}


add_map("resistor", ENCMAP, intype="ord", pattern=r"^(?:condensator|resistor)s?(?:[-_]color(?:[-_]code)?)?$",
        entropy=3.4, printables_rate=.3333333333333333, expansion_factor=(56., 2.))

