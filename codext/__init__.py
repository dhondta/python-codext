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


def main():
    import argparse, os
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--decode")
    group.add_argument("-e", "--encode")
    parser.add_argument("-i", "--input-file", dest="infile")
    parser.add_argument("-o", "--output-file", dest="outfile")
    args = parser.parse_args()
    if os.path.isfile(args.infile):
        with codecs.open(f, encoding=args.decode) as fin:
            c = fin.read()
    else:
        pass  #FIXME: take from stdin
    if args.outfile is None:
        print(c)
    else:
        with open(args.outfile, 'w') as fout:
            fout.write(c)
