# -*- coding: UTF-8 -*-
from argparse import ArgumentParser, RawTextHelpFormatter
from types import MethodType

from .ascii85 import *
from .base45 import *
from .base85 import *
from .base91 import *
from .base100 import *
from .base122 import *
from .baseN import *
from ..__common__ import *
from ..__info__ import __version__


def main():
    descr = """Usage: debase [OPTION]... [FILE]
Base decode multi-layer FILE, or standard input, to standard output.

With no FILE, or when FILE is -, read standard input.

Optional arguments:
  -f, --stop-function   set the result chceking function (default: text)
                         format: printables|text|flag|lang_[bigram]|[regex]
  -i, --ignore-generic  ignore generic base codecs while guess-decoding
  -M, --max-depth       maximum codec search depth (default: 5)
  -m, --min-depth       minimum codec search depth (default: 0)
  -s, --do-not-stop     do not stop if a valid output is found

      --help     display this help and exit
      --verbose  show guessing information and steps
      --version  output version information and exit

Report debase bugs to <https://github.com/dhondta/python-codext/issues/new>
Full documentation at: <https://python-codext.readthedocs.io/en/latest/enc/base.html>
"""
    parser = ArgumentParser(description=descr, formatter_class=RawTextHelpFormatter, add_help=False)
    parser.format_help = MethodType(lambda s: s.description, parser)
    parser.add_argument("file", nargs="?")
    parser.add_argument("-f", "--stop-function", default="text")
    parser.add_argument("-i", "--ignore-generic", action="store_true")
    parser.add_argument("-M", "--max-depth", default=5, type=int)
    parser.add_argument("-m", "--min-depth", default=0, type=int)
    parser.add_argument("-s", "--do-not-stop", action="store_true")
    parser.add_argument("--help", action="help")
    parser.add_argument("--version", action="version")
    parser.add_argument("--verbose", action="store_true")
    parser.version = "CodExt " + __version__
    args = parser.parse_args()
    excl = [[], ["base%d-generic" % i for i in range(2, 255)]][args.ignore_generic]
    sfunc = getattr(stopfunc, args.stop_function, args.stop_function)
    c = _input(args.file)
    c = c.rstrip("\r\n") if isinstance(c, str) else c.rstrip(b"\r\n")
    r = codecs.guess(c, sfunc, args.min_depth, args.max_depth, exclude=excl, codec_categories="base",
                     stop=not args.do_not_stop, show=True, scoring_heuristic=False, debug=args.verbose)
    if not args.do_not_stop:
        print("Could not decode :-(" if len(r) == 0 else ensure_str(list(r.items())[0][1]))

