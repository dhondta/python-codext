# -*- coding: UTF-8 -*-
"""Brainfuck core, shared by the codecs of Brainfuck and of the esoteric languages derived from it (e.g. Pikalang,
 COW).

Brainfuck works on a tape of 8-bit cells (wrapping around) with a data pointer, using 8 commands: "+" and "-"
 (increment and decrement the cell), ">" and "<" (move the pointer), "[" and "]" (loop while the cell is not null), "."
 (output the cell) and "," (input a byte into the cell, 0 here as no input is available).
"""


MIN_STEPS, STEPS_PER_COMMAND = 10 ** 6, 1000


def bf_program(data, nonzero=False):
    """ Generate a Brainfuck program that prints the given bytes. It uses the first cell for the output and, for large
         differences between successive bytes, the second one as the counter of a multiplication loop.
    
    :param data:    bytes to be printed
    :param nonzero: for languages whose cells are not reduced modulo 256 and that cannot print a null cell (e.g. COW),
                     the first cell is kept away from 0 (a null byte being printed from 256 or -256)
    """
    code, v = [], 0
    for t in data:
        d = (t - v + 128) % 256 - 128
        if nonzero and v + d == 0:
            d += 256 if d <= 0 else -256
        op, n = "+-"[d < 0], abs(d)
        # either add the difference directly, or as a * b + c with a loop of a iterations adding b
        best = op * n
        for a in range(2, 17):
            b, c = divmod(n, a)
            if c > a // 2:
                b, c = b + 1, c - a
            if b > 0 and a + b + abs(c) + 7 < len(best):
                best = ">" + "+" * a + "[<" + op * b + ">-]<" + ("+-"[(op == "-") != (c < 0)]) * abs(c)
        code.append(best + ".")
        v = v + d if nonzero else t
    return "".join(code)


def bf_run(code, unmatched=None, max_steps=None):
    """ Run a Brainfuck program (made of commands only) and return its output as bytes.

    :param code:      Brainfuck commands
    :param unmatched: function called with the index of an unmatched bracket (it may raise an error), the bracket being
                       then ignored
    :param max_steps: maximum number of executed commands, for stopping programs that do not halt (by default, 1000
                       per command, with a minimum of 1 million)
    """
    code, stack, jumps = list(code), [], {}
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * len(code))
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if len(stack) == 0:
                if unmatched:
                    unmatched(i)
                code[i] = ""
            else:
                j = stack.pop()
                jumps[i], jumps[j] = j, i
    for i in stack:
        if unmatched:
            unmatched(i)
        code[i] = ""
    tape, p, i, steps, out = [0], 0, 0, 0, bytearray()
    while i < len(code):
        if (steps := steps + 1) > max_steps:
            raise ValueError(f"program did not halt within {max_steps} steps")
        c = code[i]
        if c == "+":
            tape[p] = (tape[p] + 1) % 256
        elif c == "-":
            tape[p] = (tape[p] - 1) % 256
        elif c == ">":
            if (p := p + 1) == len(tape):
                tape.append(0)
        elif c == "<":
            if (p := p - 1) < 0:
                raise ValueError("data pointer moved before the first cell")
        elif c == "[" and tape[p] == 0 or c == "]" and tape[p] != 0:
            i = jumps[i]
        elif c == ".":
            out.append(tape[p])
        elif c == ",":
            tape[p] = 0
        i += 1
    return bytes(out)
