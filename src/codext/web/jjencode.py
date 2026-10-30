# -*- coding: UTF-8 -*-
"""JJEncode Codec - jjencode content encoding.

JJEncode, created by Yosuke Hasegawa, converts JavaScript code into a JavaScript program only made of symbols ("$", "_",
 "+", "!", ...) and of the name of a global variable ("$" by default), that runs the code. The program fills the
 variable with an object whose properties hold the hexadecimal digits and some letters taken from the string
 representations of JavaScript values (e.g. "false" or "[object Object]"), gets the Function constructor through
 "(0)['constructor']['constructor']" and calls it on a string literal holding the code. Some punctuation characters are
 kept as is, the hexadecimal digits and the letters "l", "o", "t" and "u" are taken from the properties and the other
 characters are written as octal ("\\NNN") or Unicode ("\\uXXXX") escape sequences of their UTF-16 code units.

Encoding gives the same program as the reference encoder, except for two cases where the reference encoder gives a wrong
 program: the Unicode escape sequences of the characters below U+1000 are padded to four hexadecimal digits, and the
 octal escape sequences that would absorb a following digit are padded to three digits. Decoding parses the program
 (without running it), whatever the name of the variable, and returns the code. Malformed programs are reported
 whatever the errors handling.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://utf-8.jp/public/jjencode.html
"""
from ._javascript import *
from ..__common__ import *


__examples__ = {
    'enc(jjencode|jj_encode)': {
        'alert(1)': "$=~[];$={___:++$,$$$$:(![]+\"\")[$],__$:++$,$_$_:(![]+\"\")[$],_$_:++$,$_$$:({}+\"\")[$],$$_$:($[$"
                    "]+\"\")[$],_$$:++$,$$$_:(!\"\"+\"\")[$],$__:++$,$_$:++$,$$__:({}+\"\")[$],$$_:++$,$$$:++$,$___:++$"
                    ",$__$:++$};$.$_=($.$_=$+\"\")[$.$_$]+($._$=$.$_[$.__$])+($.$$=($.$+\"\")[$.__$])+((!$)+\"\")[$._$$"
                    "]+($.__=$.$_[$.$$_])+($.$=(!\"\"+\"\")[$.__$])+($._=(!\"\"+\"\")[$._$_])+$.$_[$.$_$]+$.__+$._$+$.$"
                    ";$.$$=$.$+(!\"\"+\"\")[$._$$]+$.__+$._+$.$+$.$$;$.$=($.___)[$.$_][$.$_];$.$($.$($.$$+\"\\\"\"+$.$_"
                    "$_+(![]+\"\")[$._$_]+$.$$$_+\"\\\\\"+$.__$+$.$$_+$._$_+$.__+\"(\"+$.__$+\")\"+\"\\\"\")())();",
    },
    'enc(jjencode-_)': {
        '': "_=~[];_={___:++_,$$$$:(![]+\"\")[_],__$:++_,$_$_:(![]+\"\")[_],_$_:++_,$_$$:({}+\"\")[_],$$_$:(_[_]+\"\")"
            "[_],_$$:++_,$$$_:(!\"\"+\"\")[_],$__:++_,$_$:++_,$$__:({}+\"\")[_],$$_:++_,$$$:++_,$___:++_,$__$:++_};"
            "_.$_=(_.$_=_+\"\")[_.$_$]+(_._$=_.$_[_.__$])+(_.$$=(_.$+\"\")[_.__$])+((!_)+\"\")[_._$$]+"
            "(_.__=_.$_[_.$$_])+(_.$=(!\"\"+\"\")[_.__$])+(_._=(!\"\"+\"\")[_._$_])+_.$_[_.$_$]+_.__+_._$+_.$;"
            "_.$$=_.$+(!\"\"+\"\")[_._$$]+_.__+_._+_.$+_.$$;_.$=(_.___)[_.$_][_.$_];_.$(_.$(_.$$+\"\\\"\"+\"\\\"\")())();",
    },
    'enc-dec(jjencode|jjencode-_|jjencode-x$1)': ["", "alert(\"Hello, World!\")", "@random{256}",
                                                  "caf\xe9 \u20ac \U0001f600", "\x00\x01\n\\\"'",
                                                  "\x01" + "2" * 3 + " 1 \x1f7"],
    'dec(jjencode)': {'': None, 'alert(1)': None},
}


DIGITS = ["___", "__$", "_$_", "_$$", "$__", "$_$", "$$_", "$$$", "$___", "$__$", "$_$_", "$_$$", "$$__", "$$_$",
          "$$$_", "$$$$"]
LETTERS = {'l': "(![]+\"\")[{v}._$_]", 'o': "{v}._$", 't': "{v}.__", 'u': "{v}._"}
PROLOGUE = "{v}=~[];{v}={{___:++{v},$$$$:(![]+\"\")[{v}],__$:++{v},$_$_:(![]+\"\")[{v}],_$_:++{v},$_$$:({{}}+\"\")" \
           "[{v}],$$_$:({v}[{v}]+\"\")[{v}],_$$:++{v},$$$_:(!\"\"+\"\")[{v}],$__:++{v},$_$:++{v},$$__:({{}}+\"\")" \
           "[{v}],$$_:++{v},$$$:++{v},$___:++{v},$__$:++{v}}};{v}.$_=({v}.$_={v}+\"\")[{v}.$_$]+({v}._$={v}.$_" \
           "[{v}.__$])+({v}.$$=({v}.$+\"\")[{v}.__$])+((!{v})+\"\")[{v}._$$]+({v}.__={v}.$_[{v}.$$_])+({v}.$=(!\"\"" \
           "+\"\")[{v}.__$])+({v}._=(!\"\"+\"\")[{v}._$_])+{v}.$_[{v}.$_$]+{v}.__+{v}._$+{v}.$;{v}.$$={v}.$+(!\"\"+" \
           "\"\")[{v}._$$]+{v}.__+{v}._+{v}.$+{v}.$$;{v}.$=({v}.___)[{v}.$_][{v}.$_];"
# $.$($.$($.$$+"\""+<escaped code>+"\"")())(), that is, Function(Function("return\"" + <escaped code> + "\"")())()
START, END = "{v}.$({v}.$({v}.$$+\"\\\"\"+", "\"\\\"\")())();"
PUNCTUATION = "".join(map(chr, [*range(0x21, 0x30), *range(0x3a, 0x41), *range(0x5b, 0x61), *range(0x7b, 0x80)]))
_VAR = r"[A-Za-z_$][A-Za-z0-9_$]*"


def _err(msg):
    raise JjencodeDecodeError(f"'jjencode' codec can't decode: {msg}")


def jjencode_encode(var=""):
    def encode(text, errors="strict"):
        v, r, s = var or "$", "", ""
        units = utf16_units(ensure_str(text))
        # pending literal characters, closed with "+" before a term
        lit = lambda close=True: [f"\"{s}\"" + "+" * close, ""][s == ""]
        for i, n in enumerate(units):
            c = chr(n)
            if c in "\"\\":
                s += "\\\\\\" + c
            elif c in PUNCTUATION:
                s += c
            elif c in "0123456789abcdef":
                r, s = r + lit() + f"{v}.{DIGITS[int(c, 16)]}+", ""
            elif c in LETTERS:
                r, s = r + lit() + LETTERS[c].format(v=v) + "+", ""
            else:
                if n < 128:
                    d, terms = f"{n:o}", []
                    # unlike the reference encoder, pad the octal escape sequence when it would absorb the next
                    #  character (e.g. "\1" followed by "2" would give "\12")
                    if i + 1 < len(units) and chr(units[i+1]) in "01234567" and (len(d) == 1 or d[0] in "0123"):
                        d = d.zfill(3)
                else:
                    # unlike the reference encoder, pad the hexadecimal digits of the Unicode escape sequence
                    d, terms = f"{n:04x}", [LETTERS['u'].format(v=v)]
                terms += [f"{v}.{DIGITS[int(x, 16)]}" for x in d]
                r, s = r + "\"" + s + "\\\\\"+" + "".join(t + "+" for t in terms), ""
        r += lit()
        return PROLOGUE.format(v=v) + START.format(v=v) + r + END, len(text)
    return encode


def jjencode_decode(var=""):
    def decode(text, errors="strict"):
        p = re.sub(r"\s+", "", ensure_str(text))
        # the name of the variable is read from the program
        if (m := re.match(rf"({_VAR})=~\[\];", p)) is None:
            _err("variable initialization not found")
        v = m.group(1)
        start, end = START.format(v=v), END
        if (i := p.find(start)) < 0:
            _err("payload not found")
        p = p[i+len(start):]
        if not p.endswith(end) and not p.endswith(end[:-1]):
            _err("end of payload not found")
        p = p[:-len(end) + (not p.endswith(end))]
        tokens = {f"{v}.{d}": "0123456789abcdef"[i] for i, d in enumerate(DIGITS)}
        tokens.update({t.format(v=v): c for c, t in LETTERS.items()})
        token = re.compile(r"\"((?:[^\"\\]|\\.)*)\"|" + "|".join(map(re.escape, sorted(tokens, key=len, reverse=True))),
                           re.S)
        # the payload is the source of a string literal, made of terms each followed by "+"
        body, i = "", 0
        while i < len(p):
            if (m := token.match(p, i)) is None or not p.startswith("+", m.end()):
                _err(f"unexpected token at position {i} of the payload")
            body += tokens[m.group()] if m.group(1) is None else js_unescape(m.group(1), _err)
            i = m.end() + 1
        return (r := js_unescape(body, _err)), len(r)
    return decode


add("jjencode", jjencode_encode, jjencode_decode, rf"^jj[-_]?encode(?:[-_]({_VAR}))?$", printables_rate=1.,
    expansion_factor=None)
