# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from .__common__ import *
from .__info__ import __author__, __copyright__, __email__, __license__, __source__, __version__


__all__ = ["add", "add_map", "clear", "decode", "encode", "guess", "lookup",  "open", "rank", "register", "remove",
           "reset"]

decode   = codecs.decode
encode   = codecs.encode
guess    = codecs.guess
lookup   = codecs.lookup
open     = codecs.open

_lst = list
list = list_encodings  # not included in __all__ because of shadow name


reset()


# populate codext with attributes from codecs that were not modified
for attr in codecs.__all__:
    if attr in __all__:
        continue
    locals()[attr] = getattr(codecs, attr)
    __all__.append(attr)


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


def main():
    import argparse, os

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
    ])
    kw = {'formatter_class': _CustomFormatter}
    parser = argparse.ArgumentParser(description=descr, epilog=examples, **kw)
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
    guess.add_argument("-e", "--exclude", nargs="*", action="extend", metavar="CAT|COD|ENC",
                       help="categories, codecs and encodings to be explicitely not used ;\n "
                            "format: [category|codec|encoding] OR depth:[category|codec|encoding]")
    guess.add_argument("-E", "--extended", action="store_true",
                       help="while using the scoring heuristic, also consider null scores (default: False)")
    lng = "lang_%s" % LANG
    def_func = lng if getattr(stopfunc, lng, None) else "text"
    guess.add_argument("-f", "--stop-function", default=def_func, metavar="FUNC", help="result checking function "
                       "(default: %s) ; format: printables|text|flag|lang_[bigram]|[regex]\nNB: [regex] is case-"
                       "sensitive ; add -i to force it as case-insensitive or add '(?i)' in front of the expression"
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
    guess.add_argument("-s", "--do-not-stop", action="store_true",
                       help="do not stop if a valid output is found (default: False)")
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
    search = sparsers.add_parser("search", help="search for codecs")
    search.add_argument("pattern", nargs="+", help="encoding pattern to search")
    listi = sparsers.add_parser("list", help="list items")
    lsparsers = listi.add_subparsers(dest="type", help="type of item to be listed", required=True)
    liste = lsparsers.add_parser("encodings", help="list encodings")
    liste.add_argument("category", nargs="+", help="selected categories")
    listm = lsparsers.add_parser("macros", help="list macros")
    addm = sparsers.add_parser("add-macro", help="add a macro to the registry")
    addm.add_argument("name", help="macro's name")
    addm.add_argument("encoding", nargs="+", help="list of encodings to chain")
    remm = sparsers.add_parser("remove-macro", help="remove a macro from the registry")
    remm.add_argument("name", help="macro's name")
    args = parser.parse_args()
    if args.command in ["guess", "rank"]:
        args.include, args.exclude = __format_list(args.include), __format_list(args.exclude, False)
    try:
        # if a search pattern is given, only handle it
        if args.command == "search":
            results = []
            for enc in args.pattern:
                results.extend(codecs.search(enc))
            print(", ".join(results) or "No encoding found")
            return 0
        # add/remove macros (not requiring to input a file or text)
        elif args.command == "add-macro":
            add_macro(args.name, *args.encoding)
            return 0
        elif args.command == "remove-macro":
            remove_macro(args.name)
            return 0
        # list encodings or macros
        elif args.command == "list":
            if args.type == "encodings":
                cats = args.category or list_categories()
                for c in sorted(cats):
                    l = list_encodings(c)
                    if len(l) > 0:
                        if len(cats) > 0:
                            print(c.upper() + ":")
                        __print_tabular(l)
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
                with open(args.outfile, 'wb') as f:
                    f.write(c)
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
                             not args.no_heuristic, args.extended, args.verbose)
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

