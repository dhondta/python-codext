# -*- coding: UTF-8 -*-
"""JSFuck Codec - JSFuck content encoding.

JSFuck, created by Martin Kleppe, writes JavaScript with only six characters: "[", "]", "(", ")", "!" and "+". It builds
 values from empty arrays (e.g. "+[]" is 0, "![]" is false and "[][[]]" is undefined), takes characters from their
 string representations (e.g. "(![]+[])[+[]]" is "f"), gets methods by name (e.g. "[]["at"]") and the Function
 constructor through their "constructor" property, and calls it to reach other values (e.g. "escape") or to evaluate a
 string literal of escape sequences, for the characters it cannot build otherwise.

Encoding gives an expression whose value is the text, as the reference encoder (version 0.5.0) does, except for two
 cases where the reference encoder gives a wrong expression: the characters taken from the representation of RegExp
 ("E", "R", ":", "?" and "\\", also used for the texts with several characters that cannot be built) and the octal
 escape sequences that would absorb a following digit (padded to three digits). The "-eval" variant gives a program that
 runs the text as JavaScript code. Decoding evaluates the expression with an interpreter of the subset of JavaScript
 that JSFuck relies on (with a fixed date), without running any code: a program that runs some code (e.g. made with the
 "-eval" variant) gives this code. Malformed or unsupported expressions are reported whatever the errors handling.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/aemkei/jsfuck
"""
from decimal import Decimal, ROUND_HALF_UP
from math import floor, inf, isfinite, nan, trunc

from ._javascript import *
from ..ciphers._jsfloat import js_str
from ..__common__ import *


__examples__ = {
    'enc(jsfuck)': {'a': "(![]+[])[+!+[]]", '1': "[+!+[]]+[]", 'false': "(![]+[])"},
    'enc(jsfuck-eval)': {'1': "[][(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+["
                              "]]+(!![]+[][(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+"
                              "[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+!+[]]+(!!"
                              "[]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+!+[]]+(!![]+[])[+[]"
                              "]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]([+!+[]]+[])()"},
    'dec(jsfuck)': {'': "", '+[]': "0", '[]+[]': "", '!![]+[][[]]': "NaN", '!![]+[]+[][[]]': "trueundefined",
                    '+[![]]+[]': "NaN", '[][(![]+[])[+[]]]': "undefined", '[+[]': None, '+[]]': None,
                    '[][[]][[]]': None},
    'enc-dec(jsfuck|jsfuck-eval)': ["", "alert(\"Hello, World!\")", "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                    "abcdefghijklmnopqrstuvwxyz", "~0123456789 abcdefghijklmnopqrstuvwxyz()+.~",
                                    "[(~t~)]", "~\\\"", "caf\xe9 \u20ac \U0001f600", "\x00\x01\n\\\"'", "\x0a2 \x011"],
}


# --------------------------------------------------- Encoding ---------------------------------------------------------
# tables of the reference encoder (jsfuck.js, version 0.5.0)
SIMPLE = {'false': "![]", 'true': "!![]", 'undefined': "[][[]]", 'NaN': "+[![]]",
          'Infinity': "+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]]+[+[]])"}
# unlike the reference encoder, RegExp is replaced first, so that the "Function" it introduces is also replaced
CONSTRUCTORS = {'RegExp': "Function(\"return/\"+false+\"/\")()", 'Array': "[]", 'Number': "(+[])", 'String': "([]+[])",
                'Boolean': "(![])", 'Function': "[][\"at\"]"}
_MAPPING = [
    ('a', "(false+\"\")[1]"), ('b', "([][\"entries\"]()+\"\")[2]"), ('c', "([][\"at\"]+\"\")[3]"),
    ('d', "(undefined+\"\")[2]"), ('e', "(true+\"\")[3]"), ('f', "(false+\"\")[0]"), ('g', "(false+[0]+String)[20]"),
    ('h', "(+(101))[\"to\"+String[\"name\"]](21)[1]"), ('i', "([false]+undefined)[10]"),
    ('j', "([][\"entries\"]()+\"\")[3]"), ('k', "(+(20))[\"to\"+String[\"name\"]](21)"), ('l', "(false+\"\")[2]"),
    ('m', "(Number+\"\")[11]"), ('n', "(undefined+\"\")[1]"), ('o', "(true+[][\"at\"])[10]"),
    ('p', "(+(211))[\"to\"+String[\"name\"]](31)[1]"), ('q', "(\"\")[\"fontcolor\"]([0]+false+\")[20]"),
    ('r', "(true+\"\")[1]"), ('s', "(false+\"\")[3]"), ('t', "(true+\"\")[0]"), ('u', "(undefined+\"\")[0]"),
    ('v', "(+(31))[\"to\"+String[\"name\"]](32)"), ('w', "(+(32))[\"to\"+String[\"name\"]](33)"),
    ('x', "(+(101))[\"to\"+String[\"name\"]](34)[1]"), ('y', "(NaN+[Infinity])[10]"),
    ('z', "(+(35))[\"to\"+String[\"name\"]](36)"), ('A', "(NaN+[][\"entries\"]())[11]"), ('B', "(+[]+Boolean)[10]"),
    ('C', "Function(\"return escape\")()((\"\")[\"italics\"]())[2]"),
    ('D', "Function(\"return escape\")()([][\"at\"])[\"at\"](\"-1\")"), ('E', "(RegExp+\"\")[12]"),
    ('F', "(+[]+Function)[10]"), ('G', "(false+Function(\"return Date\")()())[30]"), ('I', "(Infinity+\"\")[0]"),
    ('M', "(true+Function(\"return Date\")()())[30]"), ('N', "(NaN+\"\")[0]"), ('R', "(+[]+RegExp)[10]"),
    ('S', "(+[]+String)[10]"), ('T', "(NaN+Function(\"return Date\")()())[30]"), (' ', "(NaN+[][\"at\"])[11]"),
    ('"', "(\"\")[\"fontcolor\"]()[12]"), ('%', "Function(\"return escape\")()([][\"at\"])[22]"),
    ('&', "(\"\")[\"fontcolor\"](\")[13]"), ('(', "([][\"at\"]+\"\")[11]"), (')', "(\"\"+[][\"at\"])[12]"),
    ('+', "(+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]])+[])[2]"), (',', "[[]][\"concat\"]([[]])+\"\""),
    ('-', "(+(.+[0000001])+\"\")[2]"),
    ('.', "(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]"),
    ('/', "(false+[0])[\"italics\"]()[10]"), (':', "(RegExp()+\"\")[3]"), (';', "(\"\")[\"fontcolor\"](NaN+\")[21]"),
    ('<', "(\"\")[\"italics\"]()[0]"), ('=', "(\"\")[\"fontcolor\"]()[11]"), ('>', "(\"\")[\"italics\"]()[2]"),
    ('?', "(RegExp()+\"\")[2]"), ('[', "([][\"entries\"]()+\"\")[0]"), ('\\', "(RegExp(\"/\")+\"\")[1]"),
    (']', "([][\"entries\"]()+\"\")[22]"), ('{', "([0]+false+[][\"at\"])[20]"),
    ('}', "([][\"at\"]+\"\")[\"at\"](\"-1\")"),
]
# characters kept as is, all the others being escaped, when several characters cannot be built
KEEP = "0123456789.adefilnrsuN"


def _digit(n):
    out = "+[]"
    if n > 0:
        out = "+!" + out
    for _ in range(1, n):
        out = "+!+[]" + out
    return out[1:] if n > 1 else out


def __mapping():
    """ Build the expressions of the characters as the reference encoder does, replacing the names of the constructors,
         the simple values and the numbers, then the characters of the strings and the other characters, until only the
         six characters of JSFuck remain. """
    # JavaScript enumerates the integer keys first (here, the digits), then the others in their insertion order
    m = {str(n): f"[{_digit(n)}]" for n in range(10)}
    m.update(_MAPPING)
    sub = lambda v, p, r: re.sub(p, r if callable(r) else (lambda _: r), v, flags=re.I)
    def _number(mo):
        values = list(mo.group(1))
        return re.sub(r"(\d)", lambda d: m[d.group(1)], "+".join([_digit(int(values.pop(0)))] + values))
    for c in sorted(m, key=ord):
        v = m[c]
        for k, r in CONSTRUCTORS.items():
            v = sub(v, r"\b" + k, r + "[\"constructor\"]")
        for k, r in SIMPLE.items():
            v = sub(v, k, r)
        v = sub(v, r"(\d\d+)", _number)
        v = sub(v, r"\((\d)\)", lambda d: m[d.group(1)])
        v = sub(v, r"\[(\d)\]", lambda d: m[d.group(1)])
        v = sub(v, r"\+\"\"", "+[]")
        m[c] = sub(v, "\"\"", "[]+[]")
    rx = re.compile(r"[^\[\]()!+]")
    for c in m:
        m[c] = re.sub(r"\"([^\"]+)\"", lambda mo: "+".join(mo.group(1)), m[c])
    while missing := {c: v for c, v in m.items() if rx.search(v)}:
        for c in missing:
            missing[c] = m[c] = rx.sub(lambda mo: mo.group() if mo.group() in missing else m[mo.group()], m[c])
    return m


MAPPING = __mapping()
_TOKEN = re.compile(r"false|true|undefined|NaN|Infinity|.", re.S)


def _escape_sequence(units, i, prefix):
    """ Escape sequence of the UTF-16 code unit at position i, padded when it would absorb the next character. """
    n = ord(units[i])
    if n >= 256:
        return f"{prefix}u{n:04x}"
    d = f"{n:o}"
    if i + 1 < len(units) and units[i+1] in "01234567" and len(d) < 3:
        d = d.zfill(3)
    return prefix + d


def _jsfuck(text, wrap=False):
    if not text:
        return ""
    e, units = _jsfuck, "".join(map(chr, utf16_units(text)))
    n = sum(c not in MAPPING for c in units)
    if n > 1:
        # escape sequences written with "t" instead of "\", replaced after splitting the string
        s = "".join(c if c in KEEP else _escape_sequence(units, i, "t") for i, c in enumerate(units))
    elif n == 1:
        s = "".join(c if c in MAPPING and c not in "\"\\" else _escape_sequence(units, i, "\\")
                    for i, c in enumerate(units))
    else:
        s = units
    out = "+".join(f"({SIMPLE[t]}+[])" if t in SIMPLE else MAPPING[t] for t in _TOKEN.findall(s))
    if re.fullmatch(r"\d", s):
        out += "+[]"
    if n > 1:
        out = f"({out})[{e('split')}]({e('t')})[{e('join')}]({e(chr(92))})"
    if n > 0:
        # Function("return\"" + <escaped text> + "\"")()
        out = f"[][{e('at')}][{e('constructor')}]({e('return' + chr(34))}+{out}+{e(chr(34))})()"
    if wrap:
        out = f"[][{e('at')}][{e('constructor')}]({out})()"
    return out


def jsfuck_encode(variant=""):
    def encode(text, errors="strict"):
        return _jsfuck(ensure_str(text), variant == "eval"), len(text)
    return encode


# --------------------------------------------------- Decoding ---------------------------------------------------------
# JavaScript values are represented by Python objects: undefined, booleans, numbers (floats), strings (of UTF-16 code
#  units), arrays (lists), and the classes below for the other objects ; the date is fixed, so that decoding is
#  reproducible
DATE = "Thu Jan 01 1970 00:00:00 GMT+0000 (Coordinated Universal Time)"
WHITESPACES = " \t\n\v\f\r\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029" \
              "\u202f\u205f\u3000\ufeff"
MAX_LENGTH = 1 << 24


class _JSError(Exception):
    pass


class _Undefined:
    pass


UNDEFINED = _Undefined()


class _Object:
    """ JavaScript object, known by its string representation (e.g. "[object Array Iterator]"). """
    def __init__(self, tag):
        self.tag = tag


class _RegExp:
    def __init__(self, source, flags=""):
        self.source, self.flags = source, flags


class _Function:
    """ JavaScript function, either native (with an implementation called with "this" and the list of arguments, if it
         is supported), or made with the Function constructor from its source code (with an implementation if it only
         returns a known value). """
    def __init__(self, name, impl=None, source=None, **props):
        self.name, self.impl, self.source, self.props = name, impl, source, props

    def __str__(self):
        if self.source is not None:
            return f"function anonymous(\n) {{\n{self.source}\n}}"
        return f"function {self.name}() {{ [native code] }}"


class _Code:
    """ Source code that a program runs, as the result of the decoding. """
    def __init__(self, source):
        self.source = source


def _raise(msg):
    raise _JSError(msg)


def _check(v):
    if isinstance(v, _Code):
        raise _JSError("the result of running some code cannot be used")
    return v


def _prim(v):
    """ ToPrimitive, with the default hint. """
    if isinstance(_check(v), list):
        return ",".join("" if x is UNDEFINED else _str(x) for x in v)
    if isinstance(v, _Object):
        return v.tag
    if isinstance(v, _RegExp):
        return f"/{v.source}/{v.flags}"
    if isinstance(v, _Function):
        return str(v)
    return v


def _str(v):
    """ ToString. """
    v = _prim(v)
    if v is UNDEFINED:
        return "undefined"
    if isinstance(v, bool):
        return ["false", "true"][v]
    if isinstance(v, float):
        return js_str(v)
    return v


def _num(v):
    """ ToNumber. """
    v = _prim(v)
    if v is UNDEFINED:
        return nan
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, float):
        return v
    s = v.strip(WHITESPACES)
    if s == "":
        return 0.
    for p, b in [("0x", 16), ("0o", 8), ("0b", 2)]:
        if s[:2].lower() == p and re.fullmatch("[0-9a-fA-F]+" if b == 16 else f"[0-{b-1}]+", s[2:]):
            return float(int(s[2:], b))
    if re.fullmatch(r"[+-]?(?:Infinity|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)", s):
        return float(s.replace("Infinity", "inf"))
    return nan


def _bool(v):
    """ ToBoolean. """
    if _check(v) is UNDEFINED:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, float):
        return v == v and v != 0
    if isinstance(v, str):
        return v != ""
    return True


def _int(v):
    """ ToIntegerOrInfinity. """
    v = _num(v)
    return 0 if v != v else v if not isfinite(v) else trunc(v)


def _add(a, b):
    a, b = _prim(a), _prim(b)
    if isinstance(a, str) or isinstance(b, str):
        if len(r := _str(a) + _str(b)) > MAX_LENGTH:
            raise _JSError("string too long")
        return r
    return _num(a) + _num(b)


def _arg(args, i=0, default=UNDEFINED):
    return args[i] if len(args) > i else default


def _index(n, length, negative=True):
    n = _int(n)
    return n + length if negative and n < 0 else n if negative or n >= 0 else -1


def _to_radix(x, radix):
    radix = 10 if radix is UNDEFINED else _int(radix)
    if not 2 <= radix <= 36:
        raise _JSError("toString() radix must be between 2 and 36")
    if radix == 10 or not isfinite(x):
        return js_str(x)
    if x != floor(x):
        raise _JSError("toString() with a radix is only supported for integers")
    n, digits, r = int(abs(x)), "0123456789abcdefghijklmnopqrstuvwxyz", ""
    while True:
        n, d = divmod(n, radix)
        r = digits[d] + r
        if n == 0:
            return "-" * (x < 0) + r


def _to_fixed(x, digits):
    d = _int(digits)
    if not 0 <= d <= 100:
        raise _JSError("toFixed() digits argument must be between 0 and 100")
    if not isfinite(x) or abs(x) >= 1e21:
        return js_str(x)
    # -0 is written without its sign, and halves are rounded up, as with the exact value of the number
    return str(Decimal(x + 0.).quantize(Decimal(1).scaleb(-d), ROUND_HALF_UP))


def _html(tag, attr=None):
    """ Method of the String HTML methods (e.g. "<i>text</i>" or "<font color=\"red\">text</font>"). """
    def _f(this, args):
        a = f" {attr}=\"{_str(_arg(args)).replace(chr(34), '&quot;')}\"" if attr else ""
        return f"<{tag}{a}>{_str(this)}</{tag}>"
    return _f


def _split(this, args):
    s, sep = _str(this), _arg(args)
    return [s] if sep is UNDEFINED else list(s) if (sep := _str(sep)) == "" else s.split(sep)


def _array(this):
    """ Array of the "this" of an array method, as array methods also work on strings (array-like objects). """
    if isinstance(_check(this), str):
        return list(this)
    if not isinstance(this, list):
        raise _JSError("array methods are only supported on arrays and strings")
    return this


def _strict_equal(x, y):
    """ Strict equality (===), for indexOf. """
    return x is y if not isinstance(x, (bool, float, str)) else type(x) is type(y) and x == y


def _same(x, y):
    """ SameValueZero, for includes (NaN being equal to itself). """
    return _strict_equal(x, y) or isinstance(x, float) and isinstance(y, float) and x != x and y != y


def _js_escape(this, args):
    s = _str(_arg(args))
    return "".join(c if re.match(r"[A-Za-z0-9@*_+\-./]", c) else f"%{ord(c):02X}" if ord(c) < 256 else
                   f"%u{ord(c):04X}" for c in s)


def _js_unescape(this, args):
    return re.sub(r"%u([0-9a-fA-F]{4})|%([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1) or m.group(2), 16)),
                  _str(_arg(args)))


def _regexp(this, args):
    p = _arg(args)
    if isinstance(p, _RegExp):
        return _RegExp(p.source, p.flags)
    s = "" if p is UNDEFINED else _str(p)
    # escape the slashes (outside of character classes and escapes) and the line terminators, as V8 does
    s = re.sub(r"\\.|\[(?:\\.|[^\]\\])*\]|/|\n|\r|\u2028|\u2029", lambda m: {'/': "\\/", '\n': "\\n", '\r': "\\r",
               '\u2028': "\\u2028", '\u2029': "\\u2029"}.get(m.group(), m.group()), s)
    return _RegExp(s or "(?:)")


def _new_array(this, args):
    if len(args) == 1 and isinstance(args[0], float):
        if args[0] != _int(args[0]) or not 0 <= args[0] <= MAX_LENGTH:
            raise _JSError("invalid array length")
        return [UNDEFINED] * int(args[0])
    return list(args)


def _function(this, args):
    """ The Function constructor: only the bodies returning a known global, a regular expression literal or a string
         literal give a function that can be called, other bodies being some code to run. """
    body = _str(_arg(args, default=""))
    b, value = body.strip(WHITESPACES), None
    if (m := re.fullmatch(r"return(?:[ \t]+(\w+)|[ \t]*/((?:\\.|[^/\\\n])+)/([dgimsuvy]*)|"
                          r"[ \t]*\"((?:\\.|[^\"\\])*)\"|[ \t]*'((?:\\.|[^'\\])*)');?", b, re.S)):
        name, rx, flags, dq, sq = m.groups()
        if name is not None:
            value = GLOBALS.get(name)
        elif rx is not None:
            value = _RegExp(rx, flags)
        else:
            value = "".join(map(chr, utf16_units(js_unescape(dq if dq is not None else sq, _raise))))
    return _Function("anonymous", None if value is None else lambda this, args: value, source=body)


def _call_method(this, args):
    f = _check(this)
    if not isinstance(f, _Function):
        raise _JSError("call() on a non-function")
    return _call(f, _arg(args), [])


def _m(name, impl=None):
    return name, _Function(name, impl)


def _char(negative, default, f=lambda c: c):
    """ Method returning (a function of) the character at the given position (from the end if negative). """
    def _f(this, args):
        s = _str(this)
        i = _index(_arg(args, default=0.), len(s), negative)
        return f(s[i]) if 0 <= i < len(s) else default
    return _f


STRING_PROTO = dict([
    _m("at", _char(True, UNDEFINED)), _m("charAt", _char(False, "")),
    _m("charCodeAt", _char(False, nan, lambda c: float(ord(c)))),
    _m("concat", lambda t, a: _add(_str(t), _str(a[0])) if a else _str(t)),
    _m("includes", lambda t, a: _str(_arg(a)) in _str(t)),
    _m("indexOf", lambda t, a: float(_str(t).find(_str(_arg(a))))),
    _m("slice", lambda t, a: _str(t)[max(0, _index(_arg(a, default=0.), len(_str(t)))):]),
    _m("substr", lambda t, a: _str(t)[max(0, _index(_arg(a, default=0.), len(_str(t)))):]),
    _m("substring", lambda t, a: _str(t)[max(0, _index(_arg(a, default=0.), 0, False)):]),
    _m("split", _split),
    _m("replace", lambda t, a: _str(t).replace(_str(_arg(a)), "undefined", 1)),
    _m("toLowerCase", lambda t, a: _str(t).lower()), _m("toUpperCase", lambda t, a: _str(t).upper()),
    _m("trim", lambda t, a: _str(t).strip(WHITESPACES)),
    _m("toString", lambda t, a: _str(t)), _m("valueOf", lambda t, a: _str(t)),
    _m("anchor", _html("a", "name")), _m("big", _html("big")), _m("blink", _html("blink")), _m("bold", _html("b")),
    _m("fixed", _html("tt")), _m("fontcolor", _html("font", "color")), _m("fontsize", _html("font", "size")),
    _m("italics", _html("i")), _m("link", _html("a", "href")), _m("small", _html("small")),
    _m("strike", _html("strike")), _m("sub", _html("sub")), _m("sup", _html("sup")),
    *map(_m, ["codePointAt", "endsWith", "isWellFormed", "lastIndexOf", "localeCompare", "match", "matchAll",
              "normalize", "padEnd", "padStart", "repeat", "replaceAll", "search", "startsWith", "toLocaleLowerCase",
              "toLocaleUpperCase", "toWellFormed", "trimEnd", "trimStart"]),
])
ARRAY_PROTO = dict([
    _m("at", lambda t, a: v[i] if 0 <= (i := _index(_arg(a, default=0.), len(v := _array(t)))) < len(v) else UNDEFINED),
    _m("concat", lambda t, a: _array(t) + (a[0] if isinstance(_arg(a), list) else a)),
    _m("entries", lambda t, a: _Object("[object Array Iterator]")),
    _m("keys", lambda t, a: _Object("[object Array Iterator]")),
    _m("values", lambda t, a: _Object("[object Array Iterator]")),
    _m("fill", lambda t, a: [_arg(a)] * len(_array(t))),
    _m("flat", lambda t, a: [y for x in _array(t) for y in (x if isinstance(x, list) else [x])]),
    _m("includes", lambda t, a: any(_same(x, _arg(a)) for x in _array(t))),
    _m("indexOf", lambda t, a: float(next((i for i, x in enumerate(_array(t)) if _strict_equal(x, _arg(a))), -1))),
    _m("join", lambda t, a: ("," if (s := _arg(a)) is UNDEFINED else _str(s)).join("" if x is UNDEFINED else _str(x)
                                                                                    for x in _array(t))),
    _m("reverse", lambda t, a: _array(t)[::-1]),
    _m("slice", lambda t, a: (v := _array(t))[max(0, _index(_arg(a, default=0.), len(v))):]),
    _m("toString", lambda t, a: _prim(_array(t))),
    *map(_m, ["copyWithin", "every", "filter", "find", "findIndex", "findLast", "findLastIndex", "flatMap", "forEach",
              "lastIndexOf", "map", "pop", "push", "reduce", "reduceRight", "shift", "some", "sort", "splice",
              "toLocaleString", "toReversed", "toSorted", "toSpliced", "unshift", "with"]),
])
NUMBER_PROTO = dict([
    _m("toString", lambda t, a: _to_radix(_num(t), _arg(a))), _m("toFixed", lambda t, a: _to_fixed(_num(t), _arg(a))),
    _m("valueOf", lambda t, a: _num(t)), *map(_m, ["toExponential", "toLocaleString", "toPrecision"]),
])
BOOLEAN_PROTO = dict([_m("toString", lambda t, a: _str(t)), _m("valueOf", lambda t, a: t)])
FUNCTION_PROTO = dict([_m("toString", lambda t, a: _str(t)), _m("call", _call_method), *map(_m, ["apply", "bind"])])
REGEXP_PROTO = dict([_m("toString", lambda t, a: _str(t)), *map(_m, ["exec", "test"])])
OBJECT_PROTO = dict([_m("toString", lambda t, a: "[object Object]"), *map(_m, ["hasOwnProperty", "isPrototypeOf",
                     "propertyIsEnumerable", "toLocaleString", "valueOf"])])
# constructors, with their static properties
STRING = _Function("String", lambda t, a: _str(a[0]) if a else "",
                   fromCharCode=_Function("fromCharCode", lambda t, a: chr(int(n) % 65536 if isfinite(n := _num(
                                          _arg(a, default=0.))) else 0)))
NUMBER = _Function("Number", lambda t, a: _num(a[0]) if a else 0.)
BOOLEAN = _Function("Boolean", lambda t, a: _bool(_arg(a)))
ARRAY = _Function("Array", _new_array)
FUNCTION = _Function("Function", _function)
REGEXP = _Function("RegExp", _regexp)
OBJECT = _Function("Object", lambda t, a: _Object("[object Object]") if _arg(a) is UNDEFINED else _arg(a))
for _proto, _ctor in [(STRING_PROTO, STRING), (ARRAY_PROTO, ARRAY), (NUMBER_PROTO, NUMBER), (BOOLEAN_PROTO, BOOLEAN),
                      (FUNCTION_PROTO, FUNCTION), (REGEXP_PROTO, REGEXP), (OBJECT_PROTO, OBJECT)]:
    _proto['constructor'] = _ctor
# globals that "Function('return <name>')()" can give
GLOBALS = {f.name: f for f in [STRING, NUMBER, BOOLEAN, ARRAY, FUNCTION, REGEXP, OBJECT]}
GLOBALS.update({
    'Date': _Function("Date", lambda t, a: DATE),
    'escape': _Function("escape", _js_escape),
    'unescape': _Function("unescape", _js_unescape),
    'eval': _Function("eval", lambda t, a: _Code(a[0]) if isinstance(_arg(a), str) else _arg(a)),
})


def _get(o, k):
    """ Property access o[k]. """
    k = _str(k)
    if _check(o) is UNDEFINED:
        raise _JSError(f"cannot read property '{k[:20]}' of undefined")
    proto = OBJECT_PROTO
    if isinstance(o, (str, list)):
        if re.fullmatch(r"0|[1-9]\d{0,9}", k):
            return o[int(k)] if int(k) < len(o) else UNDEFINED
        if k == "length":
            return float(len(o))
        proto = STRING_PROTO if isinstance(o, str) else ARRAY_PROTO
    elif isinstance(o, bool):
        proto = BOOLEAN_PROTO
    elif isinstance(o, float):
        proto = NUMBER_PROTO
    elif isinstance(o, _Function):
        if k in o.props:
            return o.props[k]
        if k == "name":
            return o.name
        proto = FUNCTION_PROTO
    elif isinstance(o, _RegExp):
        if k in ("source", "flags"):
            return getattr(o, k)
        proto = REGEXP_PROTO
    return proto.get(k, OBJECT_PROTO.get(k, UNDEFINED))


def _call(f, this, args):
    if not isinstance(_check(f), _Function):
        raise _JSError(f"'{_str(f)[:20]}' is not a function")
    if f.impl is None:
        if f.source is not None:
            return _Code(f.source)
        raise _JSError(f"calling {f.name}() is not supported")
    return f.impl(this, args)


class _Parser:
    """ Recursive descent parser of the JSFuck grammar, evaluating the expression while parsing it:
          expression := unary ("+" unary)*
          unary      := ("!" | "+") unary | postfix
          postfix    := ("[" expression? "]" | "(" expression ")") ("[" expression "]" | "(" expression? ")")* """
    def __init__(self, code):
        self.s, self.i = code, 0

    def _expect(self, c):
        if self.s[self.i:self.i+1] != c:
            raise _JSError(f"expected '{c}' at position {self.i}")
        self.i += 1

    def _next_is(self, c):
        if self.s[self.i:self.i+1] == c:
            self.i += 1
            return True
        return False

    def expression(self):
        v = self.unary()
        while self._next_is("+"):
            v = _add(v, self.unary())
        return v

    def unary(self):
        if self._next_is("!"):
            return not _bool(self.unary())
        if self._next_is("+"):
            return _num(self.unary())
        if self._next_is("["):
            v = [] if self._next_is("]") else [self.expression()]
            if v:
                self._expect("]")
        elif self._next_is("("):
            v = self.expression()
            self._expect(")")
        else:
            raise _JSError(f"unexpected {'end' if self.i >= len(self.s) else repr(self.s[self.i])} at position "
                           f"{self.i}")
        this = UNDEFINED
        while True:
            if self._next_is("["):
                k = self.expression()
                self._expect("]")
                this, v = v, _get(v, k)
            elif self._next_is("("):
                args = [] if self._next_is(")") else [self.expression()]
                if args:
                    self._expect(")")
                v, this = _call(v, this, args), UNDEFINED
            else:
                return v


def jsfuck_run(code):
    """ Evaluate a JSFuck expression and return its value as a string, or the code it runs. """
    code = re.sub(r"\s+", "", code)
    if code == "":
        return ""
    p = _Parser(code)
    try:
        v = p.expression()
        if p.i < len(code):
            raise _JSError(f"unexpected {code[p.i]!r} at position {p.i}")
        v = v.source if isinstance(v, _Code) else _str(v)
    except _JSError as e:
        raise JsfuckDecodeError(f"'jsfuck' codec can't decode: {e}")
    except RecursionError:
        raise JsfuckDecodeError("'jsfuck' codec can't decode: expression nested too deeply")
    # combine the UTF-16 surrogate pairs
    return v.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass")


def jsfuck_decode(variant=""):
    def decode(text, errors="strict"):
        return (r := jsfuck_run(ensure_str(text))), len(r)
    return decode


add("jsfuck", jsfuck_encode, jsfuck_decode, r"^jsfuck(?:[-_](eval))?$", printables_rate=1., expansion_factor=None)
