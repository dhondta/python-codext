# -*- coding: UTF-8 -*-
"""Brainfuck Codec - Brainfuck content encoding.

Brainfuck is an esoteric programming language created in 1993 by Urban Müller, working on a tape of 8-bit cells with
 a data pointer and 8 commands: "+" and "-" (increment and decrement the cell), ">" and "<" (move the pointer), "[" and
 "]" (loop while the cell is not null), "." (output the cell) and "," (input a byte into the cell). Encoding generates a
 program that prints the text (as UTF-8), while decoding runs the program and returns its output.

Whitespace is ignored ; other characters are comments in Brainfuck, hence they are only accepted with a non-strict
 errors handling (otherwise, any text would decode). A program that does not halt within 1000 steps per command (with
 a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://esolangs.org/wiki/Brainfuck
"""
from ._brainfuck import *
from ..__common__ import *


__examples__ = {
    'enc(brainfuck|brainf*ck|bf)': {'A': ">++++++++[<++++++++>-]<+.", '': ""},
    'dec(brainfuck)':              {
        # example program of Wikipedia
        "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.":
            "Hello World!\n",
        '+,.':                   "\x00",
        '[+].':                  "\x00",
        '+++\n.':                "\x03",
        '++ +.':                 "\x03",
        '++a.':                  None,
        '[+.':                   None,
        '+].':                   None,
        '<+':                    None,
        '+[]':                   None,
    },
    'enc-dec(brainfuck)':          ["", "Hello World!", "@random{256}", "Café, ñandú & 10€"],
}
__guess__ = ["brainfuck"]


COMMANDS = "+-<>[].,"


def brainfuck_encode(text, errors="strict"):
    return (r := bf_program(text.encode("utf-8"))), len(r)


def brainfuck_decode(text, errors="strict"):
    _h, code = handle_error("brainfuck", errors, decode=True), []
    for i, c in enumerate(text):
        if c in COMMANDS:
            code.append(c)
        elif not c.isspace():
            # with a non-strict errors handling, other characters are comments, as in Brainfuck
            _h(c, i)
    # positions of the commands in the text, for reporting unmatched brackets
    pos = [i for i, c in enumerate(text) if c in COMMANDS]
    return (r := ensure_str(bf_run(code, lambda i: _h(code[i], pos[i])))), len(r)


add("brainfuck", brainfuck_encode, brainfuck_decode, pattern=r"^(?:brainf(?:uck|\*ck)|bf)$", printables_rate=1.,
    expansion_factor=(13., .2))
