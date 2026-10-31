# -*- coding: UTF-8 -*-
"""Generic baseN functions.

This module holds the common machinery of the base codecs: the charset selection (a charset may depend on the variant
 given in the codec name, e.g. "-inv" for inverted charsets), the generic base conversion and the codec factory, the
 generic "baseN-generic" codec (N from 2 to 255, with a generated charset) and the command-line tool factory used by the
 baseXX console scripts.

When N is not a power of 2, the whole input is converted as a single big integer written in base N (most significant
 digit first), each leading null byte of the input being kept as a leading first character of the charset (as Base58
 does).
"""
from argparse import ArgumentParser, RawTextHelpFormatter
from functools import lru_cache
from math import log
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits, printable
from sys import stderr, stdout
from textwrap import wrap as wraptext
from types import FunctionType, MethodType

from ..__common__ import *
from ..__common__ import _set_exc
from ..__info__ import __version__


_set_exc("BaseError")
_set_exc("BaseEncodeError")
_set_exc("BaseDecodeError")
"""
Curve fitting:

>>> import matplotlib.pyplot as plt
>>> import pandas as pd
>>> import scipy.optimize
>>> from statistics import mean
>>> from tinyscript import random
>>> x, y = [], []
>>> for i in range(2, 256):
	v = []
	for j in range(16, 2048, 16):
		s = random.randstr(j)
		v.append(float(len(codext.encode(s, "base%d-generic" % i))) / len(s))
	x.append(i)
	y.append(mean(v))
>>> data = pd.DataFrame({'base': x, 'expf': y})
>>> def fit(x, y, func, params):
	params, cv = scipy.optimize.curve_fit(func, x, y, params)
	print(params)
	y2 = func(x, *params)
	plt.clf()
	plt.plot(x, y, ".", color="blue", alpha=.3)
	plt.plot(x, y2, color="red", linewidth=3.0)
	plt.show()
>>> fit(data['base'], data['expf'], lambda x, a, b, c, d: a / (x**b + c) + d, (1, 1, 1, 1))
[ 0.02841434  0.00512664 -0.99999984  0.01543879]
>>> fit(data['base'], data['expf'], lambda x, a, b, c, d: a / (x**b + c) + d, (.028, .005, -1, .015))
[ 0.02827357  0.00510124 -0.99999984  0.01536941]
"""
EXPANSION_FACTOR = lambda base: 0.02827357 / (base**0.00510124-0.99999984) + 0.01536941
SIZE_LIMIT = 1024 * 1024 * 1024


def _generate_charset(n):
    """ Generate a characters set.
    
    :param n: size of charset
    """
    if 1 < n <= len(printable):
        return printable[:n]
    elif len(printable) < n < 256:
        return "".join(chr(i) for i in range(n))
    raise ValueError("Bad size of character set")


def _get_charset(charset, p=""):
    """ Characters set selection function. It allows to define charsets in many different ways.
    
    :param charset: charset object, can be a string (the charset itself), a function (that chooses the right charset
                     depending on the input parameter) or a dictionary (either by exact key or by pattern matching)
    :param p:       the parameter for choosing the charset
    """
    # case 1: charset is a function, so return its result
    if isinstance(charset, FunctionType):
        return charset(p)
    # case 2: charset is a string, so return it
    elif isinstance(charset, str):
        return charset
    # case 3: charset is a dict with keys '' and 'inv', typically for a charset using lowercase and uppercase characters
    #          that can be inverted
    elif isinstance(charset, dict) and list(charset.keys()) == ["", "inv"]:
        return charset["inv" if re.match(r"[-_]inv(erted)?$", p) else ""]
    # case 4: charset is a dict, but not with the specific keys '' and 'inv', so consider it as pattern-charset pairs
    elif isinstance(charset, dict):
        # try to handle [p]arameter as a simple key
        try:
            return charset[p]
        except KeyError:
            pass
        # or handle [p]arameter as a pattern
        default, n, best = None, None, None
        for pattern, cset in charset.items():
            n = len(cset)
            if re.match(pattern, ""):
                default = cset
                continue
            m = re.match(pattern, p)
            if m:  # find the longest match from the patterns
                s, e = m.span()
                if e - s > len(best or ""):
                    best = pattern
        if best:
            return charset[best]
        # special case: the given [p]arameter can be the charset itself if it has the right length
        p = re.sub(r"^[-_]+", "", p)
        if len(p) == n:
            return p
        # or simply rely on key ''
        if default is not None:
            return default
    raise ValueError(f"Bad charset descriptor ('{p}')")


# generic base en/decoding functions
# conversions between integers and digits in base N split the numbers with powers of N (divide and conquer), as repeated
#  divisions or multiplications by N take a quadratic time with large numbers ; below this number of digits, the
#  simple loops are faster
_SMALL = 64


@lru_cache(maxsize=128)
def _power(n, k):
    return n ** k


def _to_digits(i, n, width=0):
    """ Digits of the integer i in base N (as indices in the charset), left-padded with zeros to the given width (by
         default, the smallest power of 2 holding i, the leading zeros being then removed). """
    if (width or _SMALL + 1) <= _SMALL or not width and i < _power(n, _SMALL):
        d = []
        while i:
            i, c = divmod(i, n)
            d.append(c)
        return [0] * (width - len(d)) + d[::-1]
    top = not width
    if top:
        width = 2 * _SMALL
        while _power(n, width) <= i:
            width *= 2
    half = width // 2
    hi, lo = divmod(i, _power(n, half))
    d = _to_digits(hi, n, width - half) + _to_digits(lo, n, half)
    if top:
        k = 0
        while d[k] == 0:
            k += 1
        d = d[k:]
    return d


def _from_digits(d, n):
    """ Integer of the digits in base N (as indices in the charset), combining halves as hi * N^len(lo) + lo. """
    if len(d) <= _SMALL:
        i = 0
        for c in d:
            i = i * n + c
        return i
    half = len(d) // 2
    return _from_digits(d[:half], n) * _power(n, len(d) - half) + _from_digits(d[half:], n)


def base_encode(input, charset, errors="strict", exc=BaseEncodeError):
    """ Base-10 to base-N encoding.
    
    :param input:   input (str or int) to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    i, n = input if isinstance(input, int) else s2i(input) if input else 0, len(charset)
    if n == 1:
        if i > SIZE_LIMIT:
            raise InputSizeLimitError("Input exceeded size limit")
        return i * charset[0]
    # keep this fast-path only for a non-standard 10-character charset ; the digits
    # charset uses the generic conversion below (leading zeros, bignums, no str/int round-trip)
    if n == 10 and charset != digits:
        return "".join(charset[int(x)] for x in str(i))
    r = "".join(charset[c] for c in _to_digits(i, n)) if i > 0 else ""
    # preserve leading zero bytes: big-integer bases such as Base58 map each
    # leading null byte of the input to a leading charset[0] character
    if not isinstance(input, int):
        r = charset[0] * (len(input) - len(input.lstrip("\x00"))) + r
    return r


def base_decode(input, charset, errors="strict", exc=BaseDecodeError):
    """ Base-N to base-10 decoding.
    
    :param input:   input to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    n = len(charset)
    if n == 1:
        return i2s(len(input))
    if n == 10 and charset != digits:
        return "".join(str(charset.index(c)) for c in input)
    # index of each character (the first one, if the charset holds a character more than once)
    index, d = {c: k for k, c in reversed(list(enumerate(charset)))}, []
    for k, c in enumerate(input):
        try:
            d.append(index[c])
        except KeyError:
            # no output decoded up to the error, as the digits before it are not the beginning of the number
            handle_error("base", errors, exc, decode=True)(c, k, "", f"base{n}")
    i = _from_digits(d, n)
    # restore the leading zero bytes encoded as leading charset[0] characters
    return chr(0) * (len(input) - len(input.lstrip(charset[0]))) + i.to_bytes((i.bit_length() + 7) // 8,
                                                                              "big").decode("latin-1")


# base codec factory functions
def base(charset, pattern, pow2=False, encode_template=base_encode, decode_template=base_decode, name=None, **kwargs):
    """ Base-N codec factory.
    
    :param charset: charset selection function
    :param pattern: matching pattern for the codec name (first capturing group is used as the parameter for selecting
                     the charset)
    :param pow2:    whether the base codec's N is a power of 2
    """
    cs = _get_charset(charset)
    n = len(cs)
    nb = log(n, 2)
    if pow2 and nb != int(nb):
        raise BaseError("Bad charset ; {} is not a power of 2".format(n))
    
    def encode(param="", *args):
        a = _get_charset(charset, args[0] if len(args) > 0 and args[0] else param)
        def _encode(input, errors="strict"):
            if len(input) == 0:
                return "", 0
            return encode_template(input, a, errors), len(input)
        return _encode
    
    def decode(param="", *args):
        a = _get_charset(charset, args[0] if len(args) > 0 and args[0] else param)
        sl, sc = "\n" not in a, "\n" not in a and not "\r" in a
        def _decode(input, errors="strict"):
            if len(input) == 0:
                return "", 0
            input = _stripl(input, sc, sl)
            return decode_template(input, a, errors), len(input)
        return _decode
    
    kwargs['len_charset'] = n
    kwargs['printables_rate'] = float(len([c for c in cs if c in printable])) / len(cs)
    kwargs['expansion_factor'] = kwargs.pop('expansion_factor', (EXPANSION_FACTOR(n), .05))
    n = "base{}".format(n) if name is None else name
    try:
        g = [n, n + "-inv"] if "[-_]inv(erted)?$" in charset.keys() else [n]
    except AttributeError:
        g = [n]
    kwargs['guess'] = kwargs.get('guess', g)
    add(n, encode, decode, pattern, entropy=nb, **kwargs)


def base_generic():
    """ Base-N generic codec. """
    def encode(n):
        a = _generate_charset(int(n))
        def _encode(input, errors="strict"):
            return base_encode(input, a, errors), len(input)
        return _encode
    
    def decode(n):
        a = _generate_charset(int(n))
        sl, sc = "\n" not in a, "\n" not in a and not "\r" in a
        def _decode(input, errors="strict"):
            input = _stripl(input, sc, sl)
            return base_decode(input, a, errors), len(input)
        return _decode
    
    add("base", encode, decode, r"^base[-_]?([2-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?:[-_]generic)?$",
        guess=[f"base{i}-generic" for i in range(2, 255)], entropy=lambda e, n: log(int(n.split("-")[0][4:]), 2),
        len_charset=lambda n: int(n.split("-")[0][4:]), printables_rate=1., category="base-generic", penalty=.4,
        expansion_factor=lambda f, n: (EXPANSION_FACTOR(int(n.split("-")[0][4:])), .05))


def main(n, ref=None, alt=None, inv=True, swap=True, wrap=True):
    base = str(n) + ("-" + alt.lstrip("-") if alt else "")
    src = "The data are encoded as described for the base%(base)s alphabet in %(reference)s.\n" % \
          {'base': base, 'reference': "\n" + ref if len(ref) > 20 else ref} if ref else ""
    text = "%(source)sWhen decoding, the input may contain newlines in addition to the bytes of the formal base" \
           "%(base)s alphabet.  Use --ignore-garbage to attempt to recover from any other non-alphabet bytes in the" \
           " encoded stream." % {'base': base, 'source': src}
    text = "\n".join(x for x in wraptext(text, 74))
    descr = """Usage: base%(base)s [OPTION]... [FILE]
Base%(base)s encode or decode FILE, or standard input, to standard output.

With no FILE, or when FILE is -, read standard input.

Mandatory arguments to long options are mandatory for short options too.
  -d, --decode          decode data
  -i, --ignore-garbage  when decoding, ignore non-alphabet characters
%(inv)s%(swap)s%(wrap)s

      --help     display this help and exit
      --version  output version information and exit

%(text)s

Report base%(base)s translation bugs to <https://github.com/dhondta/python-codext/issues/new>
Full documentation at: <https://python-codext.readthedocs.io/en/latest/enc/base.html>
""" % {'base': base, 'text': text,
       'inv': ["", "  -I, --invert          invert charsets from the base alphabet (e.g. digits and letters)\n"][inv],
       'swap': ["", "  -s, --swapcase        swap the case\n"][swap],
       'wrap': ["", "  -w, --wrap=COLS       wrap encoded lines after COLS character (default 76).\n"+ 26 * " " + \
                    "Use 0 to disable line wrapping"][wrap]}
    
    def _main():
        p = ArgumentParser(description=descr, formatter_class=RawTextHelpFormatter, add_help=False)
        p.format_help = MethodType(lambda s: s.description, p)
        p.add_argument("file", nargs="?")
        p.add_argument("-d", "--decode", action="store_true")
        p.add_argument("-i", "--ignore-garbage", action="store_true")
        if inv:
            p.add_argument("-I", "--invert", action="store_true")
        if swap:
            p.add_argument("-s", "--swapcase", action="store_true")
        if wrap:
            p.add_argument("-w", "--wrap", type=int, default=76)
        p.add_argument("--help", action="help")
        p.add_argument("--version", action="version")
        p.version = "CodExt " + __version__
        args = p.parse_args()
        if args.decode:
            args.wrap = 0
        args.invert = getattr(args, "invert", False)
        c, f = _input(args.file), [encode, decode][args.decode]
        if swap and args.swapcase and args.decode:
            c = codecs.decode(c, "swapcase")
        c = b(c).rstrip(b"\r\n")
        try:
            c = f(c, "base" + base + ["", "-inv"][getattr(args, "invert", False)],
                  ["strict", "ignore"][args.ignore_garbage])
        except Exception as err:
            # as GNU's base64, write the output decoded up to the error (if any), then report the error on stderr
            stdout.buffer.write(b(getattr(err, "output", "") or ""))
            stdout.flush()
            print(f"base{base}: invalid input", file=stderr)
            return 1
        if args.decode:
            stdout.buffer.write(c)
            return 0
        c = ensure_str(c)
        if swap and args.swapcase:
            c = codecs.encode(c, "swapcase")
        for l in (wraptext(c, args.wrap) if args.wrap > 0 else [c]) if wrap else c.split("\n"):
            print(l)
        return 0
    return _main

