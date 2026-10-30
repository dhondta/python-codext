# -*- coding: UTF-8 -*-
"""Tap code - Tap/knock code encoding.

The tap code (or knock code), used by prisoners of war (e.g. in Vietnam) to communicate by tapping on walls, writes each
 letter as its row and column in a 5x5 Polybius square, K being replaced by C. Each coordinate is written as dots
 (taps), as cryptii does: the row and the column are separated by a space and the letters by two spaces. The words are
 separated by " / " ; the "-inv" variant uses the reversed alphabet.

When decoding, the dots are read in pairs whatever separates them (e.g. spaces, commas or the blank braille pattern, as
 written by former versions of this codec), a "/" (or a space between blank braille patterns) giving a space.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Tap_code
           https://cryptii.com/pipes/tap-code
"""
from ..__common__ import *


__examples__ = {
    'enc(tap|knock-code|tap_code)': {
        'this is a test': ".... ....  .. ...  .. ....  .... ... / .. ....  .... ... / . . / .... ....  . .....  "
                          ".... ...  .... ....",
        'water':          "..... ..  . .  .... ....  . .....  .... ..",
        'Kick':           ". ...  .. ....  . ...  . ...",
        'test!':          None,
    },
    'dec(tap)': {
        # Wikipedia example, with commas
        '..... .., . ., .... ...., . ....., .... ..':                       "water",
        # as written by former versions of this codec
        ".... ....⠀.. ...⠀.. ....⠀.... ...⠀ ⠀.. ....⠀.... ...":            "this is",
        '/ . . //  . .. /':                                                 " a  b ",
        '. . .':                                                            None,
        '. ......':                                                         None,
        '. / .':                                                            None,
        '. . x':                                                            None,
    },
    'enc-dec(tap|tap-inv)': ["this is a test", "the quicc brown fox  jumps over the lazy dog", " ", ""],
}
__guess__ = ["tap", "tap-inv"]


ALPHABETS = {'': "abcdefghijlmnopqrstuvwxyz", 'inv': "abcdefghijlmnopqrstuvwxyz"[::-1]}


def tap_encode(variant=""):
    alphabet = ALPHABETS[variant]
    def encode(text, errors="strict"):
        _h, tokens = handle_error("tap", errors, sep="  "), []
        for i, c in enumerate(ensure_str(text).lower()):
            if c == " ":
                tokens.append("/")
            elif (c := "c" if c == "k" else c) in alphabet:
                r, c = divmod(alphabet.index(c), 5)
                tokens.append("." * (r + 1) + " " + "." * (c + 1))
            elif (t := _h(c, i).rstrip()):
                tokens.append(t)
        # two spaces between letters, one around the word separators
        r = "".join(("" if i == 0 else " " if "/" in (p, t) else "  ") + t for i, (p, t) in
                    enumerate(zip([None] + tokens, tokens)))
        return r, len(text)
    return encode


def tap_decode(variant=""):
    alphabet = ALPHABETS[variant]
    def decode(text, errors="strict"):
        _h, t = handle_error("tap", errors, decode=True, kind="token"), ensure_str(text)
        # alternating separators and runs of dots, starting and ending with a (possibly empty) separator
        parts, r, pos, row = re.split(r"(\.+)", t), "", 0, None
        for k, p in enumerate(parts):
            if k % 2:
                if len(p) > 5:
                    r += _h(p, pos)
                elif row is None:
                    row = len(p) - 1
                else:
                    r, row = r + alphabet[row * 5 + len(p) - 1], None
            else:
                for i, c in enumerate(p):
                    if not (c.isspace() or c in ",/⠀"):
                        r += _h(c, pos + i)
                # a "/" or, as with former versions of this codec, a space between blank braille patterns is a space
                n = p.count("/") if "/" in p else p.count(" ") if "⠀" in p else 0
                if n and row is not None:
                    # a space cannot separate the row and the column of a letter
                    r += _h(p, pos)
                    row = None
                r += " " * n
            pos += len(p)
        if row is not None:
            r += _h(parts[-2], pos - len(parts[-1]) - len(parts[-2]))
        return r, len(text)
    return decode


add("tap", tap_encode, tap_decode, r"^(?:tap|knock)(?:[-_]code)?(?:[-_]?(inv))?$", printables_rate=1.,
    expansion_factor=(7.5, .04))
