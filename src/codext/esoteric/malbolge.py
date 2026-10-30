# -*- coding: UTF-8 -*-
"""Malbolge Codec - Malbolge content encoding.

Malbolge is an esoteric programming language created by Ben Olmstead in 1998, designed to be as difficult to program in
 as possible. It runs on a ternary virtual machine with 59049 words of 10 trits, holding both the code and the data, and
 three registers (A, the accumulator, C, the code pointer, and D, the data pointer). The instruction executed depends on
 the character at C and on its position ((C + [C]) % 94): "j" (D = [D]), "i" (C = [D]), "*" (A = [D] = [D] rotated to
 the right), "p" (A = [D] = crazy operation of A and [D]), "<" (output A modulo 256), "/" (input to A), "v" (stop) and
 "o" (nop), the executed character being then enciphered. Encoding generates a program that prints the text (as UTF-8),
 while decoding runs the program and returns its output.

The program is run as with the reference interpreter ("<" being the output, as in the reference interpreter, and not
 the input as in the specification), the cases left undefined by the reference interpreter being handled as in the
 specification: executing a character that is not graphic ASCII ends the program and a modified cell that is no longer
 graphic ASCII is not enciphered. No input is available ("/" gives the end of file, 59048). The program must have at
 least two instructions ; whitespace is ignored and invalid characters are only accepted (and skipped) with a non-strict
 errors handling. A program that does not halt within 1000 steps per instruction (with a minimum of 1 million) is
 stopped.

Encoding searches, for each byte, the shortest sequence of "o", "p", "*" and "j" that sets A to this byte (modulo 256)
 before printing it with "<", "j" moving the data pointer back to cells already executed (holding values written by
 former instructions) so that all the bytes can be reached.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.lscheffer.com/malbolge_spec.html
           https://esolangs.org/wiki/Malbolge
"""
from ._brainfuck import MIN_STEPS, STEPS_PER_COMMAND
from ..__common__ import *


__examples__ = {
    'enc(malbolge|mb)': {'': "DP", 'A': ">CB;@?>=<;4XE", 'Hi': "DCBA@?>=6;:981U543210/.-&%*#G4"},
    'dec(malbolge)': {
        # Hello World program from Wikipedia and program printing 42 from the Esoteric File Archive
        "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc": "Hello World!",
        "'&%$#\"!76543210/43,P0).'&%I6":                                      "42",
        # whitespace is ignored
        "D\n P ":                                                             "",
        # less than two instructions, invalid characters
        "Q":                                                                   None,
        "D\xe9P":                                                             None,
        "DQ":                                                                  None,
    },
    'enc-dec(malbolge)': ["", "Hello World!", "@random{64}", "Caf\xe9, \xf1and\xfa & 10\u20ac", "\x00a\x00"],
}
__guess__ = ["malbolge"]


SIZE = 3 ** 10
XLAT1 = "+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI.v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha"
XLAT2 = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@"
# crazy operation on trits, as CRAZY[trit of [D]][trit of A], then on pairs of trits
CRAZY = [[1, 0, 0], [1, 0, 2], [2, 2, 1]]
_CRAZY9 = [[CRAZY[d // 3][a // 3] * 3 + CRAZY[d % 3][a % 3] for a in range(9)] for d in range(9)]


def crazy(a, d):
    """ Tritwise crazy operation of A and [D]. """
    r, p = 0, 1
    for _ in range(5):
        r += _CRAZY9[d % 9][a % 9] * p
        a, d, p = a // 9, d // 9, p * 9
    return r


def rotr(v):
    """ Rotate a word to the right by one trit. """
    return v // 3 + v % 3 * 3 ** 9


# values (character codes) of the instructions at each position (modulo 94)
_VALUES = {i: [33 + (XLAT1.index(i) - k) % 94 for k in range(94)] for i in "ji*p</vo"}


def _value(i, instruction):
    """ Value (character code) of the given instruction at the given position. """
    return _VALUES[instruction][i % 94]


def _step(state, instruction, c, cells):
    """ Simulate an instruction at position c of the program being encoded, from the state (A, D, cells modified while
         searching), cells holding the values of the executed part of the program ; the data pointer never goes ahead
         of the code pointer, as the next cells are not known yet. """
    a, d, new = state
    v = _value(c, instruction)
    get = lambda x: v if x == c else new.get(x, cells.get(x))
    new = dict(new)
    if instruction == "j":
        if (d := get(d)) > c:
            return
    elif instruction == "*":
        a = new[d] = rotr(get(d))
    elif instruction == "p":
        a = new[d] = crazy(a, get(d))
    # the executed character is enciphered (or the value written in its cell, if graphic ASCII)
    w = new.get(c, v)
    new[c] = ord(XLAT2[w - 33]) if 33 <= w <= 126 else w
    return a, d + 1, new


def malbolge_run(program, max_steps=None):
    """ Run a Malbolge program (as a list of character codes) and return its output as bytes.

    :param program:   list of the values of the instructions
    :param max_steps: maximum number of executed instructions, for stopping programs that do not halt (by default,
                       1000 per instruction, with a minimum of 1 million)
    """
    # the remaining memory is filled with the crazy operation of the previous word and of the second previous one,
    #  lazily (up to the highest address used), from the last two initial words
    mem, (x, y) = list(program), program[-2:]
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * len(program))
    a, c, d, out = 0, 0, 0, bytearray()
    for _ in range(max_steps):
        while len(mem) <= max(c, d):
            x, y = y, crazy(y, x)
            mem.append(y)
        if not 33 <= mem[c] <= 126:
            # a character that is not graphic ASCII ends the program
            return bytes(out)
        i = XLAT1[(mem[c] - 33 + c) % 94]
        if i == "j":
            d = mem[d]
        elif i == "i":
            c = mem[d]
        elif i == "*":
            a = mem[d] = rotr(mem[d])
        elif i == "p":
            a = mem[d] = crazy(a, mem[d])
        elif i == "<":
            out.append(a % 256)
        elif i == "/":
            # no input is available, hence the end of file
            a = SIZE - 1
        elif i == "v":
            return bytes(out)
        if 33 <= mem[c] <= 126:
            mem[c] = ord(XLAT2[mem[c] - 33])
        c, d = (c + 1) % SIZE, (d + 1) % SIZE
    raise ValueError(f"program did not halt within {max_steps} steps")


def malbolge_encode(text, errors="strict"):
    # for each byte, a breadth-first search finds the shortest sequence of instructions setting A to this byte (modulo
    #  256), keeping one state per value of A and D at each depth
    r, cells, state = "", {}, (0, 0, {})
    for b in text.encode("utf-8"):
        layer, found = {state[:2]: (state, "")}, (state, "") if state[0] % 256 == b else None
        while found is None:
            c, new = len(r) + len(next(iter(layer.values()))[1]), {}
            for st, path in layer.values():
                for i in "opj*":
                    if (st2 := _step(st, i, c, cells)) is not None and st2[:2] not in new:
                        new[st2[:2]] = (st2, path + i)
                        # stop as soon as A holds the byte
                        if st2[0] % 256 == b:
                            found = new[st2[:2]]
                            break
                if found:
                    break
            layer = new
        state, path = found
        for i in path + "<":
            r += chr(_value(len(r), i))
        a, d, new = _step(state, "<", len(r) - 1, cells)
        cells.update(new)
        state = (a, d, {})
    # the program has at least two instructions
    r = r or chr(_value(0, "o"))
    if len(r) >= SIZE:
        raise MalbolgeEncodeError("'malbolge' codec can't encode: the text is too long")
    return (r := r + chr(_value(len(r), "v"))), len(text)


def malbolge_decode(text, errors="strict"):
    _h, program = handle_error("malbolge", errors, decode=True, kind="instruction"), []
    for k, c in enumerate(ensure_str(text)):
        if c.isspace():
            continue
        if not 33 <= ord(c) <= 126 or XLAT1[(ord(c) - 33 + len(program)) % 94] not in "ji*p</vo":
            # with a non-strict errors handling, invalid characters are skipped
            _h(c, k)
            continue
        program.append(ord(c))
    if len(program) < 2:
        raise MalbolgeDecodeError("'malbolge' codec can't decode: the program must have at least two instructions")
    if len(program) > SIZE:
        raise MalbolgeDecodeError("'malbolge' codec can't decode: the program is too long")
    return (r := ensure_str(malbolge_run(program))), len(r)


add("malbolge", malbolge_encode, malbolge_decode, r"^(?:malbolge|mb)$", printables_rate=1.,
    expansion_factor=(8., .1))
