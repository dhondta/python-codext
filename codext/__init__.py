# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from .__common__ import *
from .__info__ import __author__, __copyright__, __license__, __version__


__all__ = ["add", "clear", "decode", "encode", "lookup",  "open", "register",
           "remove", "reset"]


decode   = codecs.decode
encode   = codecs.encode
lookup   = codecs.lookup
open     = codecs.open


reset()


def __stdin_pipe():
    """ Stdin pipe read function. """
    try:
        with open(0, 'rb') as f:
            for l in f:
                yield l
    except TypeError:
        import sys
        for l in sys.stdin:
            yield l


def main():
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument("encoding")
    parser.add_argument("-d", "--decode", action="store_true")
    parser.add_argument("-e", "--errors", default="strict",
                        choices=["ignore", "replace", "strict"],
                        help="ignore|replace|strict")
    parser.add_argument("-i", "--input-file", dest="infile")
    parser.add_argument("-o", "--output-file", dest="outfile")
    args = parser.parse_args()
    # handle input file or stdin
    if os.path.isfile(args.infile):
        with open(args.infile) as f:
            c = f.read()
    else:
        c = ""
        for line in __stdin_pipe():
            c += codecs.encode(line, errors=args.errors)
    # encode or decode
    c = getattr(codext, ["encode", "decode"][args.decode])\
        (c, args.encoding, args.errors)
    # hanbdle output file or stdout
    if args.outfile is None:
        print(c)
    else:
        with open(args.outfile, 'w') as f:
            f.write(c)
