# -*- coding: UTF-8 -*-
from argparse import ArgumentParser, RawTextHelpFormatter
from types import MethodType

from .base45 import *
from .base85 import *
from .base91 import *
from .base100 import *
from .base122 import *
from .baseN import *
from ..__common__ import *
from ..__info__ import __version__


def main():
    descr = """Usage: unbase [OPTION]... [FILE]
Decode multi-layer base encoded FILE, or standard input, to standard output.

With no FILE, or when FILE is -, read standard input.

Optional arguments:
  -E, --extended        also consider generic base codecs while guess-decoding
  -f, --stop-function   set the result chceking function (default: text)
                         format: printables|text|flag|lang_[bigram]
  -M, --max-depth       maximum codec search depth (default: 5)
  -m, --min-depth       minimum codec search depth (default: 0)
  -p, --pattern         pattern to be matched while searching
  -s, --show            show the decoding chain

      --help     display this help and exit
      --verbose  show guessing information and steps
      --version  output version information and exit

Report unbase bugs to <https://github.com/dhondta/python-codext/issues/new>
Full documentation at: <https://python-codext.readthedocs.io/en/latest/enc/base.html>
"""
    parser = ArgumentParser(description=descr, formatter_class=RawTextHelpFormatter, add_help=False)
    parser.format_help = MethodType(lambda s: s.description, parser)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("file", nargs="?")
    parser.add_argument("-E", "--extended", action="store_true")
    group.add_argument("-f", "--stop-function", default="text")
    parser.add_argument("-M", "--max-depth", type=int, default=10)
    parser.add_argument("-m", "--min-depth", type=int, default=0)
    group.add_argument("-p", "--pattern")
    parser.add_argument("-s", "--show", action="store_true")
    parser.add_argument("--help", action="help")
    parser.add_argument("--version", action="version")
    parser.add_argument("--verbose", action="store_true")
    parser.version = "CodExt " + __version__
    args = parser.parse_args()
    c, e = _input(args.file), [["base%d-generic" % i for i in range(2, 256)], []][args.extended]
    c = c.rstrip("\r\n") if isinstance(c, str) else c.rstrip(b"\r\n")
    r = codecs.guess(c, stopfunc._validate(args.stop_function), 0, args.max_depth, "base", tuple(e), stop=False,
                     show=args.verbose, debug=args.verbose)
    if len(r) == 0:
        print("Could not decode :-(")
        return 0
    ans = max(r.items(), key=lambda x: len(x[0]))
    if args.show:
        print(" - ".join(ans[0]))
    print(ensure_str(ans[1]))
    return 0

