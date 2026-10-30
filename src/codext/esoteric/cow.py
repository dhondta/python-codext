# -*- coding: UTF-8 -*-
"""COW Codec - COW content encoding.

COW is an esoteric programming language created by Sean Heber in 2003, made of 12 variations of the word "moo". Its
 memory is a tape of integer cells, as in Brainfuck, with a register, and its instructions are: "MoO" and "MOo"
 (increment and decrement the cell), "moO" and "mOo" (move the pointer), "MOO" and "moo" (loop while the cell is not
 null), "Moo" (print the cell as a character, or read a character when it is null), "OOM" and "oom" (print or read the
 cell as an integer), "OOO" (reset the cell), "MMM" (copy the cell to the register, or the register to the cell) and
 "mOO" (execute the value of the cell as an instruction, 3 or an invalid one ending the program). Encoding generates a
 program that prints the text (as UTF-8), while decoding runs the program and returns its output.

The program is run as with the reference interpreter, including the quirks of its loops ("MOO" skips the instruction
 that follows it, "moo" the one that precedes it, when searching for their match). No input is available, cells being
 left unchanged by "Moo" and set to 0 by "oom". When decoding, instructions may be separated by whitespace ; other
 characters, ignored by the language as comments, are only accepted with a non-strict errors handling. A program that
 does not halt within 1000 steps per instruction (with a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://bigzaphod.github.io/COW/
"""
from ._brainfuck import *
from ..__common__ import *


__examples__ = {
    'enc(cow)':     {'': "", 'A': "moO MoO MoO MoO MoO MoO MoO MoO MoO MOO mOo MoO MoO MoO MoO MoO MoO MoO MoO moO MOo "
                               "moo mOo MoO Moo"},
    'dec(cow)':     {
        'MoO OOM':                                          "1\n",
        'MoO\nMMM moO MMM OOM':                             "1\n",
        'MoO MoO MOO MOo moO MoO mOo moo moO OOM':          "2\n",
        # "MOO" skips the instruction that follows it, hence matching the second "moo"
        'OOO MOO moo moo MoO OOM':                          "1\n",
        'MOO MoO MOO MoO moo moo MoO OOM':                  "1\n",
        # a "moo" right after a "MOO" counts twice when searching forward
        'MOO MoO MOO moo MoO OOM':                          "1\n",
        'MoO MoO MoO MoO MoO MoO mOO OOM':                  "7\n",
        'MoO MoO MoO mOO OOM':                              "",
        'OOO MOo mOO OOM':                                  "",
        'Moo oom OOM':                                      "0\n",
        'MOO':                                              "",
        'mOo':                                              None,
        'moo':                                              None,
        'MoO moo':                                          None,
        'MOO MoO':                                          None,
        'MoO OOM moo!':                                     None,
    },
    'enc-dec(cow)': ["", "Hello World!", "@random{256}", "Café, ñandú & 10€", "\x00a\x00"],
}
__guess__ = ["cow"]


COW = ["moo", "mOo", "moO", "mOO", "Moo", "MOo", "MoO", "MOO", "OOO", "MMM", "OOM", "oom"]
CODES = {w: i for i, w in enumerate(COW)}
# Brainfuck commands as COW instructions (without input, as "Moo" with a null cell reads a character)
BF2COW = {'+': "MoO", '-': "MOo", '>': "moO", '<': "mOo", '.': "Moo", '[': "MOO", ']': "moo"}


def cow_run(program, max_steps=None):
    """ Run a COW program (as a list of instruction codes) like the reference interpreter and return its output as
         bytes with the index of the failing instruction (None if the program ended normally). """
    mem, p, pc, reg, out, steps, n = [0], 0, 0, None, bytearray(), 0, len(program)
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * n)
    while pc < n:
        if (steps := steps + 1) > max_steps:
            raise ValueError(f"program did not halt within {max_steps} steps")
        i = program[pc]
        # mOO executes the value of the cell, 3 (itself) or an invalid instruction ending the program
        if i == 3:
            if mem[p] == 3 or mem[p] not in range(12):
                break
            i = mem[p]
        if i == 0:
            # moo searches backward for its MOO, skipping the previous instruction, then executes it
            if pc == 0:
                return bytes(out), pc
            q, level = pc - 1, 1
            while level > 0 and q > 0:
                q -= 1
                level += (program[q] == 0) - (program[q] == 7)
            if level != 0:
                return bytes(out), pc
            pc, i = q, 7
        if i == 1:
            if p == 0:
                return bytes(out), pc
            p -= 1
        elif i == 2:
            if (p := p + 1) == len(mem):
                mem.append(0)
        elif i == 4:
            # without input, a null cell is left unchanged
            if mem[p] != 0:
                out.append(mem[p] & 0xff)
        elif i == 5:
            mem[p] -= 1
        elif i == 6:
            mem[p] += 1
        elif i == 7 and mem[p] == 0:
            # MOO searches forward for its moo, skipping the next instruction ; a moo right after a MOO counts twice
            q, level = pc + 1, 1
            if q == n:
                break
            while level > 0:
                prev, q = program[q], q + 1
                if q == n:
                    break
                if program[q] == 7:
                    level += 1
                elif program[q] == 0:
                    level -= 1 + (prev == 7)
            if level != 0:
                return bytes(out), pc
            pc = q
        elif i == 8:
            mem[p] = 0
        elif i == 9:
            if reg is None:
                reg = mem[p]
            else:
                mem[p], reg = reg, None
        elif i == 10:
            out.extend(f"{mem[p]}\n".encode())
        elif i == 11:
            # without input, the integer read is 0
            mem[p] = 0
        pc += 1
    return bytes(out), None


def cow_encode(text, errors="strict"):
    return (r := " ".join(BF2COW[c] for c in bf_program(text.encode("utf-8"), True))), len(r)


def cow_decode(text, errors="strict"):
    _h, program, pos, i = handle_error("cow", errors, decode=True), [], [], 0
    while i < len(text):
        if text[i].isspace():
            i += 1
        elif (w := text[i:i+3]) in CODES:
            program.append(CODES[w])
            pos.append(i)
            i += 3
        else:
            # with a non-strict errors handling, other characters are ignored (as comments)
            _h(text[i], i)
            i += 1
    out, k = cow_run(program)
    if k is not None:
        # with a non-strict errors handling, the program stops at the failing instruction
        handle_error("cow", errors, decode=True, kind="instruction")(COW[program[k]], pos[k])
    return (r := ensure_str(out)), len(r)


add("cow", cow_encode, cow_decode, r"^cow$", printables_rate=1., expansion_factor=(40., .05))
