# -*- coding: UTF-8 -*-
"""Utility functions and constants, independent of the codecs registry.

This module holds the conversion helpers (str/bytes, integers), the error handling helpers, the input helpers and the
 constants about the platform and the locale. It depends on no other module of codext, so that any of them can rely on
 it ; its public names are re-exported by ``__common__`` (hence available to the codecs through its star import).
"""
import builtins
import codecs
import re
import sys
from functools import wraps
from locale import getlocale
from platform import system
from string import ascii_lowercase, ascii_uppercase, digits, printable, punctuation


__all__ = ["b", "ensure_str", "exc_name", "fix_inout_formats", "get_alphabet_from_mask", "handle_error", "i2s", "isb",
           "iss", "maketrans", "s2i", "DARWIN", "LANG", "LINUX", "MASKS", "PRINTABLES", "UNIX", "WINDOWS"]

maketrans = str.maketrans
PRINTABLES = frozenset(printable)

LANG = getlocale()
if LANG:
    LANG = (LANG[0] or "")[:2].lower()
MASKS = {
    'a': printable,
    'b': "".join(chr(i) for i in range(256)),
    'd': digits,
    'h': digits + "abcdef",
    'H': digits + "ABCDEF",
    'l': ascii_lowercase,
    'p': punctuation,
    's': " ",
    'u': ascii_uppercase,
}

DARWIN = system() == "Darwin"
LINUX = system() == "Linux"
UNIX = DARWIN or LINUX
WINDOWS = system() == "Windows"


isb = lambda s: isinstance(s, bytes)
iss = lambda s: isinstance(s, str)
fix = lambda x, ref: b(x) if isb(ref) else ensure_str(x) if iss(ref) else x

s2i = lambda s: int(codecs.encode(s, "base16"), 16)
exc_name = lambda e: "".join(t.capitalize() for t in re.split(r"[-_+]", e))


def i2s(input):
    h = hex(input)[2:].rstrip("eL")
    return codecs.decode(h.zfill(len(h) + len(h) % 2), "hex")


# conversion functions
def b(s):
    """ Non-crashing bytes conversion function. """
    try:
        return s.encode("latin-1")
    except:
        pass
    try:
        return s.encode("utf-8")
    except:
        pass
    return s


def ensure_str(s, encoding="utf-8", errors='strict'):
    """ Dummy str conversion function. """
    if isinstance(s, bytes):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    return s


# make conversion functions compatible with input/output strings/bytes
def fix_inout_formats(f, inkind=None, outkind=None):
    """ This decorator ensures that the first output of f will have the same text format as the first input (str or
         bytes).
    
    The kinds of the input and output sides ("bytes" or "text") tell how a bytes input is passed to f and how the output
     of f is turned back into bytes:
    - a "bytes" side holds data, passed byte for byte (as a str of the characters 0 to 255, which b(...) turns back into
       the same bytes) ;
    - a "text" side holds characters, read from UTF-8 (or Latin-1 if not valid UTF-8) and written in UTF-8 ; if both
       sides are "text" and the input was not valid UTF-8, the output is written like the input was read, in Latin-1.
    Without kinds, the input is read as UTF-8 (or Latin-1) and the output written with b(...) (Latin-1 or UTF-8). """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        a0 = args[0]
        a0_isb, kinds, okind = isb(a0), inkind is not None and outkind is not None, outkind
        if a0_isb and kinds:
            if inkind == "bytes":
                a0 = a0.decode("latin-1")
            else:
                try:
                    a0 = a0.decode("utf-8")
                except UnicodeDecodeError:
                    a0 = a0.decode("latin-1")
                    # not UTF-8 text ; text-to-text codecs give it back in the form it was read
                    okind = "bytes"
        elif iss(a0) and kinds and inkind == "bytes" and any(ord(c) > 255 for c in a0):
            # a str on a bytes side is handled as its bytes form (b(...), hence UTF-8 when not in Latin-1)
            x = b(a0)
            a0 = x.decode("latin-1") if isb(x) else a0
        else:
            a0 = ensure_str(a0) if iss(a0) or a0_isb else a0
        r = f(a0, *args[1:], **kwargs)
        # special case: input is in bytes ; ensure that the returned length is this of the bytes, not this processed by
        #                the decode/encode function
        if isinstance(r, (tuple, list)) and isinstance(r[1], int) and a0_isb:
            r = tuple([list(r)[0]] + [len(args[0])] + list(r)[2:])
        _fix = (lambda x: _to_bytes(x, okind)) if a0_isb and kinds else (lambda x: fix(x, args[0]))
        return (_fix(r[0]), ) + tuple(r[1:]) if isinstance(r, (tuple, list)) else _fix(r)
    return _wrapper


def _to_bytes(x, kind):
    """ Write an output of the given kind as bytes: byte for byte for "bytes", in UTF-8 for "text". """
    if not iss(x):
        return x
    return b(x) if kind == "bytes" else x.encode("utf-8", "surrogatepass")


# alphabet generation function from a given mask
def get_alphabet_from_mask(mask):
    """ This function generates an alphabet from the given mask. The style used is similar to Hashcat ; group keys are
         marked with a heading "?". """
    i, alphabet = 0, ""
    while i < len(mask):
        c = mask[i]
        if c == "?" and i < len(mask) - 1 and mask[i+1] in MASKS.keys():
            for c in MASKS[mask[i+1]]:
                if c not in alphabet:
                    alphabet += c
            i += 1
        elif c not in alphabet:
            alphabet += c
        i += 1
    return alphabet


# generic error handling function
def handle_error(ename, errors, sep="", repl_char="?", repl_minlen=1, decode=False, kind="character", item="position"):
    """ This shortcut function allows to handle error modes given some tuning parameters.
    
    :param ename:       encoding name
    :param errors:      error handling mode
    :param sep:         token separator
    :param repl_char:   replacement character (for use when errors="replace")
    :param repl_minlen: repeat number for the replacement character
    :param decode:      whether we are encoding or decoding
    :param item:        position item description (for describing the error ; e.g. "group" or "token")
    """
    exc = f"{exc_name(ename)}{['En','De'][decode]}codeError"
     
    def _handle_error(token, position, output="", eename=None):
        """ This handles an encoding/decoding error according to the selected handling mode.
        
        :param token:    input token to be encoded/decoded
        :param position: token position index
        :param output:   output, as decoded up to the position of the error
        """
        if errors == "strict":
            token = f"{token[:7]}..." if len(token := ensure_str(token)) > 10 else token
            err = getattr(builtins, exc)(f"'{eename or ename}' codec can't {['en','de'][decode]}code {kind} '{token}' "
                                         f"in {item} {position}")
            err.output = output
            err.__cause__ = err
            raise err
        elif errors == "leave":
            return token + sep
        elif errors == "replace":
            return repl_char * repl_minlen + sep
        elif errors == "ignore":
            return ""
        else:
            raise ValueError(f"Unsupported error handling '{errors}'")
    return _handle_error


def __stdin_pipe():
    """ Stdin pipe read function. """
    try:
        with open(0, 'rb') as f:
            for l in f:
                yield l
    except TypeError:
        for l in sys.stdin:
            yield l


def _input(infile):
    # handle input file or stdin
    if infile:
        with open(infile, 'rb') as f:
            return f.read()
    return b("").join(__stdin_pipe())


def _set_exc(name, etype="ValueError"):
    if not hasattr(builtins, name):
        ns = {}
        exec(f"class {name}({etype}): __module__ = 'builtins'", {}, ns)
        setattr(builtins, name, ns[name])
_set_exc("InputSizeLimitError")
_set_exc("ParameterError")


def _stripl(s, st_lines, st_crlf):
    if st_crlf:
        s = s.replace(b"\r\n", b"") if isb(s) else s.replace("\r\n", "")
    if st_lines:
        s = s.replace(b"\n", b"") if isb(s) else s.replace("\n", "")
    return s


def _human_keys(text):
    """ Sorting function for considering strings with numbers (e.g. base2, base10, base100) """
    tokens = []
    for s in re.split(r"(\d+|\D+)", text):
        tokens.append(int(s) if s.isdigit() else s)
    return tokens

