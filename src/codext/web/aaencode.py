# -*- coding: UTF-8 -*-
"""AAEncode Codec - aaencode content encoding.

AAEncode, created by Yosuke Hasegawa, converts JavaScript code into a JavaScript program made of Japanese-style
 emoticons ("kaomoji", e.g. "ﾟωﾟﾉ" or "(ﾟДﾟ)") that runs the code. The program builds the digits and the letters it
 needs from the string representations of JavaScript values (e.g. "false" or "undefined"), gets the Function constructor
 through "(3).constructor.constructor" and calls it on a string literal holding the code, each character being written
 as an octal ("\\NNN") or Unicode ("\\uXXXX") escape sequence of its UTF-16 code unit.

Encoding gives the same program as the reference encoder. Decoding parses the program (without running it), whatever its
 whitespaces, and returns the code. Malformed programs are reported whatever the errors handling.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://utf-8.jp/public/aaencode.html
"""
from ._javascript import *
from ..__common__ import *


__examples__ = {
    'enc(aaencode|aa_encode)': {
        'alert(1)': "ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); (ﾟДﾟ) =(ﾟΘﾟ)= (o^_^o)/ (o"
                    "^_^o);(ﾟДﾟ)={ﾟΘﾟ: '_' ,ﾟωﾟﾉ : ((ﾟωﾟﾉ==3) +'_') [ﾟΘﾟ] ,ﾟｰﾟﾉ :(ﾟωﾟﾉ+ '_')[o^_^o -(ﾟΘﾟ)] ,ﾟДﾟﾉ:((ﾟｰﾟ="
                    "=3) +'_')[ﾟｰﾟ] }; (ﾟДﾟ) [ﾟΘﾟ] =((ﾟωﾟﾉ==3) +'_') [c^_^o];(ﾟДﾟ) ['c'] = ((ﾟДﾟ)+'_') [ (ﾟｰﾟ)+(ﾟｰﾟ)-(ﾟ"
                    "Θﾟ) ];(ﾟДﾟ) ['o'] = ((ﾟДﾟ)+'_') [ﾟΘﾟ];(ﾟoﾟ)=(ﾟДﾟ) ['c']+(ﾟДﾟ) ['o']+(ﾟωﾟﾉ +'_')[ﾟΘﾟ]+ ((ﾟωﾟﾉ==3) +"
                    "'_') [ﾟｰﾟ] + ((ﾟДﾟ) +'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ ((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [(ﾟｰﾟ) - (ﾟΘﾟ)]+(ﾟД"
                    "ﾟ) ['c']+((ﾟДﾟ)+'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ (ﾟДﾟ) ['o']+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ];(ﾟДﾟ) ['_'] =(o^_^o) [ﾟoﾟ] ["
                    "ﾟoﾟ];(ﾟεﾟ)=((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟДﾟ) .ﾟДﾟﾉ+((ﾟДﾟ)+'_') [(ﾟｰﾟ) + (ﾟｰﾟ)]+((ﾟｰﾟ==3) +'_') [o^_^o -"
                    "ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟωﾟﾉ +'_') [ﾟΘﾟ]; (ﾟｰﾟ)+=(ﾟΘﾟ); (ﾟДﾟ)[ﾟεﾟ]='\\\\'; (ﾟДﾟ).ﾟΘﾟﾉ=(ﾟДﾟ+ ﾟ"
                    "ｰﾟ)[o^_^o -(ﾟΘﾟ)];(oﾟｰﾟo)=(ﾟωﾟﾉ +'_')[c^_^o];(ﾟДﾟ) [ﾟoﾟ]='\\\"';(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (ﾟεﾟ+(ﾟД"
                    "ﾟ)[ﾟoﾟ]+ (ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ)+ (ﾟｰﾟ)+ (ﾟΘﾟ)+ (ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ (ﾟｰﾟ)+ (ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ"
                    ")+ (ﾟｰﾟ)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ (ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ)+ ((o^_^o) +(o^_^o))+ ((o^_^o) - (ﾟΘﾟ))+ (ﾟДﾟ)[ﾟεﾟ]+(ﾟΘ"
                    "ﾟ)+ ((o^_^o) +(o^_^o))+ (ﾟｰﾟ)+ (ﾟДﾟ)[ﾟεﾟ]+((ﾟｰﾟ) + (ﾟΘﾟ))+ (c^_^o)+ (ﾟДﾟ)[ﾟεﾟ]+((o^_^o) +(o^_^o))+"
                    " (ﾟΘﾟ)+ (ﾟДﾟ)[ﾟεﾟ]+((ﾟｰﾟ) + (ﾟΘﾟ))+ (ﾟΘﾟ)+ (ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');",
    },
    'enc-dec(aaencode)': ["", "alert(\"Hello, World!\")", "@random{256}", "caf\xe9 \u20ac \U0001f600",
                          "\x00\x01\n\\\"'"],
    'dec(aaencode)': {'': None, 'alert(1)': None},
}


DIGITS = ["(c^_^o)", "(ﾟΘﾟ)", "((o^_^o) - (ﾟΘﾟ))", "(o^_^o)", "(ﾟｰﾟ)", "((ﾟｰﾟ) + (ﾟΘﾟ))", "((o^_^o) +(o^_^o))",
          "((ﾟｰﾟ) + (o^_^o))", "((ﾟｰﾟ) + (ﾟｰﾟ))", "((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "(ﾟДﾟ) .ﾟωﾟﾉ", "(ﾟДﾟ) .ﾟΘﾟﾉ",
          "(ﾟДﾟ) ['c']", "(ﾟДﾟ) .ﾟｰﾟﾉ", "(ﾟДﾟ) .ﾟДﾟﾉ", "(ﾟДﾟ) [ﾟΘﾟ]"]
HEADER = "ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); "
# easter egg of the reference encoder
EASTER_EGG = (re.compile(r"ひだまりスケッチ×(365|３５６)\s*来週も見てくださいね[!！]"),
              "X=_=3; \r\n\r\n    X / _ / X < \"来週も見てくださいね!\";\r\n\r\n")
PROLOGUE = "(ﾟДﾟ) =(ﾟΘﾟ)= (o^_^o)/ (o^_^o);(ﾟДﾟ)={ﾟΘﾟ: '_' ,ﾟωﾟﾉ : ((ﾟωﾟﾉ==3) +'_') [ﾟΘﾟ] ,ﾟｰﾟﾉ :(ﾟωﾟﾉ+ '_')" \
           "[o^_^o -(ﾟΘﾟ)] ,ﾟДﾟﾉ:((ﾟｰﾟ==3) +'_')[ﾟｰﾟ] }; (ﾟДﾟ) [ﾟΘﾟ] =((ﾟωﾟﾉ==3) +'_') [c^_^o];(ﾟДﾟ) ['c'] = " \
           "((ﾟДﾟ)+'_') [ (ﾟｰﾟ)+(ﾟｰﾟ)-(ﾟΘﾟ) ];(ﾟДﾟ) ['o'] = ((ﾟДﾟ)+'_') [ﾟΘﾟ];(ﾟoﾟ)=(ﾟДﾟ) ['c']+(ﾟДﾟ) ['o']+" \
           "(ﾟωﾟﾉ +'_')[ﾟΘﾟ]+ ((ﾟωﾟﾉ==3) +'_') [ﾟｰﾟ] + ((ﾟДﾟ) +'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ ((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+" \
           "((ﾟｰﾟ==3) +'_') [(ﾟｰﾟ) - (ﾟΘﾟ)]+(ﾟДﾟ) ['c']+((ﾟДﾟ)+'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ (ﾟДﾟ) ['o']+" \
           "((ﾟｰﾟ==3) +'_') [ﾟΘﾟ];(ﾟДﾟ) ['_'] =(o^_^o) [ﾟoﾟ] [ﾟoﾟ];(ﾟεﾟ)=((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟДﾟ) .ﾟДﾟﾉ+" \
           "((ﾟДﾟ)+'_') [(ﾟｰﾟ) + (ﾟｰﾟ)]+((ﾟｰﾟ==3) +'_') [o^_^o -ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟωﾟﾉ +'_') [ﾟΘﾟ]; " \
           "(ﾟｰﾟ)+=(ﾟΘﾟ); (ﾟДﾟ)[ﾟεﾟ]='\\\\'; (ﾟДﾟ).ﾟΘﾟﾉ=(ﾟДﾟ+ ﾟｰﾟ)[o^_^o -(ﾟΘﾟ)];(oﾟｰﾟo)=(ﾟωﾟﾉ +'_')[c^_^o];" \
           "(ﾟДﾟ) [ﾟoﾟ]='\\\"';"
# Function(Function("return\"" + <escaped code> + "\"")(1))("_")
START = "(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (ﾟεﾟ+(ﾟДﾟ)[ﾟoﾟ]+ "
BACKSLASH, QUOTE, U = "(ﾟДﾟ)[ﾟεﾟ]+", "(ﾟДﾟ)[ﾟoﾟ]", "(oﾟｰﾟo)+ "
EPILOGUE = QUOTE + ") (ﾟΘﾟ)) ('_');"
# for decoding, whitespaces are removed from the program and from its tokens
_ws = lambda s: re.sub(r"\s+", "", s)
_START, _END = _ws(START), _ws(EPILOGUE).rstrip(";")
_TOKENS = {_ws(BACKSLASH): "\\", _ws(U): "u", **{_ws(d) + "+": "0123456789abcdef"[i] for i, d in enumerate(DIGITS)}}
_TOKEN = re.compile("|".join(map(re.escape, sorted(_TOKENS, key=len, reverse=True))))


def _err(msg):
    raise AaencodeDecodeError(f"'aaencode' codec can't decode: {msg}")


def aaencode_encode(text, errors="strict"):
    t = ensure_str(text)
    r = HEADER + [EASTER_EGG[1], ""][EASTER_EGG[0].search(t) is None] + PROLOGUE + START
    for n in utf16_units(t):
        r += BACKSLASH + ("".join(DIGITS[int(c)] + "+ " for c in f"{n:o}") if n <= 127 else
                          U + "".join(DIGITS[int(c, 16)] + "+ " for c in f"{n:04x}"))
    return r + EPILOGUE, len(text)


def aaencode_decode(text, errors="strict"):
    p = _ws(ensure_str(text))
    if (i := p.find(_START)) < 0:
        _err("payload not found")
    p = p[i+len(_START):].rstrip(";")
    if not p.endswith(_END):
        _err("end of payload not found")
    p, body, i = p[:-len(_END)], "", 0
    # the payload is the source of a string literal, made of backslashes, "u"'s and hexadecimal digits
    while i < len(p):
        if (m := _TOKEN.match(p, i)) is None:
            _err(f"unexpected token at position {i} of the payload")
        body, i = body + _TOKENS[m.group()], m.end()
    return (r := js_unescape(body, _err)), len(r)


add("aaencode", aaencode_encode, aaencode_decode, r"^aa[-_]?encode$", expansion_factor=None)
