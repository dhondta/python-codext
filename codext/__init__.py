# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from __future__ import print_function
from six import b, binary_type, text_type

from .__common__ import *
from .__info__ import __author__, __copyright__, __email__, __license__, __source__, __version__


__all__ = ["add", "add_map", "clear", "decode", "encode", "lookup",  "open", "register", "remove", "reset"]

decode   = codecs.decode
encode   = codecs.encode
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
        "codext --search bitcoin",
        "codext -d base32 -i file.b32",
        "codext morse < to_be_encoded.txt",
        "echo \"test\" | codext base100",
        "echo -en \"test\" | codext braille -o test.braille",
        "codext base64 < to_be_encoded.txt > text.b64",
        "echo -en \"test\" | codext base64 | codext base32",
        "echo -en \"mrdvm6teie6t2cq=\" | codext upper | codext -d base32 | codext -d base64",
        "echo -en \"test\" | codext upper reverse base32 | codext -d base32 reverse lower",
        "echo -en \"test\" | codext upper reverse base32 base64 morse",
    ])
    parser = argparse.ArgumentParser(description=descr, epilog=examples, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("encoding", nargs="+", help="list of encodings to apply")
    parser.add_argument("-d", "--decode", action="store_true", help="set decode mode")
    parser.add_argument("-e", "--errors", default="strict", choices=["ignore", "leave", "replace", "strict"],
                        help="error handling")
    parser.add_argument("-i", "--input-file", dest="infile", help="input file (if none, take stdin as input)")
    parser.add_argument("-o", "--output-file", dest="outfile", help="output file (if none, display result to stdout)")
    parser.add_argument("-s", "--strip-newlines", action="store_true", dest="strip", help="strip newlines from input")
    parser.add_argument("--search", action="store_true", help="search for encoding names")
    args = parser.parse_args()
    # if a search pattern is given, only handle it
    if args.search:
        results = []
        for enc in args.encoding:
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
    # encode or decode
    for encoding in args.encoding:
        c = getattr(codecs, ["encode", "decode"][args.decode])(c, encoding, args.errors)
    # handle output file or stdout
    if args.outfile:
        with open(args.outfile, 'wb') as f:
            f.write(c)
    else:
        if PY3:
            try:
                c = c.decode("utf-8")
            except:
                c = c.decode("latin-1")
        print(c, end="")

