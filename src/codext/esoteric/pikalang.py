# -*- coding: UTF-8 -*-
"""Pikalang Codec - Pikalang content encoding.

Pikalang is an esoteric programming language derived from Brainfuck, based on the vocabulary of Pikachu from Pokémon:
 "pi" (+), "ka" (-), "pipi" (>), "pichu" (<), "pika" ([), "chu" (]), "pikachu" (.) and "pikapi" (,). Encoding generates
 a program that prints the text (as UTF-8), while decoding runs the program and returns its output. The words are
 separated by whitespace ; a program that does not halt within 1000 steps per word (with a minimum of 1 million) is
 stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/groteworld/pikalang
"""
from ._brainfuck import *
from ..__common__ import *


__examples__ = {
    'enc(pikalang)':   {'A': "pipi pi pi pi pi pi pi pi pi pika pichu pi pi pi pi pi pi pi pi pipi ka chu pichu pi "
                             "pikachu", '': ""},
    'dec(pikalang)':   {
        # example program of the reference implementation
        "pi pi pi pi pi pi pi pi pi pi pika pipi pi pi pi pi pi pi pi pipi pi pi pi pi pi pi pi pi pi pi pipi pi pi "
        "pi pipi pi pichu pichu pichu pichu ka chu pipi pi pi pikachu pipi pi pikachu pi pi pi pi pi pi pi pikachu "
        "pikachu pi pi pi pikachu pipi pi pi pikachu pichu pichu pi pi pi pi pi pi pi pi pi pi pi pi pi pi pi pikachu "
        "pipi pikachu pi pi pi pikachu ka ka ka ka ka ka pikachu ka ka ka ka ka ka ka ka pikachu pipi pi pikachu pipi "
        "pikachu": "Hello World!\n",
        'pi pikapi pikachu':     "\x00",
        'pika pi chu pikachu':   "\x00",
        'pi pi pi\npikachu':     "\x03",
        'pikachu pikachu pikap': None,
        'pika pi pikachu':       None,
        'pi chu pikachu':        None,
        'pichu pi':              None,
        'pi pika chu':           None,
    },
    'enc-dec(pikalang)': ["", "Hello World!", "@random{256}", "Café, ñandú & 10€"],
}
__guess__ = ["pikalang"]


ENCMAP = {'+': "pi", '-': "ka", '>': "pipi", '<': "pichu", '[': "pika", ']': "chu", '.': "pikachu", ',': "pikapi"}
DECMAP = {v: k for k, v in ENCMAP.items()}


def pikalang_encode(text, errors="strict"):
    return (r := " ".join(ENCMAP[c] for c in bf_program(text.encode("utf-8")))), len(r)


def pikalang_decode(text, errors="strict"):
    _h, code, tokens = handle_error("pikalang", errors, decode=True, kind="word"), [], text.split()
    for i, t in enumerate(tokens):
        try:
            code.append(DECMAP[t])
        except KeyError:
            # with a non-strict errors handling, unknown words are ignored (as comments in Brainfuck)
            _h(t, i)
            code.append("")
    return (r := ensure_str(bf_run(code, lambda i: _h(tokens[i], i)))), len(r)


add("pikalang", pikalang_encode, pikalang_decode, printables_rate=1., expansion_factor=(60., .045))
