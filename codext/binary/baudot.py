# -*- coding: UTF-8 -*-
"""Baudot Codec - baudot content conversion to HTML.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__CODES = ["ccitt1", "ccitt2", "eu", "ita1", "ita2", "ita2_us", "murray", "uk"]
if PY3:
    __CODES.extend(["ita2_meteo", "mtk2"])
__guess__     = ["baudot%s-{}-{}".format(x, y) for x in __CODES for y in ["lsb", "msb"]]
__examples1__ = {
    'enc(baudot-BAD_ALPHABET)': None,
    'enc(baudot_ccitt2_lsb)':   {'TEST 1234': "00001100001010000001001001101111101110011000001010"},
    'enc(baudot-ita1)':         {'TEST 1234': "10101000101010010101100000100000001000100010000101"},
    'enc(baudot_ita2_msb)':     {'TEST 1234': "10000000010010110000001001101110111100110000101010"},
    'enc(baudot-ita2-us)':      {'TEST 1234': "10000000010010110000001001101110111100110000101010"},
    'enc(baudot)':              {'\x01\x02':  None},
    'enc(baudot_ccitt1-lsb)':   {'TEST ':     None},
}
__examples2__ = {
    'enc(baudot_spaced-BAD_ALPHABET)': None,
    'enc(baudot-spaced_ccitt2_lsb)':   {'TEST 1234': "00001 10000 10100 00001 00100 11011 11101 11001 10000 01010"},
    'enc(baudot_spaced-ita1)':         {'TEST 1234': "10101 00010 10100 10101 10000 01000 00001 00010 00100 00101"},
    'enc(baudot-spaced_ita2_msb)':     {'TEST 1234': "10000 00001 00101 10000 00100 11011 10111 10011 00001 01010"},
    'enc(baudot_spaced-ita2-us)':      {'TEST 1234': "10000 00001 00101 10000 00100 11011 10111 10011 00001 01010"},
}
__examples3__ = {
    'enc(baudot_tape-BAD_ALPHABET)': None,
    'enc(baudot_tape-ita1)': {
        'TEST 1234': "***.**\n* *. *\n   .* \n* *.  \n* *. *\n*  .  \n * .  \n   . *\n   .* \n  *.  \n  *. *",
    },
    'dec(baudot-tape_ita2)':       {'BAD_HEADER\n   .* \n': None},
    'dec(baudot-tape_ita2-us)':    {'***.**\nBAD_TAPE\n': None},
    'dec(baudot_tape-ccitt1_lsb)': {'***.**\n   .* \n*  . *\n*  .  \n': None},
}
if PY3:
    __examples1__.update({
        'enc(baudot_ccitt1_lsb)': {'TEST1234':  "101010001010001101010100000100000100000100101"},
        'enc(baudot-fr)':         {'TEST 1234': "10101000101010010101100000100000001000100010000101"},
    })
    __examples2__.update({
        'enc(baudot-spaced_ccitt1_lsb)': {'TEST1234':  "10101 00010 10001 10101 01000 00100 00010 00001 00101"},
        'enc(baudot_spaced-fr)':         {'TEST 1234': "10101 00010 10100 10101 10000 01000 00001 00010 00100 00101"},
    })


PATTERN = r"^baudot%s([-_](?:ccitt1|ccitt2|eu|fr|ita1|ita2|ita2[-_](?:us" + (r"|meteo" if PY3 else r"") + r")" + \
          (r"|mtk2" if PY3 else r"") + r"|murray|uk|us_tty)(?:[-_](?:lsb|msb))?)?$"
# reserved character
RES_CHR = "\xff"

# sources:
# - http://rabbit.eng.miami.edu/info/baudot.html
# - https://en.wikipedia.org/wiki/Baudot_code
# - https://fr.qwe.wiki/wiki/Baudot_code
# all alphabets consider MSB by default
# CCITT-1 original Baudot code (source: http://rabbit.eng.miami.edu/info/baudot.html)
CCITT1 = [
    "00001", "00010",
    "\x00\xff\xff\xffA-JKEXGM/ZHLYSBRUTCQIWFNOVDP",
    "\x00\xff\xff\xff1.6(2\xff7)\xff:\xff=3\xff8-4\xff9/\xff?\xff£5'0+" if PY3 else \
        "\x00\xff\xff\xff1.6(2\xff7)\xff:\xff=3\xff8-4\xff9/\xff?\xff$5'0+",
]
# CCITT-2 revised Baudot code (source: http://rabbit.eng.miami.edu/info/baudot.html)
CCITT2 = [
    "11111", "11011",
    "\x00E\nA SIU\rDRJNFCKTZLWHYPQOBG\xffMXV\xff",
    "\x003\n- \x0787\r$4',!:(5\")2#6019?&\xff./;\xff",
]
# Original Baudot (French/European ; sources: https://fr.qwe.wiki/wiki/Baudot_code
#                                             https://en.wikipedia.org/wiki/Baudot_code)
BAUDOT = EU = FR = [
    "10000", "01000",
    "\x00AEÉYUIO\xffJGHBCFD \nXZSTWV\x7fKMLRQNP" if PY3 else "\x00AEeYUIO\xffJGHBCFD \nXZSTWV\x7fKMLRQNP",
    "\x0012&34°5 67h89f0\xff.,:;!?'\x7f()=-/\u2116%" if PY3 else "\x0012&34o5 67h89f0\xff.,:;!?'\x7f()=-/\xff%",
]
# International Telegraphic Alphabet 1 (sources: https://fr.qwe.wiki/wiki/Baudot_code
#                                                https://en.wikipedia.org/wiki/Baudot_code)
ITA1 = [
    "10000", "01000",
    "\x00AE\rYUIO\xffJGHBCFD \xffXZSTWV\x7fKMLRQNP",
    "\x0012\r34\xff5 67+89\xff0\xff\n,:.\xff?'\x7f()=-/\xff%",
]
# International Telegraphic Alphabet 2 (sources: https://fr.qwe.wiki/wiki/Baudot_code
#                                                https://en.wikipedia.org/wiki/Baudot_code)
ITA2 = [
    "11111", "11011",
    "\x00E\nA SIU\rDRJNFCKTZLWHYPQOBG\xffMXV\xff",
    "\x003\n- '87\r\x054\x07,!:(5+)2$6019?&\xff./=\xff",
]
# International Telegraphic Alphabet 2 - US TTY (sources: https://fr.qwe.wiki/wiki/Baudot_code
#                                                         https://en.wikipedia.org/wiki/Baudot_code)
ITA2_US = US_TTY = [
    "11111", "11011",
    "\x00E\nA SIU\rDRJNFCKTZLWHYPQOBG\xffMXV\xff",
    "\x003\n- \x0787\r$4',!:(5\")2#6019?&\xff./;\xff",
]
# International Telegraphic Alphabet 2 - Meteo version (source: https://en.wikipedia.org/wiki/Baudot_code)
if PY3:
    ITA2_METEO = [
        "11111", "11011",
        "\x00E\nA SIU\rDRJNFCKTZLWHYPQOBG\xffMXV\xff",
        "-3\n\u2191 \x0787\r\u21974\u2199\u29b7\u2192\u25ef\u21905+\u21962\u21936019\u2295\u2198\xff./\u29b6\xff",
    ]
# Russian MTK-2 alphabet (source: https://fr.qwe.wiki/wiki/Baudot_code)
if PY3:
    MTK2 = [
        "11111", "11011",
        "\x00Е\n\xff СИУ\r\xffРЙНФЦКТЗЛВХЫПЯОБГ\xffМЬЖ\xff",
        "\x003\n- '87\r\xff4Ю,Э:(5+)2Щ6019?Ш\xff./=\xff",
    ]
# Murray code ; NB: not all fractions are supported (source: https://en.wikipedia.org/wiki/Baudot_code)
MURRAY = [
    "00100", "11011",
    " E\xffA\xffSIU\nDRJNFCKTZLWHYPQOBF\xffMXV\x7f", 
    "\x003\xff\xff\xff'87\n²4\xff-\u215f(\xff5./2\xff6019?\xff\xff,£)*" if PY3 else \
        "\x003\xff\xff\xff'87\n²4\xff-\u215f(\xff5./2\xff6019?\xff\xff,$)*",
]
# English Baudot ; NB: not all fractions are supported (sources: https://fr.qwe.wiki/wiki/Baudot_code
#                                                                https://en.wikipedia.org/wiki/Baudot_code)
UK = [
    "10000", "01000",
    "\x00AE/YUIO\xffJGHBCFD -XZSTWV\x7fKMLRQNP", 
    "\x0012\u215f34\xff5 67\xb989\xff0\xff.\xff:\xff²?'\x7f()=-/£+" if PY3 else \
        "\x0012\xff34\xff5 67\xb989\xff0\xff.\xff:\xff²?'\x7f()=-/$+",
]


def _bits_from_tape(tape, trans={'*': "1", ' ': "0"}):
    """ Converts a tape-like string with the given translation for ones and zeros to a series of bits. """
    bits = ""
    trans_rev = {v: k for k, v in trans.items()}
    for i, line in enumerate(tape.splitlines()):
        if i == 0:
            if line != trans_rev['1'] * 3 + "." + trans_rev['1'] * 2:
                raise ValueError("Bad tape header '{}'".format(line))
        else:
            line = line[:3] + line[4:]
            if len(line) != 5:
                raise ValueError("Bad tape line '{}'".format(line))
            bits += "".join(trans.get(c, "") for c in line)
    return bits


def _bits_to_tape(bits, trans={'1': "*", '0': " "}):
    """ Converts a series of bits to a tape-like string with the given translation for ones and zeros. """
    tape = [trans['1'] * 3 + "." + trans['1'] * 2]
    for i in range(0, len(bits), 5):
        group = "".join(trans[b] for b in bits[i:i+5])
        tape.append(group[:3] + "." + group[3:])
    return "\n".join(tape)


def _check_alphabet(alphabet):
    """ Checks the length of letters and figures (must be 32 chars). """
    for chars in alphabet:
        l = len(chars)
        if l != 32:
            raise ValueError("Bad length of alphabet (%d instead of 32)" % l)


def _handle_alphabet(alphabet):
    """ Gets the given alphabet name and transforms it to its dictionary with letters and figures. """
    alphabet = (alphabet or "baudot").lower().replace("-", "_").strip("_")
    if "_lsb" in alphabet:
        alphabet = alphabet.replace("_lsb", "")
        func = lambda x: x[::-1]
    else:
        alphabet = alphabet.replace("_msb", "")
        func = lambda x: x
    _ = globals()[alphabet.upper()]
    st, a = _[:2], _[2:]
    _check_alphabet(a)
    alphabet = {n: {ch: bin(i)[2:].zfill(5) for i, ch in enumerate(alph) if ch != RES_CHR} for n, alph in \
                zip(["letters", "figures"], a)}
    return alphabet, {'letters': st[0], 'figures': st[1]}, func


def baudot_encode(alphabet=None, spaced=False, tape=False):
    ename = "baudot" + ("-spaced" if spaced else "-tape" if tape else "")
    alphabet, states, func = _handle_alphabet(alphabet)
    def encode(text, errors="strict"):
        text = text.upper()
        s, l, state, seen_states = "", len(b(text)), None, []
        for i, c in enumerate(text):
            # if the state is undefined yet, find the relevant alphabet
            if state is None:
                bits= None
                for st in states.keys():
                    try:
                        bits = func(alphabet[st][c])
                        state = st
                        if st not in seen_states:
                            seen_states.append(st)
                        break
                    except KeyError:
                        pass
                if bits is None:
                    bits = handle_error(ename, errors, "?", 5)(c, i)
                s += bits
            # otherwise, handle state change (when the current alphabet does not contain the character to encode but the
            #  other alphabet does
            else:
                try:
                    s += func(alphabet[state][c])
                    continue
                except KeyError:
                    state = list(set(states.keys()) - {state})[0]
                try:
                    s += func(states[state]) + func(alphabet[state][c])
                    if state not in seen_states:
                        seen_states.append(state)
                except KeyError as e:
                    state = list(set(states.keys()) - {state})[0]  # reset the state
                    s += handle_error(ename, errors, "?", 5)(c, i)
        # by default, if no state is specified, the encoded string is handled as letters ; so if figures are used only,
        #  it is necessary to include the groups of bits for figures at the beginning of the encoded string
        s = (states['figures'] if seen_states == ["figures"] else "") + s
        if spaced:
            s = " ".join(s[i:i+5] for i in range(0, len(s), 5))
        elif tape:
            s = _bits_to_tape(s)
        return s, l
    return encode


def baudot_decode(alphabet=None, spaced=False, tape=False):
    ename = "baudot" + ("-spaced" if spaced else "-tape" if tape else "")
    alphabet, states, func = _handle_alphabet(alphabet)
    alphabet = {st: {v: k for k, v in alph.items()} for st, alph in alphabet.items()}
    states = {v: k for k, v in states.items()}
    def decode(text, errors="strict"):
        s, l = "", len(b(text))
        if spaced:
            text = text.replace(" ", "")
        elif tape:
            text = _bits_from_tape(text)
        # infer the starting state by searching for the first encountered groups of bits indicating a valid state ;
        #  by default, we assume letters
        state = "letters"
        for i in range(0, len(text), 5):
            bits = func(text[i:i+5])
            # the following code handles a possible ambiguity ; e.g. when letters have a group of bits matching
            #  a state change
            if bits in states.keys():
                error = False
                # so, when we see the bits of a state, we parse previous groups in order to determine if they are valid
                #  groups in the corresponding state, that is, if no error occurs ; if an error occurs, then it is a
                #  valid state change and not simply a character, and we can set it as the starting state
                for j in range(i-5, 0, -5):
                    try:
                        alphabet[states[bits]][text[j:j+5]]
                    except KeyError:
                        error = True
                        break
                if error:
                    state = list(set(states.values()) - {states[bits]})[0]
                    break
        # now parse the input text
        for i in range(0, len(text), 5):
            bits = func(text[i:i+5])
            try:
                s += alphabet[state][bits]
            except KeyError:
                if bits in states.keys() and states[bits] != state:
                    state = states[bits]
                else:
                    s += handle_error(ename, errors, decode=True, item="group")(bits, i//5)
        return s, l
    return decode


add("baudot", baudot_encode, baudot_decode, PATTERN % r"", examples=__examples1__, guess=[x % "" for x in __guess__],
    entropy=1., printables_rate=1.)


baudot_spaced_encode = lambda a: baudot_encode(a, spaced=True)
baudot_spaced_decode = lambda a: baudot_decode(a, spaced=True)
add("baudot-spaced", baudot_spaced_encode, baudot_spaced_decode, PATTERN % r"[-_]spaced", examples=__examples2__,
    guess=[x % "-spaced" for x in __guess__], entropy=1.48, printables_rate=1.)


baudot_tape_encode = lambda a: baudot_encode(a, tape=True)
baudot_tape_decode = lambda a: baudot_decode(a, tape=True)
add("baudot-tape", baudot_tape_encode, baudot_tape_decode, PATTERN % r"[-_]tape", examples=__examples3__,
    guess=[x % "-tape" for x in __guess__], entropy=1.86, printables_rate=1.)

