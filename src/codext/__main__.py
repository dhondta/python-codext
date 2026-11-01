# -*- coding: UTF-8 -*-
"""Codecs extension module - command-line tool.

"""
import argparse
import sys
from difflib import get_close_matches
from encodings import normalize_encoding
from encodings.aliases import aliases
from getpass import getpass
from importlib import import_module

from . import __common__
from .__common__ import *
from .__common__ import PERS_MACROS_FILE
from .compose import QUESTIONS, report as compose_report
from .guess import stopfunc
from .__info__ import __author__, __copyright__, __email__, __license__, __source__, __version__


def __format_list(items, include=True):
    if items is None:
        return
    d = {-1: list_encodings() if include else []}
    for n, i in enumerate(items):
        try:
            depth, i = i.split(":")
            depth = int(depth.strip().replace("~", "-"))
            if depth < 0:
                depth = -1
        except ValueError:
            if n == 0:
                d[-1] = []
            depth = -1
        d.setdefault(depth, [])
        d[depth].append(i.strip())
    return d


def __is_binary(data):
    """ Bytes are binary data if they are neither valid UTF-8 nor latin-1 text (as returned by text codecs). """
    try:
        data.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return any(b < 32 and b not in b"\t\n\r" or 127 <= b < 160 for b in data)


def __print_tabular(lst, space=4):
    try:
        cols, _ = os.get_terminal_size()
        # first, convert the list to a table that fits into the terminal
        i, line, w = 0, "", []
        while i < len(lst):
            x = lst[i]
            l = len(x)
            col = "%-{}s".format(l + space) % x
            i += 1
            w.append(l)
            if len(line) + len(col) > cols:
                break
            line += col
        while True:
            t = [lst[j:j+i] for j in range(0, len(lst), i)]
            w = [max(0 if j+k*i >= len(lst) else len(lst[j+k*i]) for k in range(len(t))) for j, _ in enumerate(w)]
            if sum(w) + space * len(w) >= cols:
                i -= 1
                w.pop()
            else:
                break
        print("\n".join("".join("%-{}s".format(w[n] + space) % x for n, x in enumerate(r)) for r in t) + "\n")
    except (AttributeError, OSError):
        print(", ".join(lst) + "\n")


def __ask(question, given=None):
    """ Ask an assessment question of the compose feature on the terminal, unless it was answered with an option. """
    if given is not None:
        return given
    if question['choices'] is None:
        # free answer, here the secret key (hence not echoed)
        return getpass(f"[?] {question['question']} ").strip()
    choices = list(question['choices'].items())
    print(f"[?] {question['question']}", file=sys.stderr)
    for i, (value, descr) in enumerate(choices, 1):
        print(f"    {i}) {descr}{['', ' (default)'][value == question['default']]}", file=sys.stderr)
    while True:
        a = input("    > ").strip()
        if a == "":
            return question['default']
        if a.isdigit() and 1 <= int(a) <= len(choices):
            return choices[int(a) - 1][0]
        if a in question['choices']:
            return a
        print(f"    please answer with a number from 1 to {len(choices)}", file=sys.stderr)


def __show(name):
    """ Describe a codec, an encoding or a macro: its name, its category, its module and the docstring of this module,
         which documents the codec ; a macro is described by its chain of encodings. """
    ci = lookup(name)
    if isinstance(ci, CodecMacro):
        pers = name in __common__.PERS_MACROS
        chain = (__common__.PERS_MACROS if pers else __common__.MACROS)[name]
        return f"macro    : {name} ({f'personal, in {PERS_MACROS_FILE}' if pers else 'embedded'})\n" \
               f"chain    : {' · '.join(chain)}"
    p = ci.parameters
    codec, cat, module = p.get('name', ci.name), p.get('category'), p.get('module')
    # the native codecs are documented by their module from the encodings package (e.g. encodings.cp500)
    if cat == "native":
        n = normalize_encoding(ci.name).lower()
        module = f"encodings.{aliases.get(n, n)}"
    try:
        doc = (import_module(module).__doc__ or "").strip()
    except (ImportError, TypeError, ValueError):
        doc = ""
    lines = [f"codec    : {codec} ({cat})"] + ([f"encoding : {name}"] if name != codec else []) + \
            [f"module   : {module}", "", doc or "No description available."]
    return "\n".join(lines)


def main():
    class _CustomFormatter(argparse.RawTextHelpFormatter):
        def __init__(self, prog, **kwargs):
            kwargs['max_help_position'] = 32
            super(_CustomFormatter, self).__init__(prog, **kwargs)
        
        def _format_action_invocation(self, action):
            if not action.option_strings:
                metavar, = self._metavar_formatter(action, action.dest)(1)
                return metavar
            else:
                return ", ".join(action.option_strings)
    
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
        "echo -en \"test\" | codext encode base64 gzip | codext guess gzip -c base",
        "codext compose",
        "codext compose -a alphanumeric -l 4 -k mysecret -m mychain -n",
        "codext show rle",
        "codext show base64-url rot-13 example-macro",
    ])
    kw = {'formatter_class': _CustomFormatter}
    parser = argparse.ArgumentParser(prog="codext", description=descr, epilog=examples, **kw)
    sparsers = parser.add_subparsers(dest="command", help="command to be executed", required=True)
    parser.add_argument("-i", "--input-file", dest="infile", help="input file (if none, take stdin as input)")
    parser.add_argument("-o", "--output-file", dest="outfile", help="output file (if none, display result to stdout)")
    parser.add_argument("-s", "--strip-newlines", action="store_true", dest="strip",
                        help="strip newlines from input (default: False)")
    encode = sparsers.add_parser("encode", help="encode input using the specified codecs", **kw)
    encode.add_argument("encoding", nargs="+", help="list of encodings to apply")
    encode.add_argument("-e", "--errors", default="strict", choices=["ignore", "leave", "replace", "strict"],
                        help="error handling (default: strict)")
    decode = sparsers.add_parser("decode", help="decode input using the specified codecs", **kw)
    decode.add_argument("encoding", nargs="+", help="list of encodings to apply")
    decode.add_argument("-e", "--errors", default="strict", choices=["ignore", "leave", "replace", "strict"],
                        help="error handling (default: strict)")
    guess = sparsers.add_parser("guess", help="try guessing the decoding codecs", **kw)
    guess.add_argument("encoding", nargs="*", help="list of known encodings to apply (default: none)")
    guess.add_argument("-b", "--beam", type=int, metavar="INT",
                       help="number of best-ranked decodings kept per candidate for the next depth (default: all)")
    guess.add_argument("-e", "--exclude", nargs="*", action="extend", metavar="CAT|COD|ENC",
                       help="categories, codecs and encodings to be explicitely not used ;\n "
                            "format: [category|codec|encoding] OR depth:[category|codec|encoding]")
    guess.add_argument("-E", "--extended", action="store_true",
                       help="while using the scoring heuristic, also consider null scores (default: False)")
    lng = "lang_%s" % LANG
    def_func = lng if getattr(stopfunc, lng, None) else "text"
    guess.add_argument("-f", "--stop-function", default=def_func, metavar="FUNC", help="result checking function "
                       "(default: %s) ; format: printables|text|text_strict|flag|lang_[bigram]|[regex]\nNB: [regex] "
                       "is case-sensitive ; add -i to force it as case-insensitive or add '(?i)' in front of the "
                       "expression"
                       % def_func)
    guess.add_argument("-H", "--no-heuristic", action="store_true", help="DO NOT use the scoring heuristic ; slows down"
                       " the search but may be more accurate (default: False)")
    guess.add_argument("-i", "--include", nargs="*", action="extend", metavar="CAT|COD|ENC",
                       help="categories, codecs and encodings to be explicitely used ;\n "
                            "format: [category|codec|encoding] OR depth:[category|codec|encoding]")
    guess.add_argument("-I", "--case-insensitive", dest="icase", action="store_true",
                       help="while using the regex stop function, set it as case-insensitive (default: False)")
    if len(stopfunc.LANG_BACKENDS) > 0:
        _lb = stopfunc.LANG_BACKEND
        guess.add_argument("-l", "--lang-backend", default=_lb, choices=stopfunc.LANG_BACKENDS + ["none"],
                           help="natural language detection backend (default: %s)" % _lb)
    guess.add_argument("-m", "--min-depth", default=0, type=int, metavar="INT",
                       help="minimum codec search depth before triggering results (default: 0)")
    guess.add_argument("-M", "--max-depth", default=5, type=int, metavar="INT",
                       help="maximum codec search depth (default: 5)")
    guess.add_argument("-n", "--max-nodes", type=int, metavar="INT",
                       help="maximum number of candidates to be decoded with every encoding (default: no limit)")
    guess.add_argument("-s", "--do-not-stop", action="store_true",
                       help="do not stop if a valid output is found (default: False)")
    guess.add_argument("-t", "--timeout", type=float, metavar="SECONDS",
                       help="maximum duration of the search, then returning the results found so far (default: no "
                            "limit)")
    guess.add_argument("-v", "--verbose", action="store_true",
                       help="show guessing information and steps (default: False)")
    rank = sparsers.add_parser("rank", help="rank the most probable encodings based on the given input", **kw)
    rank.add_argument("-e", "--exclude", nargs="*", action="extend", metavar="CAT|COD|ENC",
                      help="categories, codecs and encodings to be explicitely not used ;\n "
                           "format: [category|codec|encoding] OR depth:[category|codec|encoding]")
    rank.add_argument("-E", "--extended", action="store_true",
                      help="while using the scoring heuristic, also consider null scores (default: False)")
    rank.add_argument("-i", "--include", nargs="*", action="extend", metavar="CAT|COD|ENC",
                      help="categories, codecs and encodings to be explicitely used ;\n "
                           "format: [category|codec|encoding] OR depth:[category|codec|encoding]")
    rank.add_argument("-l", "--limit", type=int, default=10, help="limit the number of displayed results")
    strength = sparsers.add_parser("strength", help="evaluate the strength of a chain of codecs", **kw)
    strength.add_argument("encoding", nargs="+", help="list of encodings forming the chain to evaluate")
    strength.add_argument("-e", "--exclude", nargs="*", action="extend", metavar="CAT|COD|ENC",
                          help="categories, codecs and encodings the guessing adversary may not use")
    strength.add_argument("-f", "--stop-function", default="text", metavar="FUNC",
                          help="stop function for the guessing adversary (default: text)")
    strength.add_argument("-i", "--include", nargs="*", action="extend", metavar="CAT|COD|ENC",
                          help="categories, codecs and encodings the guessing adversary may use")
    compose = sparsers.add_parser("compose", help="compose a strong chain of codecs from a few assessment questions",
                                  **kw)
    compose.add_argument("-a", "--alphabet", choices=list(QUESTIONS[1]['choices']),
                         help="characters the encoded output may contain (default: printable)")
    compose.add_argument("-b", "--binary", action="store_const", const="binary", dest="input",
                         help="the input is any data (bytes) rather than text (default: text)")
    compose.add_argument("-d", "--disguise", action="store_const", const="yes",
                         help="the output shall look like text rather than encoded data (default: no)")
    compose.add_argument("-e", "--exclude", nargs="*", action="extend", metavar="CAT|COD|ENC",
                         help="categories, codecs and encodings not to be used in the chain")
    compose.add_argument("-i", "--include", nargs="*", action="extend", metavar="CAT|COD|ENC",
                         help="categories, codecs and encodings that may be used in the chain (default: all but the "
                              "lossy ones)")
    compose.add_argument("-k", "--key",
                         help="secret key for a keyed layer, needed to decode (letters only, at least 4)")
    compose.add_argument("-l", "--layers", choices=list(QUESTIONS[3]['choices']),
                         help="number of layers (default: 3)")
    compose.add_argument("-m", "--macro", metavar="NAME", help="save the chain as a macro with the given name")
    compose.add_argument("-n", "--non-interactive", action="store_true",
                         help="do not ask the questions, using the default answers for the options not given")
    compose.add_argument("-s", "--seed", type=int, help="seed for drawing the chain (default: random)")
    compose.add_argument("-x", "--expansion", choices=list(QUESTIONS[2]['choices']),
                         help="how many times larger than the input the output may be (default: 5)")
    show = sparsers.add_parser("show", help="show the documentation of codecs, encodings or macros")
    show.add_argument("encoding", nargs="+", help="names of codecs, encodings or macros")
    search = sparsers.add_parser("search", help="search for codecs")
    search.add_argument("pattern", nargs="+", help="encoding pattern to search")
    listi = sparsers.add_parser("list", help="list items")
    lsparsers = listi.add_subparsers(dest="type", help="type of item to be listed", required=True)
    liste = lsparsers.add_parser("encodings", help="list encodings")
    liste.add_argument("category", nargs="*", help="selected categories")
    listm = lsparsers.add_parser("macros", help="list macros")
    addm = sparsers.add_parser("add-macro", help="add a macro to the registry")
    addm.add_argument("name", help="macro's name")
    addm.add_argument("encoding", nargs="+", help="list of encodings to chain")
    remm = sparsers.add_parser("remove-macro", help="remove a macro from the registry")
    remm.add_argument("name", help="macro's name")
    args = parser.parse_args()
    if args.command in ["guess", "rank", "strength"]:
        args.include, args.exclude = __format_list(args.include), __format_list(args.exclude, False)
    try:
        # if a search pattern is given, only handle it
        if args.command == "search":
            results = []
            for enc in args.pattern:
                results.extend(codecs.search(enc))
            print(", ".join(results) or "No encoding found")
            return 0
        # show the documentation of codecs, encodings or macros
        elif args.command == "show":
            status, out = 0, []
            for name in args.encoding:
                try:
                    out.append(__show(name))
                except LookupError as e:
                    status = 1
                    similar = get_close_matches(name, list_encodings() + list_macros(), 5, .7)
                    print(f"codext: {str(e)[0].lower()}{str(e)[1:]}" +
                          (f" (similar: {', '.join(similar)})" if similar else ""), file=sys.stderr)
            if out:
                print(("\n\n" + "-" * 80 + "\n\n").join(out))
            return status
        # add/remove macros (not requiring to input a file or text)
        elif args.command == "add-macro":
            add_macro(args.name, *args.encoding)
            return 0
        elif args.command == "remove-macro":
            remove_macro(args.name)
            return 0
        # evaluate the strength of a chain of codecs (sample from a file, from a pipe, or a default one)
        elif args.command == "strength":
            sample = None
            if args.infile:
                sample = _input(args.infile)
            elif not sys.stdin.isatty():
                sample = _input(None)
            if sample is not None:
                sample = (sample.rstrip("\r\n") if isinstance(sample, str) else sample.rstrip(b"\r\n")) or None
            print(codecs.strength_report(args.encoding, sample=sample,
                                         stop_func=getattr(stopfunc, args.stop_function, stopfunc.default),
                                         include=args.include, exclude=args.exclude))
            return 0
        # compose a chain of codecs from the answers to the assessment questions, given as options or asked on the
        #  terminal (a sample to be encoded may be given from a file or from a pipe, then not asking the questions)
        elif args.command == "compose":
            sample = None
            if args.infile:
                sample = _input(args.infile)
            elif not sys.stdin.isatty():
                sample, args.non_interactive = _input(None), True
            interactive = not args.non_interactive
            answers = {}
            for q in QUESTIONS:
                given = getattr(args, q['name'])
                if interactive:
                    given = __ask(q, given)
                if given is not None:
                    answers[q['name']] = given
            print("[*] Composing the chain (this may take a while)...", file=sys.stderr)
            try:
                r = codecs.compose(answers, sample=sample or None, include=args.include, exclude=args.exclude,
                                   seed=args.seed)
            except ValueError as e:
                print(f"codext: {e}", file=sys.stderr)
                return 1
            print(compose_report(r))
            if args.macro:
                add_macro(args.macro, *r['chain'])
                print(f"saved as macro '{args.macro}': codext encode {args.macro} / codext decode {args.macro}")
                if r['answers']['key']:
                    print(f"warning: the macro holds the secret key, in plain text in {PERS_MACROS_FILE}",
                          file=sys.stderr)
            return 0
        # list encodings or macros
        elif args.command == "list":
            if args.type == "encodings":
                if args.category:
                    for c in sorted(args.category):
                        if len(l := list_encodings(c)) > 0:
                            print(c.upper() + ":")
                            __print_tabular(l)
                else:
                    __print_tabular(list_encodings())
            elif args.type == "macros":
                l = list_macros()
                if len(l) > 0:
                    __print_tabular(l)
            return 0
        # handle input file or stdin
        c =_input(args.infile)
        c = c.rstrip("\r\n") if isinstance(c, str) else c.rstrip(b"\r\n")
        # strip any other (CR)LF
        if args.strip:
            c = re.sub(r"\r?\n", "", c) if isinstance(c, str) else c.replace(b"\r\n", b"").replace(b"\n", b"")
        if args.command in ["decode", "encode"]:
            # encode or decode
            for encoding in args.encoding:
                c = getattr(codecs, ["encode", "decode"][args.command == "decode"])(c, encoding, args.errors)
            # handle output file or stdout
            if args.outfile:
                with codecs.open(args.outfile, 'wb') as f:
                    f.write(c)
            elif isinstance(c, bytes) and __is_binary(c):
                # write binary data as is, as printing it would re-encode as UTF-8 the bytes that are not valid UTF-8
                sys.stdout.buffer.write(c)
                sys.stdout.flush()
            else:
                print(ensure_str(c or "Could not %scode :-(" % ["en", "de"][args.command == "decode"]), end="")
        elif args.command == "guess":
            s, lb = args.stop_function, getattr(args, "lang_backend", "none")
            if re.match(r"lang_[a-z]{2}$", s) and lb != "none" and \
               all(re.match(r"lang_[a-z]{2}$", x) is None for x in dir(stopfunc)):
                stopfunc._reload_lang(lb)
            r = codecs.guess(c,
                             getattr(stopfunc, s, ["", "(?i)"][args.icase] + s), args.min_depth, args.max_depth,
                             args.include, args.exclude, args.encoding, not args.do_not_stop, True,  # show
                             not args.no_heuristic, args.extended, args.verbose, args.timeout, args.max_nodes,
                             args.beam)
            for i, o in enumerate(r.items()):
                e, out = o
                if len(e) > 0:
                    if args.outfile:
                        n, ext = os.path.splitext(args.outfile)
                        fn = args.outfile if len(r) == 1 else "%s-%d%s" % (n, i+1, ext)
                    else:
                        print("Codecs: %s" % ", ".join(e))
                        print(ensure_str(out))
            if len(r) == 0:
                print("Could not decode :-(")
        elif args.command == "rank":
            for i, e in codecs.rank(c, args.extended, args.limit, args.include, args.exclude):
                s = "[+] %.5f: %s" % (i[0], e)
                print(s if len(s) <= 80 else s[:77] + "...")
    except Exception as e:
        raise e
        m = str(e)
        print("codext: " + m[0].lower() + m[1:])


if __name__ == "__main__":
    sys.exit(main())
