# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from six import b, binary_type, text_type

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
    if args.infile:
        with open(args.infile, 'rb') as f:
            c = f.read()
    else:
        c = b("")
        for line in __stdin_pipe():
            c += line
    # encode or decode
    c = getattr(codecs, ["encode", "decode"][args.decode])\
        (c, args.encoding, args.errors)
    # hanbdle output file or stdout
    if args.outfile:
        with open(args.outfile, 'wb') as f:
            f.write(c)
    else:
        if PY3:
            try:
                c = c.decode("utf-8")
            except:
                c = c.decode("latin-1")
        print(c)
