# -*- coding: UTF-8 -*-
"""Resistor Codec - resistor color codes content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP = {i: "\033[48;5;%dm \033[0;00m" % c for i, c in zip("0123456789", [232, 130, 1, 214, 11, 2, 4, 129, 245, 231])}
ENCMAP[' '] = "/"


add_map("resistor", ENCMAP, pattern=r"^resistors?(?:[-_]color(?:[-_]code)?)?$")
