# -*- coding: UTF-8 -*-
"""Nokia Codec - nokia keystrokes content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from .__common__ import *


DECMAP = {
    '2': "a", '22': "b", '222': "c",
    '3': "d", '33': "e", '333': "f",
    '4': "g", '44': "h", '444': "i",
    '5': "j", '55': "k", '555': "l",
    '6': "m", '66': "n", '666': "o",
    '7': "p", '77': "q", '777': "r", '7777': "s",
    '8': "t", '88': "u", '888': "v",
    '9': "w", '99': "x", '999': "y", '9999': "z",
    '0': " ",
}
ENCMAP = {v: k for k, v in DECMAP.items()}
REPLACE_CHAR = "?"


class NokiaError(ValueError):
    pass


class Nokia3310DecodeError(NokiaError):
    pass


def nokia3310_encode(text, errors="strict"):
    r = []
    for c in text:
        r.append(ENCMAP[c.lower()])
    return "-".join(r), len(text)


def nokia3310_decode(text, errors="strict"):
    r = ""
    for i, t in enumerate(re.split(r"[_\-\s]", text)):
        try:
            r += DECMAP[t]
        except KeyError:
            if errors == "strict":
                raise Nokia3310DecodeError("'nokia3310' codec can't decode "
                                           "token '{}' in position {}"
                                           .format(t, i))
            elif errors == "replace":
                r += REPLACE_CHAR
            elif errors == "ignore":
                continue
            else:
                raise ValueError("Unsupported error handling {}".format(errors))
    return r, len(text)


add("nokia3310", nokia3310_encode, nokia3310_decode, r"nokia[-_]?3310$")
