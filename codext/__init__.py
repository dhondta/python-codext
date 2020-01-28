# -*- coding: UTF-8 -*-
"""Module for enhancing codecs preimport.

"""
import os

from .__common__ import add, codecs


__all__ = ["add", "decode", "encode", "lookup",  "open", "register"]


decode   = codecs.decode
encode   = codecs.encode
lookup   = codecs.lookup
open     = codecs.open
register = codecs.register


for f in os.listdir(os.path.dirname(__file__)):
    if not f.endswith(".py") or f == "__init__.py":
        continue
    __import__(f[:-3], globals(), locals(), [], 1)


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
