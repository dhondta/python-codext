# -*- coding: UTF-8 -*-
"""LOLCODE Codec - LOLCODE content encoding.

LOLCODE is an esoteric programming language created by Adam Lindsay in 2007, whose keywords are inspired by the
 "lolcat" Internet meme. A program starts with "HAI" and ends with "KTHXBYE", and works on dynamically typed variables
 ("I HAS A <var> ITZ <value>", "<var> R <value>") holding untyped values (NOOB), booleans (TROOF: WIN or FAIL), integers
 (NUMBR), floats (NUMBAR) or strings (YARN, with escapes such as ":)" for a newline). It has prefix operators ("SUM OF
 <x> AN <y>", "BOTH SAEM <x> AN <y>", "SMOOSH <x> AN <y> MKAY", ...), conditionals ("O RLY?" and "WTF?", on the value of
 the last expression in IT), loops ("IM IN YR <label> ... IM OUTTA YR <label>"), functions ("HOW IZ I <name> ... IF U
 SAY SO") and prints its arguments with "VISIBLE" (with a newline, unless ended with "!"). Encoding generates an ASCII
 program that prints the text, one "VISIBLE" per line, while decoding runs the program and returns its output. The
 "-lower" variant writes the keywords in lowercase and also reads lowercase keywords (and comments), which then cannot
 be used as identifiers (e.g. "i" or "a").

The program is run according to the 1.2 specification, with the behavior of the reference interpreter (lci) where the
 specification says nothing: escapes not defined in the specification are left as is (except ":3" for a carriage
 return), a division or a modulo by zero is an error, a function returns the value of IT when it does not use "FOUND
 YR" and a "GTFO" in the main program ends it. Unlike lci, WIN and FAIL are printed as such, and the version after "HAI"
 is optional. Features of LOLCODE 1.3 (e.g. BUKKIT arrays) are not supported. No input is available ("GIMMEH" gives an
 empty YARN) and "CAN HAS <library>?" is ignored. Syntax and runtime errors are reported whatever the errors handling.
 A program that does not halt within 1000 steps per token (with a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/justinmeza/lolcode-spec/blob/master/v1.2/lolcode-spec-v1.2.md
           https://github.com/justinmeza/lci
"""
import math
import unicodedata

from ._brainfuck import MIN_STEPS, STEPS_PER_COMMAND
from ..__common__ import *


__examples__ = {
    'enc(lolcode|lol)': {'': "HAI 1.2\nKTHXBYE", 'Hello, World!': "HAI 1.2\nVISIBLE \"Hello, World!\"!\nKTHXBYE",
                         'a:\n"b"\t\n': "HAI 1.2\nVISIBLE \"a::\"\nVISIBLE \":\"b:\":>\"\nKTHXBYE",
                         'caf\xe9 \u20ac\r': "HAI 1.2\nVISIBLE \"caf:(E9) :(20AC):(D)\"!\nKTHXBYE"},
    'enc(lolcode-lower|lol_lowercase)': {'': "hai 1.2\nkthxbye",
                                         'Hello\nWorld!': "hai 1.2\nvisible \"Hello\"\nvisible \"World!\"!\nkthxbye",
                                         'caf\xe9\r': "hai 1.2\nvisible \"caf:(e9):(d)\"!\nkthxbye"},
    'dec(lolcode-lower)': {
        'hai 1.2\nbtw comment\nobtw\nmulti-line comment\ntldr\nim in yr loop uppin yr n til both saem n an 3\n'
        '  visible "KTHX " sum of n an 1\nim outta yr loop\nKTHXBYE':                  "KTHX 1\nKTHX 2\nKTHX 3\n",
        'HAI 1.2\nI HAS A x ITZ WIN\nVISIBLE x!\nKTHXBYE':                               "WIN",
        'hai 1.2\ni has a i itz 1\nkthxbye':                                           None,
    },
    'dec(lolcode)': {'hai 1.2\nvisible "a"\nkthxbye': None},
    'dec(lolcode)': {
        # escapes, interpolation and comments
        'HAI 1.2\nCAN HAS STDIO?\nVISIBLE "HAI WORLD!"\nKTHXBYE':                      "HAI WORLD!\n",
        'HAI\nVISIBLE "a:)b:>c:od:"e::f:(41):[LATIN SMALL LETTER E WITH ACUTE]:3:x"!\nKTHXBYE':
            "a\nb\tc\x07d\"e:fA\xe9\r:x",
        'HAI 1.2\nI HAS A x ITZ "cat", BTW comment\nVISIBLE "my :{x}" AN 1 1.5!\nKTHXBYE':  "my cat11.50",
        'HAI 1.2\nOBTW\nmulti-line\ncomment TLDR\nVISIBLE ...\n "a" "b"\nKTHXBYE':        "ab\n",
        # types, casts and arithmetic
        'HAI 1.2\nVISIBLE SUM OF 2 AN 3 " " QUOSHUNT OF 7 AN -2 " " MOD OF -7 AN 2 " " QUOSHUNT OF 1.0 AN 3!\n'
        'KTHXBYE':                                                                      "5 -3 -1 0.33",
        'HAI 1.2\nVISIBLE PRODUKT OF "3" AN "1.5" " " BIGGR OF 2 AN 3.0 " " SMALLR OF WIN AN 2 " " DIFF OF 1 AN 2!'
        '\nKTHXBYE':                                                                    "4.50 3.00 1 -1",
        'HAI 1.2\nVISIBLE MOD OF 7.5 AN 2 " " MAEK 3.99 A NUMBR " " MAEK "2" NUMBAR " " MAEK 0 TROOF " " MAEK NOOB '
        'YARN "|"!\nKTHXBYE':                                                           "1.50 3 2.00 FAIL |",
        'HAI 1.2\nI HAS A x ITZ "12", x IS NOW A NUMBR, VISIBLE SUM OF x AN 1\nI HAS A y ITZ A NUMBAR\nVISIBLE y '
        'MAEK "-2.5" NUMBR MAEK WIN NUMBR MAEK 1 YARN MAEK 2.0 NUMBR\nKTHXBYE':          "13\n0.00-2112\n",
        # booleans and comparisons
        'HAI 1.2\nVISIBLE BOTH OF WIN AN 0 EITHER OF FAIL AN "x" WON OF WIN AN WIN NOT ""!\nKTHXBYE':
            "FAILWINFAILWIN",
        'HAI 1.2\nVISIBLE ALL OF WIN AN 1 AN "a" MKAY ANY OF 0 0.0 FAIL MKAY ALL OF WIN AN 0 MKAY ANY OF 1 MKAY!'
        '\nKTHXBYE':                                                                    "WINFAILFAILWIN",
        'HAI 1.2\nVISIBLE BOTH SAEM 3 AN 3.0 BOTH SAEM "3" AN 3 DIFFRINT "a" AN "b" BOTH SAEM NOOB AN NOOB '
        'BOTH SAEM WIN AN FAIL!\nKTHXBYE':                                              "WINFAILWINWINFAIL",
        'HAI 1.2\nVISIBLE SMOOSH "a" AN SMOOSH 1 2 MKAY "b" MKAY "c" SMOOSH "d" 3.25\nKTHXBYE':
            "a12bcd3.25\n",
        # conditionals
        'HAI 1.2\nI HAS A x ITZ 2\nBOTH SAEM x AN 1, O RLY?\n YA RLY, VISIBLE "one"\n MEBBE BOTH SAEM x AN 2\n'
        '  VISIBLE "two"\n NO WAI\n  VISIBLE "other"\nOIC\nKTHXBYE':                    "two\n",
        'HAI 1.2\n"", O RLY?\nYA RLY\nVISIBLE "yes"\nMEBBE 0\nVISIBLE "no"\nNO WAI\nVISIBLE "else"\nOIC\nWIN\n'
        'O RLY?\nYA RLY\nVISIBLE "win"\nOIC\nKTHXBYE':                                  "else\nwin\n",
        'HAI 1.2\nI HAS A c ITZ "Y"\nc, WTF?\nOMG "R"\nVISIBLE "red"\nGTFO\nOMG "Y"\nVISIBLE "yellow"\nOMG "G"\n'
        'VISIBLE "flavor"\nGTFO\nOMGWTF\nVISIBLE "none"\nOIC\n7, WTF?\nOMG 1\nVISIBLE 1\nOMGWTF\nVISIBLE "x"\nOIC'
        '\nKTHXBYE':                                                                    "yellow\nflavor\nx\n",
        'HAI 1.2\n1.5, WTF?\nOMG 1\nOMG WIN\nOMG 1.5\nVISIBLE "f"\nOIC\nKTHXBYE':        "f\n",
        # loops and functions
        'HAI 1.2\nIM IN YR l UPPIN YR i TIL BOTH SAEM i AN 3\nVISIBLE i!\nIM OUTTA YR l\nIM IN YR l NERFIN YR i '
        'WILE DIFFRINT i AN -2\nVISIBLE i!\nIM OUTTA YR l\nKTHXBYE':                    "0120-1",
        'HAI 1.2\nI HAS A n ITZ 0\nIM IN YR loop\nn R SUM OF n AN 1\nBOTH SAEM n AN 4, O RLY?\nYA RLY, GTFO\nOIC\n'
        'IM OUTTA YR loop\nVISIBLE n\nKTHXBYE':                                         "4\n",
        'HAI 1.2\nHOW IZ I fact YR n\nBOTH SAEM n AN 0, O RLY?\nYA RLY, FOUND YR 1\nOIC\nFOUND YR PRODUKT OF n AN '
        'I IZ fact YR DIFF OF n AN 1 MKAY\nIF U SAY SO\nVISIBLE I IZ fact YR 10 MKAY\nKTHXBYE':  "3628800\n",
        'HAI 1.2\nHOW IZ I nxt YR x\nSUM OF PRODUKT OF x AN 2 AN 1\nIF U SAY SO\nHOW IZ I add YR a AN YR b\n'
        'SUM OF a AN b\nGTFO\nIF U SAY SO\nHOW IZ I nop\nIF U SAY SO\nIM IN YR l nxt YR i TIL BOTH SAEM i AN 15\n'
        'VISIBLE i!\nIM OUTTA YR l\nVISIBLE MAEK I IZ add YR 1 AN YR 2 MKAY YARN MAEK I IZ nop A YARN\nKTHXBYE':
            "0137\n",
        'HAI 1.2\nVISIBLE "a"\nGTFO\nVISIBLE "b"\nKTHXBYE':                               "a\n",
        'HAI 1.2\nI HAS A x\nGIMMEH x\nVISIBLE "[" x "]" IT "|"!\nKTHXBYE':               None,
        'HAI 1.2\nI HAS A x\nGIMMEH x\nVISIBLE "[" x "]"!\nKTHXBYE':                      "[]",
        # errors
        'VISIBLE "a"':                                                                  None,
        'HAI 1.2\nVISIBLE "a\nKTHXBYE':                                                None,
        'HAI 1.2\nVISIBLE x\nKTHXBYE':                                                 None,
        'HAI 1.2\nVISIBLE QUOSHUNT OF 1 AN 0\nKTHXBYE':                                None,
        'HAI 1.2\nVISIBLE SUM OF "a" AN 1\nKTHXBYE':                                   None,
        'HAI 1.2\nIM IN YR l\nIM OUTTA YR m\nKTHXBYE':                                 None,
        'HAI 1.2\nIM IN YR l\nIM OUTTA YR l\nKTHXBYE':                                 None,
    },
    'enc-dec(lolcode|lolcode-lower)': ["", "Hello World!", "@random{256}", "Caf\xe9, \xf1and\xfa & 10\u20ac",
                                       "\x00a\x00\n", "line 1\nline 2\n\n", ':"quoted":', "not an escape: :(E9)"],
}
__guess__ = ["lolcode", "lolcode-lower"]


TYPES = {'NOOB': None, 'TROOF': False, 'NUMBR': 0, 'NUMBAR': 0., 'YARN': ""}
ESCAPES = {')': "\n", '>': "\t", 'o': "\a", '"': "\"", ':': ":", '3': "\r"}
BINARY = {('SUM', 'OF'): "+", ('DIFF', 'OF'): "-", ('PRODUKT', 'OF'): "*", ('QUOSHUNT', 'OF'): "/",
          ('MOD', 'OF'): "%", ('BIGGR', 'OF'): "max", ('SMALLR', 'OF'): "min", ('BOTH', 'OF'): "and",
          ('EITHER', 'OF'): "or", ('WON', 'OF'): "xor", ('BOTH', 'SAEM'): "==", ('DIFFRINT',): "!="}
VARIADIC = {('ALL', 'OF'): "all", ('ANY', 'OF'): "any", ('SMOOSH',): "smoosh"}
RESERVED = {"A", "ALL", "AN", "ANY", "BIGGR", "BOTH", "BTW", "CAN", "DIFF", "DIFFRINT", "EITHER", "FAIL", "FOUND",
            "GIMMEH", "GTFO", "HAI", "HOW", "I", "IF", "IM", "INVISIBLE", "IS", "IT", "ITZ", "KTHXBYE", "MAEK",
            "MEBBE", "MKAY", "MOD", "NERFIN", "NO", "NOT", "O", "OBTW", "OIC", "OMG", "OMGWTF", "PRODUKT", "QUOSHUNT",
            "R", "SMALLR", "SMOOSH", "SUM", "TIL", "TLDR", "UPPIN", "VISIBLE", "WILE", "WIN", "WON", "WTF", "YA",
            "YR"} | set(TYPES)
# words of the keywords, read in uppercase in lowercase programs
KEYWORDS = RESERVED | {"HAS", "IN", "IZ", "NOW", "OF", "OUTTA", "RLY", "SAEM", "SAY", "SO", "U", "WAI"}
MAX_DEPTH = 100
_NUMBER = re.compile(r"-?(?:[0-9]+(\.[0-9]*)?|(\.)[0-9]+)")
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


class _Break(Exception):
    pass


class _Return(Exception):
    def __init__(self, value):
        self.value = value


def _err(msg, line=None):
    raise LolcodeDecodeError(f"'lolcode' codec can't decode: {msg}" + ["", f" (line {line})"][line is not None])


def _lex(program, lower=False):
    """ Split a program into tokens, as (kind, value, line) with kind being "w" (word), "s" (string literal), "n"
         (newline, also for a comma) or "e" (end of program), keywords being also read in lowercase if lower=True. """
    tokens, i, line, n, flags = [], 0, 1, len(program), re.I if lower else 0
    is_kw = lambda w, j: re.match(w, program[j:], flags)
    stops = lambda j: j >= n or program[j].isspace() or program[j] in ",!?\u2026" or program.startswith("...", j)
    while i < n:
        c = program[i]
        if c in ",\r\n":
            tokens.append(("n", "\n", line))
            line += c != ","
            i += 1 + (program.startswith("\r\n", i))
        elif c in "!?":
            tokens.append(("w", c, line))
            i += 1
        elif c.isspace():
            i += 1
        elif (m := re.match(r"(?:\.\.\.|\u2026)[ \t]*(\r\n|\r|\n)", program[i:])):
            # line continuation, the next line not being empty
            i, line = i + m.end(), line + 1
            if re.match(r"[ \t]*(?:[\r\n]|$)", program[i:]):
                _err("line continuation followed by an empty line", line)
        elif is_kw("OBTW", i) and (not tokens or tokens[-1][0] == "n"):
            if not (m := re.compile("TLDR", flags).search(program, i)):
                _err("unterminated multi-line comment", line)
            j = m.start()
            line += len(re.findall(r"\r\n|\r|\n", program[i:j]))
            i = j + 4
            if not re.match(r"[ \t]*(?:[,\r\n]|$)", program[i:]):
                _err("multi-line comment not followed by a newline", line)
        elif is_kw("BTW", i):
            while i < n and program[i] not in "\r\n":
                i += 1
        elif c == '"':
            j = i + 1
            while j < n and program[j] != '"':
                if program[j] in "\r\n":
                    break
                j += 1 + (program[j] == ":" and j + 1 < n and program[j+1] not in "\r\n")
            if j >= n or program[j] != '"':
                _err("unterminated string", line)
            if not stops(j + 1):
                _err("expected token delimiter after string", line)
            tokens.append(("s", program[i+1:j], line))
            i = j + 1
        else:
            # a word (with at least one character, e.g. for an ellipsis not ending a line)
            j = i + 1
            while not stops(j):
                j += 1
            w = program[i:j]
            tokens.append(("w", w.upper() if lower and w.isascii() and w.upper() in KEYWORDS else w, line))
            i = j
    return tokens + [("e", "", line)]


class _Parser:
    """ Recursive-descent parser of LOLCODE 1.2, making an abstract syntax tree of tuples. """
    def __init__(self, tokens):
        self.tokens, self.pos = tokens, 0

    def peek(self, *words):
        """ Check whether the next tokens are the given words. """
        t = self.tokens[self.pos:self.pos+len(words)]
        return len(t) == len(words) and all(k == "w" and v == w for (k, v, _), w in zip(t, words))

    def accept(self, *words):
        if (r := self.peek(*words)):
            self.pos += len(words)
        return r

    def expect(self, *words):
        if not self.accept(*words):
            self.fail(f"expected '{' '.join(words)}'")

    def fail(self, msg):
        k, v, line = self.tokens[self.pos]
        _err(f"{msg}, got {({'e': 'end of program', 'n': 'newline'}).get(k, repr(v))}", line)

    @property
    def at_end(self):
        """ Whether the next token ends an expression list (newline, end of program or "!"). """
        return self.tokens[self.pos][0] in "ne" or self.peek("!")

    def newline(self):
        if self.tokens[self.pos][0] != "n":
            self.fail("expected newline")
        while self.tokens[self.pos][0] == "n":
            self.pos += 1

    def identifier(self):
        k, v, _ = self.tokens[self.pos]
        if k != "w" or v in RESERVED or not _IDENTIFIER.fullmatch(v):
            self.fail("expected identifier")
        self.pos += 1
        return v

    def type(self):
        k, v, _ = self.tokens[self.pos]
        if k != "w" or v not in TYPES:
            self.fail("expected type")
        self.pos += 1
        return v

    def program(self):
        while self.tokens[self.pos][0] == "n":
            self.pos += 1
        self.expect("HAI")
        if not self.at_end:
            self.pos += 1  # version
        self.newline()
        body = self.block(("KTHXBYE", ))
        self.expect("KTHXBYE")
        while self.tokens[self.pos][0] == "n":
            self.pos += 1
        if self.tokens[self.pos][0] != "e":
            self.fail("expected end of program")
        return body

    def block(self, *ends):
        """ Parse statements until one of the given keywords (as tuples of words). """
        stmts = []
        while not any(self.peek(*e) for e in ends):
            if self.tokens[self.pos][0] == "e":
                self.fail(f"expected '{' '.join(ends[0])}'")
            stmts.append(self.statement())
            self.newline()
        return stmts

    def statement(self):
        line = self.tokens[self.pos][2]
        if self.accept("I", "HAS", "A") or self.accept("I", "HAS", "AN"):
            name, value = self.identifier(), ("lit", None)
            if self.accept("ITZ"):
                value = ("lit", TYPES[self.type()]) if self.accept("A") else self.expression()
            return line, "decl", name, value
        if self.peek("VISIBLE") or self.peek("INVISIBLE"):
            visible, args = self.tokens[self.pos][1] == "VISIBLE", []
            self.pos += 1
            while not self.at_end:
                # as with the reference interpreter, arguments may be separated by "AN"
                args.append(self.expression())
                self.accept("AN")
            if not args:
                self.fail("expected expression")
            return line, "visible", args, not self.accept("!"), visible
        if self.accept("GIMMEH"):
            return line, "gimmeh", self.identifier()
        if self.accept("O", "RLY", "?"):
            self.newline()
            self.expect("YA", "RLY")
            self.newline()
            ends = [("MEBBE", ), ("NO", "WAI"), ("OIC", )]
            yes, guards, no = self.block(*ends), [], []
            while self.accept("MEBBE"):
                guard = self.expression()
                self.newline()
                guards.append((guard, self.block(*ends)))
            if self.accept("NO", "WAI"):
                self.newline()
                no = self.block(("OIC", ))
            self.expect("OIC")
            return line, "if", yes, guards, no
        if self.accept("WTF", "?"):
            self.newline()
            cases, default, ends = [], None, [("OMG", ), ("OMGWTF", ), ("OIC", )]
            while self.accept("OMG"):
                k, v, _ = self.tokens[self.pos]
                if k == "s" and ":{" not in v:
                    value = _string(self.expression()[1], {}, line)
                elif self.peek("WIN") or self.peek("FAIL") or k == "w" and _NUMBER.fullmatch(v):
                    value = self.expression()[1]
                else:
                    self.fail("expected literal")
                if any(type(value) is type(v) and value == v for v, _ in cases):
                    _err(f"duplicate case {value!r}", self.tokens[self.pos][2])
                self.newline()
                cases.append((value, self.block(*ends)))
            if self.accept("OMGWTF"):
                self.newline()
                default = self.block(("OIC", ))
            self.expect("OIC")
            return line, "switch", cases, default
        if self.accept("GTFO"):
            return line, "gtfo"
        if self.accept("IM", "IN", "YR"):
            label, op, var, cond = self.identifier(), None, None, None
            if not self.at_end:
                # the operation is UPPIN, NERFIN or a unary function, also written as with the reference interpreter
                #  ("I IZ <function> YR <variable> MKAY")
                call = self.accept("I", "IZ")
                op = "UPPIN" if self.accept("UPPIN") else "NERFIN" if self.accept("NERFIN") else self.identifier()
                self.expect("YR")
                var = self.identifier()
                if call and op not in ("UPPIN", "NERFIN"):
                    self.expect("MKAY")
                for kw in ["TIL", "WILE"]:
                    if self.accept(kw):
                        cond = (kw, self.expression())
            self.newline()
            body = self.block(("IM", "OUTTA", "YR"))
            self.expect("IM", "OUTTA", "YR")
            if self.identifier() != label:
                _err(f"loop '{label}' closed with another label", self.tokens[self.pos-1][2])
            return line, "loop", op, var, cond, body
        if self.accept("HOW", "IZ", "I"):
            name, args = self.identifier(), []
            if self.accept("YR"):
                args.append(self.identifier())
                while self.accept("AN", "YR"):
                    args.append(self.identifier())
            self.newline()
            body = self.block(("IF", "U", "SAY", "SO"))
            self.expect("IF", "U", "SAY", "SO")
            return line, "func", name, args, body
        if self.accept("FOUND", "YR"):
            return line, "found", self.expression()
        if self.accept("CAN", "HAS"):
            self.pos += self.tokens[self.pos][0] == "w"
            self.expect("?")
            return line, "nop"
        k, v, _ = self.tokens[self.pos]
        if k == "w" and v not in RESERVED and _IDENTIFIER.fullmatch(v):
            if self.tokens[self.pos+1][:2] == ("w", "R"):
                self.pos += 2
                return line, "assign", v, self.expression()
            self.pos += 1
            if self.accept("IS", "NOW", "A"):
                return line, "assign", v, ("maek", ("var", v, line), self.type())
            self.pos -= 1
        return line, "expr", self.expression()

    def expression(self):
        k, v, line = self.tokens[self.pos]
        if k == "s":
            self.pos += 1
            return ("str", v, line)
        for kws, op in BINARY.items():
            if self.accept(*kws):
                a = self.expression()
                self.accept("AN")
                return ("bin", op, a, self.expression(), line)
        for kws, op in VARIADIC.items():
            if self.accept(*kws):
                args = [self.expression()]
                while not self.at_end and not self.accept("MKAY"):
                    self.accept("AN")
                    args.append(self.expression())
                return ("var_op", op, args, line)
        if self.accept("NOT"):
            return ("not", self.expression())
        if self.accept("MAEK"):
            e = self.expression()
            self.accept("A")
            return ("maek", e, self.type())
        if self.accept("I", "IZ"):
            name, args = self.identifier(), []
            if self.accept("YR"):
                args.append(self.expression())
                while self.accept("AN", "YR"):
                    args.append(self.expression())
            self.accept("MKAY")
            return ("call", name, args, line)
        if k == "w":
            if (m := _NUMBER.fullmatch(v)):
                self.pos += 1
                return ("lit", float(v) if m.group(1) is not None or m.group(2) else int(v))
            if v in ("WIN", "FAIL", "NOOB"):
                self.pos += 1
                return ("lit", {'WIN': True, 'FAIL': False}.get(v))
            if self.accept("IT"):
                return ("it", )
            return ("var", self.identifier(), line)
        self.fail("expected expression")


def _type(v):
    return "NOOB" if v is None else "TROOF" if isinstance(v, bool) else "NUMBR" if isinstance(v, int) else \
           "NUMBAR" if isinstance(v, float) else "YARN"


def _troof(v):
    return v != "" if isinstance(v, str) else bool(v)


def _number(v, line, implicit=True):
    """ Cast a value to a number (NUMBR, or NUMBAR for a float or a YARN with a decimal point). """
    if v is None:
        if implicit:
            _err("cannot implicitly cast NOOB", line)
        return 0
    if isinstance(v, str):
        if not (m := _NUMBER.fullmatch(v)):
            _err(f"cannot cast {v!r} to a number", line)
        return float(v) if m.group(1) is not None or m.group(2) else int(v)
    return int(v) if isinstance(v, bool) else v


def _yarn(v, line, implicit=True):
    if v is None:
        if implicit:
            _err("cannot implicitly cast NOOB", line)
        return ""
    if isinstance(v, bool):
        return ["FAIL", "WIN"][v]
    if isinstance(v, float):
        # as in C with "%f", truncated to 2 decimals
        s = f"{v:f}"
        return s[:s.index(".") + 3] if "." in s else s
    return str(v)


def _arith(op, a, b, line):
    a, b = _number(a, line), _number(b, line)
    if op in "/%" and b == 0:
        _err("division by zero", line)
    if isinstance(a, float) or isinstance(b, float):
        a, b = float(a), float(b)
        return {'+': a + b, '-': a - b, '*': a * b, '/': a / b if b else 0., '%': math.fmod(a, b) if b else 0.,
                'max': max(a, b), 'min': min(a, b)}[op]
    if op in "/%":
        # truncated toward zero, as in C
        q = abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)
        return q if op == "/" else a - b * q
    return {'+': a + b, '-': a - b, '*': a * b, 'max': max(a, b), 'min': min(a, b)}[op]


def _equal(a, b):
    ta, tb = _type(a), _type(b)
    if ta != tb:
        return ta in ("NUMBR", "NUMBAR") and tb in ("NUMBR", "NUMBAR") and float(a) == float(b)
    return a == b


def _cast(v, t, line):
    if t == "NOOB":
        return None
    if t == "TROOF":
        return _troof(v)
    if t == "YARN":
        return _yarn(v, line, False)
    v = _number(v, line, False)
    return float(v) if t == "NUMBAR" else int(v)


def _string(raw, frame, line):
    """ Resolve the escapes and the interpolations of a string literal. """
    r, i = "", 0
    while i < len(raw):
        c = raw[i]
        if c == ":" and i + 1 < len(raw):
            e = raw[i+1]
            if e in ESCAPES:
                r, i = r + ESCAPES[e], i + 2
                continue
            if e in "({[":
                if (j := raw.find(")}]"["({[".index(e)], i + 2)) < 0:
                    _err(f"unterminated escape in string {raw!r}", line)
                s = raw[i+2:j]
                if e == "(":
                    if not re.fullmatch(r"[0-9a-fA-F]+", s) or int(s, 16) > 0x10ffff:
                        _err(f"invalid code point '{s}'", line)
                    r += chr(int(s, 16))
                elif e == "[":
                    try:
                        r += unicodedata.lookup(s)
                    except KeyError:
                        _err(f"unknown character name '{s}'", line)
                else:
                    if s not in frame:
                        _err(f"unknown variable '{s}'", line)
                    r += _yarn(frame[s], line)
                i = j + 1
                continue
        r, i = r + c, i + 1
    return r


class _Interpreter:
    def __init__(self, max_steps):
        self.out, self.funcs, self.steps, self.max_steps, self.depth = [], {}, 0, max_steps, 0

    def eval(self, e, frame):
        kind = e[0]
        if kind == "lit":
            return e[1]
        if kind == "str":
            return _string(e[1], frame, e[2])
        if kind == "it":
            return frame["IT"]
        if kind == "var":
            if e[1] not in frame:
                _err(f"unknown variable '{e[1]}'", e[2])
            return frame[e[1]]
        if kind == "bin":
            op, line = e[1], e[4]
            if op in ("and", "or"):
                # short-circuit evaluation, as with the reference interpreter
                a = _troof(self.eval(e[2], frame))
                return a if a == (op == "or") else _troof(self.eval(e[3], frame))
            a, b = self.eval(e[2], frame), self.eval(e[3], frame)
            if op == "xor":
                return _troof(a) != _troof(b)
            if op in ("==", "!="):
                return _equal(a, b) == (op == "==")
            return _arith(op, a, b, line)
        if kind == "var_op":
            if e[1] == "smoosh":
                return "".join(_yarn(self.eval(a, frame), e[3]) for a in e[2])
            for a in e[2]:
                if _troof(self.eval(a, frame)) == (e[1] == "any"):
                    return e[1] == "any"
            return e[1] == "all"
        if kind == "not":
            return not _troof(self.eval(e[1], frame))
        if kind == "maek":
            return _cast(self.eval(e[1], frame), e[2], None)
        # function call
        _, name, args, line = e
        if name not in self.funcs:
            _err(f"unknown function '{name}'", line)
        params, body = self.funcs[name]
        if len(args) != len(params):
            _err(f"function '{name}' expects {len(params)} argument(s)", line)
        if self.depth >= MAX_DEPTH:
            _err("recursion too deep", line)
        new = {'IT': None, **{p: self.eval(a, frame) for p, a in zip(params, args)}}
        self.depth += 1
        try:
            self.run(body, new)
        except _Return as r:
            return r.value
        except _Break:
            return None
        finally:
            self.depth -= 1
        return new["IT"]

    def step(self, line):
        self.steps += 1
        if self.steps > self.max_steps:
            _err(f"program did not halt within {self.max_steps} steps", line)

    def run(self, stmts, frame):
        for s in stmts:
            line, kind = s[:2]
            self.step(line)
            if kind == "decl":
                frame[s[2]] = self.eval(s[3], frame)
            elif kind == "assign":
                if s[2] not in frame:
                    _err(f"unknown variable '{s[2]}'", line)
                frame[s[2]] = self.eval(s[3], frame)
            elif kind == "visible":
                r = "".join(_yarn(self.eval(a, frame), line) for a in s[2]) + "\n" * s[3]
                if s[4]:
                    self.out.append(r)
            elif kind == "gimmeh":
                # no input is available
                frame[s[2]] = ""
            elif kind == "expr":
                frame["IT"] = self.eval(s[2], frame)
            elif kind == "if":
                if _troof(frame["IT"]):
                    self.run(s[2], frame)
                else:
                    for guard, block in s[3]:
                        if _troof(self.eval(guard, frame)):
                            self.run(block, frame)
                            break
                    else:
                        self.run(s[4], frame)
            elif kind == "switch":
                it, cases = frame["IT"], s[2]
                k = next((i for i, (v, _) in enumerate(cases) if type(v) is type(it) and v == it), None)
                try:
                    if k is None:
                        self.run(s[3] or [], frame)
                    else:
                        for _, block in cases[k:]:
                            self.run(block, frame)
                except _Break:
                    pass
            elif kind == "gtfo":
                raise _Break()
            elif kind == "loop":
                _, _, op, var, cond, body = s
                # the loop variable is temporary, starting from 0
                saved = frame.get(var, KeyError) if var else None
                if var:
                    frame[var] = 0
                try:
                    while True:
                        self.step(line)
                        if cond and _troof(self.eval(cond[1], frame)) == (cond[0] == "TIL"):
                            break
                        self.run(body, frame)
                        if op in ("UPPIN", "NERFIN"):
                            frame[var] = _arith("+-"[op == "NERFIN"], frame[var], 1, line)
                        elif op:
                            frame[var] = self.eval(("call", op, [("var", var, line)], line), frame)
                except _Break:
                    pass
                finally:
                    if var:
                        if saved is KeyError:
                            frame.pop(var, None)
                        else:
                            frame[var] = saved
            elif kind == "func":
                self.funcs[s[2]] = (s[3], s[4])
            elif kind == "found":
                raise _Return(self.eval(s[2], frame))


def lolcode_run(program, max_steps=None, lower=False):
    """ Run a LOLCODE program and return its output.

    :param program:   program as a string
    :param lower:     whether keywords may also be written in lowercase
    :param max_steps: maximum number of executed statements, for stopping programs that do not halt (by default, 1000
                       per token, with a minimum of 1 million)
    """
    try:
        tokens = _lex(program.removeprefix("\ufeff"), lower)
        body = _Parser(tokens).program()
        interpreter = _Interpreter(max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * len(tokens)))
        try:
            interpreter.run(body, {'IT': None})
        except (_Break, _Return):
            # "GTFO" or "FOUND YR" in the main program ends it
            pass
    except RecursionError:
        _err("program too deeply nested")
    return "".join(interpreter.out)


def _escape(c):
    if c in ESCAPES.values() and c != "\r":
        return ":" + next(k for k, v in ESCAPES.items() if v == c)
    return c if " " <= c <= "~" else f":({ord(c):X})"


def lolcode_encode(lower=""):
    def encode(text, errors="strict"):
        lines, esc = ensure_str(text).split("\n"), lambda l: "".join(map(_escape, l))
        stmts = [f'VISIBLE "{esc(l)}"' for l in lines[:-1]] + ([f'VISIBLE "{esc(lines[-1])}"!'] if lines[-1] else [])
        r = "\n".join(["HAI 1.2"] + stmts + ["KTHXBYE"])
        if lower:
            # lowercase keywords and hexadecimal escapes, the text being left unchanged
            r = re.sub(r'^\w+|::|:\([0-9A-F]+\)', lambda m: m.group().lower(), r, flags=re.M)
        return r, len(text)
    return encode


def lolcode_decode(lower=""):
    def decode(text, errors="strict"):
        return (r := lolcode_run(ensure_str(text), lower=bool(lower))), len(r)
    return decode


add("lolcode", lolcode_encode, lolcode_decode, r"^lol(?:code)?(?:[-_](lower)(?:case)?)?$", printables_rate=1.,
    expansion_factor=(2., .5))
