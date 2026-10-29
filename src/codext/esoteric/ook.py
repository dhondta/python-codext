# -*- coding: UTF-8 -*-
"""Ook! Codec - Ook! content encoding.

Ook! is an esoteric programming language created by David Morgan-Mar, derived from Brainfuck and designed to be read and
 written by orang-utans: each command is a pair of the words "Ook.", "Ook?" and "Ook!", e.g. "Ook. Ook?" for ">" and
 "Ook! Ook." for ".". Encoding generates a program that prints the text (as UTF-8), while decoding runs the program and
 returns its output. The "-short" variant (also known as Short Ook!) only keeps the punctuation marks (e.g. ".?" for
 ">").

When decoding, both forms are accepted (case-insensitive), whitespace being ignored. A program that does not halt within
 1000 steps per command (with a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dangermouse.net/esoteric/ook.html
"""
from ._brainfuck import *
from ..__common__ import *


__examples__ = {
    'enc(ook|ook!)': {'': "", 'A': (
        "Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. "
        "Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. "
        "Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook. Ook. "
        "Ook! Ook."
    )},
    'enc(ook-short|short_ook)':     {'A': ".?................!??..................?!!?!?...!."},
    'dec(ook|ook-short)':           {
        ".?................!??..................?!!?!?...!.": "A",
        (
            "Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. "
            "Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. "
            "Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook. Ook. "
            "Ook! Ook."
        ): "A",
        'ook. OOK. ook! ook.':  "\x01",
        'Ook. .\n!.':           "\x01",
        'Ook. Ook. Ook! Ook':   None,
        'Ook. Ook. Ook!':       None,
        'Ook! Ook? Ook! Ook.':  None,
        'Ook? Ook. Ook. Ook.':  None,
        'Ook. Ook. Ook! Ook? Ook? Ook!': None,
    },
    'enc-dec(ook|ook-short)':       ["", "Hello World!", "@random{256}", "Café, ñandú & 10€"],
}
__guess__ = ["ook", "ook-short"]


# Brainfuck commands as pairs of punctuation marks, the full form adding "Ook" before each mark
OOK = {'>': ".?", '<': "?.", '+': "..", '-': "!!", '.': "!.", ',': ".!", '[': "!?", ']': "?!"}
KOO = {v: k for k, v in OOK.items()}
TOKEN = re.compile(r"(?:ook)?([.?!])", re.I)


def ook_encode(short=False, short2=False):
    # the full form writes each punctuation mark as a word ("Ook" and the mark), separated by spaces
    word, sep = ["Ook", ""][bool(short or short2)], [" ", ""][bool(short or short2)]
    def encode(text, errors="strict"):
        code = bf_program(text.encode("utf-8"))
        return (r := sep.join(word + m for c in code for m in OOK[c])), len(r)
    return encode


def ook_decode(short=False, short2=False):
    def decode(text, errors="strict"):
        _h, marks, i = handle_error("ook", errors, decode=True), [], 0
        # the words (or the punctuation marks only) are taken one by one, whitespace being ignored
        while i < len(text):
            if text[i].isspace():
                i += 1
            elif m := TOKEN.match(text, i):
                marks.append((m.group(1), i, m.end()))
                i = m.end()
            else:
                # with a non-strict errors handling, other characters are ignored
                _h(text[i], i)
                i += 1
        if len(marks) % 2:
            # an Ook! program always holds an even number of words
            _h(text[marks[-1][1]:marks[-1][2]], marks[-1][1])
            marks.pop()
        # the commands, with their words in the text and positions for reporting errors
        code, src = [], []
        for (a, i, _), (b, _, j) in zip(marks[::2], marks[1::2]):
            src.append((" ".join(text[i:j].split()), i))
            try:
                code.append(KOO[a + b])
            except KeyError:
                # "Ook? Ook?" is not a command
                _h(*src[-1])
                code.append("")
        return (r := ensure_str(bf_run(code, lambda k: _h(*src[k])))), len(r)
    return decode


add("ook", ook_encode, ook_decode, r"^(?:(short)[-_]ook|ook!?(?:[-_](short))?)$", printables_rate=1.,
    # a Brainfuck command takes 10 characters ("Ook. Ook? ") or 2 with the short form, for 4 to 25 commands per byte
    expansion_factor=lambda f, e: (20., .1) if "short" in e else (100., .02))
