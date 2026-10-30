# -*- coding: UTF-8 -*-
"""Church Codec - Church encoding content encoding.

Church encoding, devised by Alonzo Church, represents data in the untyped lambda calculus, whose terms are variables,
 abstractions ("\\x.M" or "λx.M", a function of x) and applications ("M N", M applied to N). The natural number n is the
 numeral "\\f.\\x.f (f ... (f x))", applying f n times to x, and the list [a, b, ...] is its right fold
 "\\c.\\n.c a (c b (... n))". Encoding generates a program that evaluates to the list of the numerals of the bytes of the
 text (as UTF-8), while decoding evaluates the program and returns the bytes of the list it gives.

The program is a single term: abstractions extend as far to the right as possible, applications are left-associative
 and "\\x y.M" stands for "\\x.\\y.M". Variables are made of letters, digits, "_" and "'" (not starting with a digit),
 and must be bound. The program is evaluated lazily in normal order (call-by-need), so that only the list and its
 numerals are reduced, and must give a list of numerals lower than 256. Syntax and evaluation errors are reported
 whatever the errors handling. A program that does not give its list within 1000 steps per token (with a minimum of 1
 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Church_encoding
           https://en.wikipedia.org/wiki/Lambda_calculus
"""
import re

from ._brainfuck import MIN_STEPS, STEPS_PER_COMMAND
from ..__common__ import *


# numerals and arithmetic: SUCC = \n f x.f (n f x), MULT = \m n f.m (n f) ; 8 * 9 = 72 = "H"
_N8, _N9 = r"(\f x.f (f (f (f (f (f (f (f x))))))))", r"(\f x.f (f (f (f (f (f (f (f (f x)))))))))"
__examples__ = {
    'enc(church|church-encoding|lambda-calculus)': {
        '':         r"\c.\n.n",
        '\x00':     r"\c.\n.c (\f.\x.x) n",
        '\x01\x02': r"\c.\n.c (\f.\x.f x) (c (\f.\x.f (f x)) n)",
    },
    'dec(church)': {
        r"\c.\n.n":                                                  "",
        f"λc n.c ((λm n f.m (n f)) {_N8} {_N9}) n":                  "H",
        f"\\c n.c ((\\n f x.f (n f x)) ((\\m n f.m (n f)) {_N8} {_N9})) n": "I",
        # the identity applied to a list, a variable shadowing another one and whitespace
        r"(\x.x) (\c.\n.c (\f.\x.f x) n)":                             "\x01",
        "\\c n.c (\\f.(\\f.\\x.f (f x)) f)\n  n":                     "\x02",
        # a non-terminating argument is never evaluated (normal order)
        r"(\x y.y) ((\x.x x) (\x.x x)) (\c.\n.n)":                   "",
        # syntax errors, unbound variables, results that are not a list of numerals
        "":                                                           None,
        r"\c.\n.":                                                    None,
        r"\c n n":                                                    None,
        r"\c.\n.(n":                                                  None,
        r"\c.\n.n)":                                                  None,
        r"\c n.c 1 n":                                                None,
        r"\c.\n.m":                                                   None,
        r"\c.\n.c n n":                                               None,
        r"\c.\n.c (\f.\x.f) n":                                       None,
        r"\c.\n.c (\f.\x.c) n":                                       None,
        r"\c.\n.c":                                                   None,
        r"\c.c":                                                      None,
    },
    'enc-dec(church)': ["", "Hello World!", "@random{64}", "Caf\xe9, \xf1and\xfa & 10€", "\x00a\x00"],
}
__guess__ = ["church"]


_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")
_TOKEN = re.compile(r"\s+|[λ\\.()]|[A-Za-z_][A-Za-z0-9_']*|.")
# term nodes: (VAR, de Bruijn index), (LAM, body), (APP, function, argument)
VAR, LAM, APP = range(3)


def _err(msg):
    raise ChurchDecodeError(f"'church' codec can't decode: {msg}")


def _numeral(n):
    """ Church numeral of the given natural number. """
    return r"\f.\x." + "f (" * (n - 1) + "f " * (n > 0) + "x" + ")" * (n - 1)


def church_encode(text, errors="strict"):
    data = text.encode("utf-8")
    return (r := r"\c.\n." + "".join(f"c ({_numeral(b)}) (" for b in data[:-1]) + \
                 (f"c ({_numeral(data[-1])}) " if data else "") + "n" + ")" * (len(data) - 1)), len(text)


def church_parse(program):
    """ Parse a lambda term into nested tuples, variables being replaced by their de Bruijn index. Parsing does not
         recurse, as the generated programs nest as deep as their text is long. """
    tokens = [t for t in _TOKEN.findall(program) if not t.isspace()]
    # each group (the whole program or a parenthesis) holds the pending abstractions, as pairs of the application
    #  before them and of their number of variables, and its current application
    groups, scope, positions, i = [[[], None]], [], {}, 0

    def _close():
        pending, term = groups.pop()
        if term is None:
            _err("empty term")
        for app, n in reversed(pending):
            for _ in range(n):
                term = (LAM, term)
                positions[scope.pop()].pop()
            term = term if app is None else (APP, app, term)
        return term

    def _add(term):
        g = groups[-1]
        g[1] = term if g[1] is None else (APP, g[1], term)

    while i < len(tokens):
        t = tokens[i]
        if t in "λ\\":
            n = 0
            while (i := i + 1) < len(tokens) and _IDENTIFIER.fullmatch(t := tokens[i]):
                scope.append(t)
                positions.setdefault(t, []).append(len(scope) - 1)
                n += 1
            if n == 0 or i == len(tokens) or tokens[i] != ".":
                _err("bad abstraction (expected variables then '.')")
            groups[-1][0].append((groups[-1][1], n))
            groups[-1][1] = None
        elif t == "(":
            groups.append([[], None])
        elif t == ")":
            if len(groups) == 1:
                _err("unmatched ')'")
            _add(_close())
        elif _IDENTIFIER.fullmatch(t):
            if not positions.get(t):
                _err(f"unbound variable '{t}'")
            _add((VAR, len(scope) - 1 - positions[t][-1]))
        else:
            _err(f"invalid character '{t}'")
        i += 1
    if len(groups) > 1:
        _err("unmatched '('")
    return _close()


def church_run(program, max_steps=None):
    """ Evaluate a lambda term giving a Church list of Church numerals and return the bytes of this list.

    :param program:   lambda term, as a string
    :param max_steps: maximum number of steps of the evaluation, for stopping programs that do not give their list (by
                       default, 1000 per token, with a minimum of 1 million)
    """
    term = church_parse(program)
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * len(_TOKEN.findall(program)))
    steps = 0

    # The terms are evaluated by a lazy Krivine machine: an environment is a linked list of thunks [term, environment,
    #  value], a value is either a closure (CLO, abstraction, environment) or a free variable applied to thunks (FREE,
    #  variable, thunks), and the stack holds the thunks of the arguments and the thunks being evaluated (as tuples).
    CLO, FREE = range(2)

    def _whnf(term, env, stack):
        """ Evaluate a term applied to the thunks of the stack (the first argument on top) to weak head normal form. """
        nonlocal steps
        while True:
            if (steps := steps + 1) > max_steps:
                raise ValueError(f"program did not give its list within {max_steps} steps")
            if term[0] == APP:
                stack.append([term[2], env, None])
                term = term[1]
            elif term[0] == LAM:
                if not stack:
                    return (CLO, term, env)
                if isinstance(x := stack.pop(), tuple):
                    x[0][2] = (CLO, term, env)
                else:
                    term, env = term[1], (x, env)
            else:
                for _ in range(term[1]):
                    env = env[1]
                th = env[0]
                if th[2] is None:
                    stack.append((th, ))
                    term, env = th[0], th[1]
                elif th[2][0] == CLO:
                    term, env = th[2][1], th[2][2]
                else:
                    var, args = th[2][1], list(th[2][2])
                    while stack:
                        if isinstance(x := stack.pop(), tuple):
                            x[0][2] = (FREE, var, tuple(args))
                        else:
                            args.append(x)
                    return (FREE, var, tuple(args))

    def _apply(value, *variables):
        """ Apply a value to free variables. """
        args = [[None, None, (FREE, v, ())] for v in variables]
        if value[0] == FREE:
            return (FREE, value[1], value[2] + tuple(args))
        return _whnf(value[1], value[2], args[::-1])

    def _force(th):
        if th[2] is None:
            th[2] = _whnf(th[0], th[1], [])
        return th[2]

    # the list is read by applying it to the free variables c and n, giving either "c head tail" or "n", and each head
    #  by applying it to the free variables f and x, giving "f (f (... x))"
    c, n, f, x, out = "c", "n", "f", "x", bytearray()
    v = _apply(_whnf(term, None, []), c, n)
    while v != (FREE, n, ()):
        if v[0] != FREE or v[1] != c or len(v[2]) != 2:
            _err("the program does not give a list")
        b, w = 0, _apply(_force(v[2][0]), f, x)
        while w != (FREE, x, ()):
            if w[0] != FREE or w[1] != f or len(w[2]) != 1:
                _err("an item of the list is not a numeral")
            if (b := b + 1) > 255:
                _err("an item of the list is greater than 255")
            w = _force(w[2][0])
        out.append(b)
        v = _force(v[2][1])
    return bytes(out)


def church_decode(text, errors="strict"):
    return (r := ensure_str(church_run(ensure_str(text)))), len(r)


add("church", church_encode, church_decode, r"^(?:church(?:[-_]encoding)?|lambda[-_]calculus)$", printables_rate=1.,
    expansion_factor=(400., .004))
