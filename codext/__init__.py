# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from __future__ import print_function
from six import b, binary_type, text_type

from .__common__ import *
from .__info__ import __author__, __copyright__, __email__, __license__, __source__, __version__


__all__ = ["add", "add_map", "clear", "decode", "encode", "guess", "lookup",  "open", "register", "remove", "reset"]

decode   = codecs.decode
encode   = codecs.encode
guess    = codecs.guess
lookup   = codecs.lookup
open     = codecs.open

list = list_encodings  # not included in __all__ because of shadow name


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
    descr = "Codecs Extension (CodExt) {}\n\nAuthor   : {} ({})\nCopyright: {}\nLicense  : {}\nSource   : {}\n" \
            "\nThis tool allows to encode/decode input strings/files with an extended set of codecs.\n\n" \
            .format(__version__, __author__, __email__, __copyright__, __license__, __source__)
    examples = "usage examples:\n- " + "\n- ".join([
        "codext search bitcoin",
        "codext decode base32 -i file.b32",
        "codext encode morse < to_be_encoded.txt",
        "echo \"test\" | codext encode base100",
        "echo -en \"test\" | codext encode braille -o test.braille",
        "codext encode base64 < to_be_encoded.txt > text.b64",
        "echo -en \"test\" | codext encode base64 | codext encode base32",
        "echo -en \"mrdvm6teie6t2cq=\" | codext encode upper | codext decode base32 | codext decode base64",
        "echo -en \"test\" | codext encode upper reverse base32 | codext decode base32 reverse lower",
        "echo -en \"test\" | codext encode upper reverse base32 base64 morse",
        "echo -en \"test\" | codext encode base64 gzip | codext guess",
        "echo -en \"test\" | codext encode base64 gzip | codext guess gzip",
    ])
    parser = argparse.ArgumentParser(description=descr, epilog=examples, formatter_class=argparse.RawTextHelpFormatter)
    sparsers = parser.add_subparsers(dest="command", help="command to be executed")
    parser.add_argument("-i", "--input-file", dest="infile", help="input file (if none, take stdin as input)")
    parser.add_argument("-o", "--output-file", dest="outfile", help="output file (if none, display result to stdout)")
    parser.add_argument("-s", "--strip-newlines", action="store_true", dest="strip", help="strip newlines from input")
    encode = sparsers.add_parser("encode", help="encode input using the specified codecs")
    encode.add_argument("encoding", nargs="+", help="list of encodings to apply")
    encode.add_argument("-e", "--errors", default="strict", choices=["ignore", "leave", "replace", "strict"],
                        help="error handling")
    decode = sparsers.add_parser("decode", help="decode input using the specified codecs")
    decode.add_argument("encoding", nargs="+", help="list of encodings to apply")
    decode.add_argument("-e", "--errors", default="strict", choices=["ignore", "leave", "replace", "strict"],
                        help="error handling")
    guess = sparsers.add_parser("guess", help="try guessing the decoding codecs")
    guess.add_argument("encoding", nargs="*", help="list of known encodings to apply")
    guess.add_argument("-c", "--category", choices=list_categories(), nargs="*", help="codec categories to search in")
    guess.add_argument("-d", "--depth", default=3, type=int, help="maximum codec search depth")
    search = sparsers.add_parser("search", help="search for codecs")
    search.add_argument("pattern", nargs="+", help="encoding pattern to search")
    args = parser.parse_args()
    # if a search pattern is given, only handle it
    if args.command == "search":
        results = []
        for enc in args.pattern:
            results.extend(codecs.search(enc))
        print(", ".join(results) or "No encoding found")
        return
    # handle input file or stdin
    if args.infile:
        with open(args.infile, 'rb') as f:
            c = f.read()
    else:
        c = b("")
        for line in __stdin_pipe():
            c += line
    if args.strip:
        c = re.sub(r"\r?\n", "", c)
    if args.command in ["decode", "encode"]:
        # encode or decode
        for encoding in args.encoding:
            c = getattr(codecs, ["encode", "decode"][args.command == "decode"])(c, encoding, args.errors)
    elif args.command == "guess":
        c, e = codecs.guess(c, max_depth=args.depth, codec_categories=args.category, found=args.encoding)
        if e:
            print("Encodings: %s" % ", ".join(e))
    # handle output file or stdout
    if args.outfile:
        with open(args.outfile, 'wb') as f:
            f.write(c)
    else:
        print(ensure_str(c), end="")

