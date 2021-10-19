# -*- coding: UTF-8 -*-
"""Generic baseN functions.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from math import log
from six import integer_types, string_types
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits, printable
from textwrap import wrap
from types import FunctionType, MethodType

from ..__common__ import *
from ..__info__ import __version__


class BaseError(ValueError):
    pass


class BaseDecodeError(BaseError):
    pass


class BaseEncodeError(BaseError):
    pass


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
    elif isinstance(charset, string_types):
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
        default, n = None, None
        for pattern, cset in charset.items():
            n = len(cset)
            if pattern == "":
                default = cset
                continue
            if re.match(pattern, p):
                return cset
        # special case: the given [p]arameter can be the charset itself if it has the right length
        p = re.sub(r"^[-_]+", "", p)
        if len(p) == n:
            return p
        # or simply rely on key ''
        if default is not None:
            return default
    raise ValueError("Bad charset descriptor")


# generic base en/decoding functions
def base_encode(input, charset, errors="strict", exc=BaseEncodeError):
    """ Base-10 to base-N encoding.
    
    :param input:   input (str or int) to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    i, n, r = input if isinstance(input, integer_types) else s2i(input), len(charset), ""
    while i > 0:
        i, c = divmod(i, n)
        r = charset[c] + r
    return r


def base_decode(input, charset, errors="strict", exc=BaseDecodeError):
    """ Base-N to base-10 decoding.
    
    :param input:   input to be decoded
    :param charset: base-N characters set
    :param errors:  errors handling marker
    :param exc:     exception to be raised in case of error
    """
    i, n, dec = 0, len(charset), lambda n: base_encode(n, [chr(x) for x in range(256)], errors, exc)
    for k, c in enumerate(input):
        try:
            i = i * n + charset.index(c)
        except ValueError:
            handle_error("base", errors, exc, decode=True)(c, k, dec(i))
    return dec(i)


# base codec factory functions
def base(charset, pattern, pow2=False, encode_template=base_encode, decode_template=base_decode, name=None, **kwargs):
    """ Base-N codec factory.
    
    :param charset: charset selection function
    :param pattern: matching pattern for the codec name (first capturing group is used as the parameter for selecting
                     the charset)
    :param pow2:    whether the base codec's N is a power of 2
    """
    n = len(_get_charset(charset))
    nb = log(n, 2)
    if pow2 and nb != int(nb):
        raise BaseError("Bad charset ; {} is not a power of 2".format(n))
    
    def encode(param=""):
        a = _get_charset(charset, param)
        def _encode(input, errors="strict"):
            return encode_template(input, a, errors), len(input)
        return _encode
    
    def decode(param=""):
        a = _get_charset(charset, param)
        sl, sc = "\n" not in a, "\n" not in a and not "\r" in a
        def _decode(input, errors="strict"):
            input = _stripl(input, sc, sl)
            return decode_template(input, a, errors), len(input)
        return _decode
    
    kwargs['len_charset'] = n
    kwargs['printables_rate'] = 1.
    n = "base{}".format(n) if name is None else name
    kwargs['guess'] = kwargs.get('guess', [n])
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
        guess=["base%d-generic" % i for i in range(2, 255)], entropy=lambda e, n: log(int(n.split("-")[0][4:]), 2),
        len_charset=lambda n: int(n.split("-")[0][4:]), printables_rate=1., category="base-generic", penalty=.4)


def main(n, ref=None, alt=None, inv=True):
    base = str(n) + ("-" + alt.lstrip("-") if alt else "")
    src = "The data are encoded as described for the base%(base)s alphabet in %(reference)s.\n" % \
          {'base': base, 'reference': "\n" + ref if len(ref) > 20 else ref} if ref else ""
    descr = """Usage: base%(base)s [OPTION]... [FILE]
Base%(base)s encode or decode FILE, or standard input, to standard output.

With no FILE, or when FILE is -, read standard input.

Mandatory arguments to long options are mandatory for short options too.
  -d, --decode          decode data
  -i, --ignore-garbage  when decoding, ignore non-alphabet characters
%(inv)s  -w, --wrap=COLS       wrap encoded lines after COLS character (default 76).
                          Use 0 to disable line wrapping

      --help     display this help and exit
      --version  output version information and exit

%(source)sWhen decoding, the input may contain newlines in addition to the bytes of
the formal base%(base)s alphabet.  Use --ignore-garbage to attempt to recover
from any other non-alphabet bytes in the encoded stream.

Report base%(base)s translation bugs to <https://github.com/dhondta/python-codext/issues/new>
Full documentation at: <https://python-codext.readthedocs.io/en/latest/enc/base.html>
""" % {'base': base, 'source': src,
       'inv': ["", "  -I, --invert          invert charsets from the base alphabet (e.g. lower- and uppercase)\n"][inv]}
    
    def _main():
        p = ArgumentParser(description=descr, formatter_class=RawTextHelpFormatter, add_help=False)
        p.format_help = MethodType(lambda s: s.description, p)
        p.add_argument("file", nargs="?")
        p.add_argument("-d", "--decode", action="store_true")
        p.add_argument("-i", "--ignore-garbage", action="store_true")
        if inv:
            p.add_argument("-I", "--invert", action="store_true")
        p.add_argument("-w", "--wrap", type=int, default=76)
        p.add_argument("--help", action="help")
        p.add_argument("--version", action="version")
        p.version = "CodExt " + __version__
        args = p.parse_args()
        args.invert = getattr(args, "invert", False)
        c, f = _input(args.file), [encode, decode][args.decode]
        c = c.rstrip("\r\n") if isinstance(c, str) else c.rstrip(b"\r\n")
        try:
            c = f(c, "base" + base + ["", "-inv"][args.invert], ["strict", "ignore"][args.ignore_garbage])
        except Exception as err:
            print("%sbase%s: invalid input" % (getattr(err, "output", ""), base))
            return 1
        for l in wrap(ensure_str(c), args.wrap):
            print(l)
        return 0
    return _main

