# -*- coding: UTF-8 -*-
"""Befunge Codec - Befunge-93 content encoding.

Befunge-93 is an esoteric programming language created by Chris Pressey in 1993, whose program is a two-dimensional
 grid of 80x25 cells (wrapping around on the edges) where an instruction pointer moves in four directions. It works on
 a stack of integers, with instructions for arithmetic, string mode ('"'), output (',' for a character, '.' for an
 integer), branching ('_' and '|'), bridging ('#') and self-modification ('g' and 'p'). Encoding generates an ASCII
 program that prints the text (as UTF-8), with rows of 80 cells snaking downward, while decoding runs the program and
 returns its output.

The program is run as with the reference interpreter (bef), cells holding signed characters and programs being read as
 UTF-8 bytes ; no input is available ('&' and '~' push -1), a division or a modulo by zero gives 0, '?' uses a seeded
 pseudo-random generator (so that decoding is reproducible) and the playfield is extended for programs larger than 80x25
 (e.g. when encoding long texts). Executing an unsupported instruction is only accepted with a non-strict errors
 handling. A program that does not halt within 1000 steps per instruction (with a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/catseye/Befunge-93/blob/master/doc/Befunge-93.markdown
"""
from functools import lru_cache
from random import Random

from ._brainfuck import MIN_STEPS, STEPS_PER_COMMAND
from ..__common__ import *


__examples__ = {
    'enc(befunge|befunge93|befunge-93)': {'': "@", 'Hello, World!': '"!dlroW ,olleH">:#,_@',
                                          'a"\n': '19+647*+"a">:#,_@'},
    'dec(befunge)': {
        # examples of the specification
        '665+*1-,@':                         "A",
        '665+*1-.@':                         "65 ",
        '>123#...@':                         "3 2 ",
        '123.$.@':                           "3 1 ",
        '123\\...@':                         "2 3 1 ",
        '65`.25`.@':                         "1 0 ",
        # the reference interpreter's "Hello world" (newline in the end) and a program in multiple rows
        '                 v\n>v"Hello world!"0<\n,:\n^_25*,@':      "Hello world!\n",
        'v\n>"ih",,v\n  @,+55<':                               "hi\n",
        # self-modification, string mode with spaces, bridging and wrapping around the edges of the playfield
        '"@"5 0p 5 5+1-.  ':                 "9 ",
        '"a b",,,@':                         "b a",
        '1#2.@':                             "1 ",
        '<@,"x"':                            "x",
        '^\n@\n,\n"\nA\n"':                   "A",
        # empty stack, division and modulo (by zero), input and out-of-bounds get and put
        '.:.@':                              "0 0 ",
        '0!.5!.@':                           "1 0 ",
        '0|\n >"d",@':                       "d",
        '?1.@':                              "1 ",
        '07-2/.07-2%.10/.10%.@':             "-3 -1 0 0 ",
        '&.~.@':                             "-1 -1 ",
        '99*9g.1 99*9p@':                    "0 ",
        '"z"x,@':                            None,
        '"\xe9"\\,,@':                       "\xe9",
    },
    'enc-dec(befunge)': ["", "Hello World!", "@random{256}", "@random{3000}", "Café, ñandú & 10€", "\x00a\x00",
                         "a" * 200, "b" * 76, "\"quoted\"\n"],
}
__guess__ = ["befunge"]


WIDTH, HEIGHT = 80, 25
DIRECTIONS = {'>': (1, 0), '<': (-1, 0), 'v': (0, 1), '^': (0, -1)}


def _signed(v):
    """ Value stored in a cell of the playfield (a signed character). """
    return (v + 128) % 256 - 128


def befunge_run(program, unsupported=None, max_steps=None):
    """ Run a Befunge-93 program like the reference interpreter and return its output as bytes.

    :param program:     program as bytes (rows separated by newlines)
    :param unsupported: function called with the row and column of an unsupported instruction (it may raise an error),
                         the instruction being then ignored
    :param max_steps:   maximum number of executed instructions, for stopping programs that do not halt (by default,
                         1000 per instruction, with a minimum of 1 million)
    """
    rows = [r[:-1] if r.endswith(b"\r") else r for r in program.split(b"\n")]
    w, h = max([WIDTH] + [len(r) for r in rows]), max(HEIGHT, len(rows))
    grid = [[_signed(c) for c in r.ljust(w)] for r in rows] + [[32] * w for _ in range(h - len(rows))]
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * sum(c != 32 for r in grid for c in r))
    stack, out, rand = [], bytearray(), Random(0)
    pop = lambda: stack.pop() if stack else 0
    x, y, dx, dy, string_mode, steps = 0, 0, 1, 0, False, 0
    while True:
        if (steps := steps + 1) > max_steps:
            raise ValueError(f"program did not halt within {max_steps} steps")
        c = grid[y][x]
        i = chr(c) if 0 <= c < 128 else ""
        if string_mode:
            if i == '"':
                string_mode = False
            else:
                stack.append(c)
        elif i in DIRECTIONS:
            dx, dy = DIRECTIONS[i]
        elif i.isdigit():
            stack.append(int(i))
        elif i in "+-*/%`\\":
            a, b = pop(), pop()
            if i == "+":
                stack.append(b + a)
            elif i == "-":
                stack.append(b - a)
            elif i == "*":
                stack.append(b * a)
            elif i in "/%":
                # integer division and modulo truncated toward zero, as in C ; by zero, the result is 0
                q = 0 if a == 0 else abs(b) // abs(a) * (1 if (a < 0) == (b < 0) else -1)
                stack.append(q if i == "/" else 0 if a == 0 else b - a * q)
            elif i == "`":
                stack.append(int(b > a))
            else:
                stack.extend([a, b])
        elif i == "!":
            stack.append(int(pop() == 0))
        elif i == "_":
            dx, dy = (-1 if pop() else 1), 0
        elif i == "|":
            dx, dy = 0, (-1 if pop() else 1)
        elif i == "?":
            dx, dy = rand.choice(list(DIRECTIONS.values()))
        elif i == '"':
            string_mode = True
        elif i == ":":
            v = pop()
            stack.extend([v, v])
        elif i == "$":
            pop()
        elif i == ".":
            out.extend(f"{pop()} ".encode())
        elif i == ",":
            out.append(pop() & 0xff)
        elif i == "#":
            x, y = (x + dx) % w, (y + dy) % h
        elif i in "gp":
            gy, gx = pop(), pop()
            inside = 0 <= gx < w and 0 <= gy < h
            if i == "g":
                stack.append(grid[gy][gx] if inside else 0)
            elif inside:
                grid[gy][gx] = _signed(pop())
            else:
                pop()
        elif i in "&~":
            # no input is available
            stack.append(-1)
        elif i == "@":
            return bytes(out)
        elif i != " " and unsupported:
            unsupported(y, x)
        x, y = (x + dx) % w, (y + dy) % h


@lru_cache()
def _numbers():
    """ Shortest postfix expressions made of digits, "+" and "*" for the values from 0 to 255. """
    best = {n: str(n) for n in range(10)}
    changed = True
    while changed:
        changed = False
        for a, ea in list(best.items()):
            for b, eb in list(best.items()):
                for n, op in [(a + b, "+"), (a * b, "*")]:
                    if n < 256 and (n not in best or len(ea) + len(eb) + 1 < len(best[n])):
                        best[n], changed = ea + eb + op, True
    return best


def befunge_encode(text, errors="strict"):
    if not (data := text.encode("utf-8")):
        return "@", 0
    # the bytes are pushed in reverse order, printable characters in string mode and the others as numbers ; they are
    #  then printed in a loop until the stack is empty (or with one "," per byte if a null byte would stop this loop)
    items, num = [], _numbers()
    for c in reversed(data):
        items.extend([("s", chr(c))] if 32 <= c < 127 and c != 34 else [("o", e) for e in num[c]])
    loop = 0 not in data
    tail = ">:#,_@" if loop else "," * len(data) + "@"
    if not loop:
        items.extend(("o", e) for e in tail)
    # first, try a single row
    cells, in_str = "", False
    for k, c in items:
        if (k == "s") != in_str:
            cells, in_str = cells + '"', not in_str
        cells += c
    cells += '"' * in_str + (tail if loop else "")
    if len(cells) <= WIDTH:
        return cells, len(text)
    # otherwise, rows of 80 cells snake downward: the even rows go rightward, between ">" and "v", and the odd ones go
    #  leftward, between "<" and "v" ; the string mode is closed at the end of each row
    rows, cur, in_str, cap = [], [], False, WIDTH - 2
    for k, c in items:
        if k == "s":
            if len(cur) + 2 + (not in_str) > cap:
                rows.append(cur + ['"'] * in_str)
                cur, in_str = [], False
            if not in_str:
                cur, in_str = cur + ['"'], True
            cur.append(c)
        else:
            if in_str:
                cur, in_str = cur + ['"'], False
            if len(cur) + 1 > cap:
                rows.append(cur)
                cur = []
            cur.append(c)
    cur += ['"'] * in_str
    if loop:
        # the loop takes the end of a rightward row, or a row of its own (reached from its first column)
        if len(rows) % 2 == 0 and len(cur) + len(tail) <= cap + 1:
            cur += list(tail)
        else:
            rows.append(cur)
            if len(rows) % 2:
                rows.append([])
            cur = list(tail[1:])
    rows.append(cur)
    lines = []
    for i, r in enumerate(rows):
        last = i == len(rows) - 1
        if i % 2 == 0:
            lines.append((">" + "".join(r)) if last else (">" + "".join(r).ljust(cap) + "v"))
        else:
            lines.append("v" + "".join(reversed(r)).rjust(cap) + "<")
    return "\n".join(lines), len(text)


def befunge_decode(text, errors="strict"):
    _h, program = handle_error("befunge", errors, decode=True, kind="instruction", item="row/column"), \
                  ensure_str(text).encode("utf-8")
    lines = program.split(b"\n")
    out = befunge_run(program, lambda y, x: _h(chr(lines[y][x]) if lines[y][x] < 128 else f"\\x{lines[y][x]:02x}",
                                               f"{y}/{x}"))
    return (r := ensure_str(out)), len(r)


add("befunge", befunge_encode, befunge_decode, r"^befunge(?:[-_]?93)?$", printables_rate=1.,
    expansion_factor=(1.2, .5))
