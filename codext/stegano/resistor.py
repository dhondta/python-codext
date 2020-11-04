# -*- coding: UTF-8 -*-
"""Resistor Codec - resistor color codes content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
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


add_map("resistor", ENCMAP, intype="ord", pattern=r"^(?:condensator|resistor)s?(?:[-_]color(?:[-_]code)?)?$")

