#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Manual codec tests.

"""
import os
import random
from unittest import TestCase

from codext.__common__ import *


class ComplementaryTestCase(TestCase):
    def test_codec_baudot(self):
        from codext.binary.baudot import _check_alphabet
        self.assertRaises(ValueError, _check_alphabet, ["BAD_ALPHABET"])
    
    def test_codec_binhex(self):
        hqx = ":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!:"
        # in non-strict modes, CRCs are not checked and what is available from the data fork is returned
        self.assertEqual(codecs.decode(hqx[:-1], "binhex", "ignore"), "Hello")
        self.assertEqual(codecs.decode(hqx.replace("XE", "XF"), "binhex", "replace"), "Helpo")
        self.assertEqual(codecs.decode(hqx[:22] + ":", "binhex", "ignore"), "")
        self.assertEqual(codecs.decode("This is a test", "binhex", "ignore"), "")
        self.assertEqual(codecs.decode(":N!8:", "binhex", "ignore"), "")
    
    def test_codec_church(self):
        from codext.esoteric.church import church_run
        # a program that does not give its list (e.g. an infinite list) is stopped, while deep terms do not recurse
        self.assertRaises(ValueError, church_run, r"(\x.x x) (\x.x x)", max_steps=100)
        self.assertRaises(ValueError, church_run, r"(\y.\c.\n.y y c n) (\y.\c.\n.c (\f.\x.x) (y y c n))")
        self.assertEqual(church_run(r"(\x.x) (" * 3000 + r"\c.\n.n" + ")" * 3000), b"")
        self.assertEqual(codecs.decode(codecs.encode("A" * 1000, "church"), "church"), "A" * 1000)
        # syntax errors are reported whatever the errors handling, and numerals must be lower than 256
        self.assertRaises(ValueError, codecs.decode, r"\c.\n.n x", "church", "ignore")
        self.assertRaises(ValueError, church_run, r"\c.\n.c (\f.\x." + "f (" * 255 + "f x" + ")" * 255 + ") n")
        self.assertEqual(church_run(r"\c.\n.c (\f.\x." + "f (" * 254 + "f x" + ")" * 254 + ") n"), b"\xff")
    
    def test_codec_coquelet(self):
        # with a non-strict errors handling, unsupported characters are replaced with "?" (in the figures shift), dropped
        #  or left as is, while bad tones are skipped one at a time
        self.assertEqual(codecs.encode("a#b", "coquelet", "replace"), "1022 1082 842 1082 842 1112 812 1082 842 1112")
        self.assertEqual(codecs.decode(codecs.encode("a#b", "coquelet", "replace"), "coquelet"), "A?B")
        self.assertEqual(codecs.encode("a#b", "coquelet", "ignore"), "1022 1082 842 1112")
        self.assertEqual(codecs.encode("a#b", "coquelet", "leave"), "1022 1082 # 842 1112")
        for e, r in [("replace", "T?E?"), ("ignore", "TE"), ("leave", "T1000E1082")]:
            self.assertEqual(codecs.decode("872 1172 1000 1022 1112 1082", "coquelet", e), r)
        self.assertRaises(ValueError, codecs.decode, "872 1172 1000", "coquelet")
        self.assertRaises(ValueError, codecs.decode, "872 1172 1000", "coquelet", "BAD_ERRORS")
        # every character of both shifts with each variant, with the shifts inserted only when needed
        from codext.frequency._ita2 import CHARS
        for v in ["coquelet", "coquelet-8"]:
            for chars in CHARS.values():
                text = "".join(c for c in chars if c is not None)
                self.assertEqual(codecs.decode(codecs.encode(text, v), v), text)
        # the idle sequence of Coquelet 8 has the tones of "M", while a misaligned one is resynchronised
        self.assertEqual(codecs.decode("773 960 773 960 826 960", "coquelet8"), "MMT")
        self.assertEqual(codecs.decode("960 773 960 826 960", "coquelet8", "ignore"), "MT")
        self.assertEqual(len(codecs.encode("A1B2", "coquelet").split()), 2 * 7)
    
    def test_codec_cow(self):
        # with a non-strict errors handling, other characters are comments and the program stops at a failing
        #  instruction
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Comment: MoO OOM then moo OOM", "cow", e), "1\n")
            self.assertEqual(codecs.decode("MoO Moo mOo Moo", "cow", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "MoO OOM comment", "cow")
        self.assertRaises(ValueError, codecs.decode, "MoO OOM comment", "cow", "BAD_ERRORS")
        from codext.esoteric.cow import cow_run
        # "MOO" with a non-null cell continues, then "moo" goes back to it forever (it skips the previous instruction,
        #  hence the "MMM" in the loop)
        self.assertRaises(ValueError, cow_run, [6, 7, 9, 0], max_steps=100)
        self.assertEqual(cow_run([6, 10, 4], max_steps=100), (b"1\n\x01", None))
    
    def test_codec_dna(self):
        self.assertEqual(codecs.decode("ABC", "dna-1", errors="ignore"), "\x02")
        self.assertEqual(codecs.decode("ABC", "dna-2", errors="replace"), "[00??01]")
    
    def test_codec_dtmf(self):
        import math, random, wave
        from io import BytesIO
        # with a non-strict errors handling, unsupported characters are replaced with "?", dropped or left as is in the
        #  frequencies, and dropped from a recording, while bad tones are skipped one at a time
        for e, enc, dec in [("replace", "697 1209 ? 770 1336", "1?5?"), ("ignore", "697 1209 770 1336", "15"),
                            ("leave", "697 1209 x 770 1336", "1x5697")]:
            self.assertEqual(codecs.encode("1x5", "dtmf", e), enc)
            self.assertEqual(codecs.decode("697 1209 x 770 1336 697", "dtmf", e), dec)
            self.assertEqual(codecs.decode(codecs.encode(b"1x5", "dtmf-wav", e), "dtmf-wav"), b"15")
        self.assertRaises(ValueError, codecs.decode, "697 1209 697", "dtmf")
        self.assertRaises(ValueError, codecs.decode, "697 1209 697", "dtmf", "BAD_ERRORS")
        # recordings made independently of the encoder, with various formats, frequency deviations, twists (levels of
        #  the tones), noise, short tones and pauses, repeated keys and a dropout in a tone
        from codext.frequency.dtmf import DTMF_TONES
        def recording(keys, rate=8000, width=2, channels=1, tone=.1, pause=.1, drift=0., twist=0., snr=None,
                      dropout=0):
            rnd, s = random.Random(42), []
            for k in keys:
                f1, f2 = (f * (1 + drift) for f in DTMF_TONES[k])
                a = .35 * 10 ** (twist / 20)
                t = [.35 * math.sin(2 * math.pi * f1 * i / rate) + a * math.sin(2 * math.pi * f2 * i / rate)
                     for i in range(int(tone * rate))]
                if dropout:
                    t[len(t) // 2:len(t) // 2 + int(dropout * rate)] = [0.] * int(dropout * rate)
                s += t + [0.] * int(pause * rate)
            if snr is not None:
                s = [x + rnd.gauss(0, math.sqrt(.35 ** 2 / 10 ** (snr / 10))) for x in s]
            full, out = 2 ** (8 * width - 1) - 1, bytearray()
            for x in s:
                v = round(max(-1, min(1, x * .9)) * full)
                out += (bytes([v + 128]) if width == 1 else v.to_bytes(width, "little", signed=True)) * channels
            buf = BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(channels)
                w.setsampwidth(width)
                w.setframerate(rate)
                w.writeframes(bytes(out))
            return buf.getvalue()
        for kw in [{}, {'rate': 44100, 'width': 3, 'channels': 2}, {'rate': 11025, 'width': 1}, {'width': 4},
                   {'drift': .015}, {'drift': -.015}, {'twist': 6}, {'twist': -6}, {'snr': 10},
                   {'tone': .04, 'pause': .04}, {'dropout': .01}]:
            self.assertEqual(codecs.decode(recording("1A*#0D", **kw), "dtmf-wav"), b"1A*#0D")
        self.assertEqual(codecs.decode(recording("1199", tone=.05, pause=.05), "dtmf-wav"), b"1199")
        # tones off by more than 4%, noise and a dial tone (350 and 440 Hz) give no key
        self.assertEqual(codecs.decode(recording("123", drift=.05), "dtmf-wav"), b"")
        rate, rnd = 8000, random.Random(1)
        dial = [.3 * (math.sin(2 * math.pi * 350 * i / rate) + math.sin(2 * math.pi * 440 * i / rate))
                for i in range(rate)]
        for s in [[rnd.gauss(0, .3) for _ in range(rate)], dial]:
            buf = BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(b"".join(round(max(-1, min(1, x)) * 32767).to_bytes(2, "little", signed=True)
                                       for x in s))
            self.assertEqual(codecs.decode(buf.getvalue(), "dtmf-wav"), b"")
        # invalid recordings are reported whatever the errors handling
        self.assertRaises(ValueError, codecs.decode, b"RIFF\x00\x00", "dtmf-wav", "ignore")
    
    def test_codec_morse(self):
        self.assertRaises(LookupError, codecs.encode, "test", "morse-AAB")
    
    def test_codec_hamming(self):
        import random
        from itertools import combinations
        from codext.binary.hamming import _codeword, _decoding
        # example of Wikipedia, minimum distances (3 and 4), correction of all the single-bit errors and, with
        #  Hamming(8,4), detection of all the double-bit errors (that Hamming(7,4) wrongly corrects)
        self.assertEqual(_codeword(0b1011, False), 0b0110011)
        for extended, n, distance in [(False, 7, 3), (True, 8, 4)]:
            codewords, table = [_codeword(d, extended) for d in range(16)], _decoding(extended)
            self.assertEqual(min(bin(a ^ c).count("1") for a, c in combinations(codewords, 2)), distance)
            for d, c in enumerate(codewords):
                self.assertTrue(all(table[c ^ 1 << i] == d for i in range(8)))
                for i, j in combinations(range(n), 2):
                    r = table[c ^ 1 << i ^ 1 << j]
                    self.assertTrue(r is None if extended else r != d)
        # a message with a flipped bit in each codeword is fully corrected
        text, rnd = "The quick brown fox jumps over the lazy dog".encode() * 10, random.Random(1)
        for e in ["hamming", "hamming84"]:
            noisy = bytes(c ^ 1 << rnd.randrange(8 if e == "hamming84" else 7) for c in codecs.encode(text, e))
            self.assertEqual(codecs.decode(noisy, e), text)
        # with a non-strict errors handling, double-bit errors are replaced, dropped or left as is, as a trailing byte
        for e, r in [("replace", b"A??"), ("ignore", b"A"), ("leave", b"A\x03\xc3\x01")]:
            self.assertEqual(codecs.decode(b"\xcci\x03\xc3\x01", "hamming84", e), r)
        self.assertRaises(ValueError, codecs.decode, b"\xcci\x03\xc3", "hamming84")
        self.assertRaises(ValueError, codecs.decode, b"\xcci\x01", "hamming84", "BAD_ERRORS")
    
    def test_codec_nrzi_differential_manchester(self):
        # these line codes do not depend on the polarity of the signal: the inverted signal gives the same bits, except
        #  the first one (depending on the initial level)
        data = bytes(range(256))
        for e in ["nrzi", "nrzi-space", "differential-manchester", "differential-manchester-inverted"]:
            # text with characters outside latin-1 is given back
            self.assertEqual(codecs.decode(codecs.encode("caf\u00e9 \u20ac", e), e), "caf\u00e9 \u20ac")
            inverted = bytes(x ^ 0xff for x in codecs.encode(data, e))
            r = codecs.decode(inverted, e)
            self.assertEqual(r[0] & 0x7f, data[0] & 0x7f)
            self.assertEqual(r[1:], data[1:])
        # differential Manchester requires a transition in the middle of each bit period and pairs of bytes ; with a
        #  non-strict errors handling, decoding ignores the missing transitions and a trailing byte
        with self.assertRaisesRegex(ValueError, "half-bits '11' in bit 4"):
            codecs.decode(b"\x9d\x55", "differential-manchester")
        self.assertRaisesRegex(ValueError, "in bit 16", codecs.decode, b"\x95\x55\x95", "differential-manchester")
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode(b"\x95\x55\x95", "differential-manchester", e), b"@")
            self.assertIsNotNone(codecs.decode(b"\x9d\x55", "differential-manchester", e))
    
    def test_codec_befunge(self):
        # with a non-strict errors handling, unsupported instructions are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode('"z"x,@', "befunge", e), "z")
        self.assertRaises(ValueError, codecs.decode, '"z"x,@', "befunge")
        from codext.esoteric.befunge import befunge_run
        self.assertRaises(ValueError, befunge_run, b">", max_steps=100)
        self.assertEqual(befunge_run(b"1.@", max_steps=100), b"1 ")
    
    def test_codec_brainfuck(self):
        # with a non-strict errors handling, other characters are comments and unmatched brackets are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Comment: ++. then +.]", "brainfuck", e), "\x02\x03")
            self.assertEqual(codecs.decode("+.[", "bf", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "+. comment", "brainfuck")
        self.assertRaises(ValueError, codecs.decode, "+. comment", "brainfuck", "BAD_ERRORS")
    
    def test_codec_lolcode(self):
        from codext.esoteric.lolcode import lolcode_run
        run = lambda body, **kw: lolcode_run(f"HAI 1.2\n{body}\nKTHXBYE", **kw)
        # leading and trailing newlines, a loop variable shadowing a variable, a unary function in a loop (with the
        #  syntax of the reference interpreter) and casts from and to NOOB
        self.assertEqual(lolcode_run("\n\nHAI\nVISIBLE 1\nKTHXBYE\n\n"), "1\n")
        self.assertEqual(run('I HAS A i ITZ "x"\nIM IN YR l UPPIN YR i TIL BOTH SAEM i AN 2\nIM OUTTA YR l\nVISIBLE i'),
                         "x\n")
        self.assertEqual(run("HOW IZ I inc YR x\nSUM OF x AN 1\nIF U SAY SO\nIM IN YR l I IZ inc YR i MKAY WILE "
                             "DIFFRINT i AN 3\nVISIBLE i!\nIM OUTTA YR l"), "012")
        self.assertEqual(run("VISIBLE MAEK NOOB NUMBR AN MAEK NOOB A NUMBAR\nI HAS AN x ITZ 1, x IS NOW A NOOB\n"
                             "BOTH SAEM x AN NOOB, VISIBLE IT"), "00.00\nWIN\n")
        # syntax and runtime errors
        for body in ['VISIBLE "a" ...\n\nVISIBLE "b"', "OBTW never closed", "OBTW x TLDR VISIBLE 1", 'VISIBLE "a"b',
                     "VISIBLE 1 ! 2", "I HAS A 1x", "MAEK 1 A BUKKIT", "VISIBLE", "SUM OF 1 AN", "WTF?\nOMG x\nOIC",
                     "WTF?\nOMG 1\nOMG 1\nOIC", "IM IN YR l I IZ f YR i\nIM OUTTA YR l", "VISIBLE SUM OF NOOB AN 1",
                     'VISIBLE ":(41"', 'VISIBLE ":(XYZ)"', 'VISIBLE ":[NOT A CHARACTER NAME]"', 'VISIBLE ":{x}"',
                     "I IZ f MKAY", "HOW IZ I f YR x\nIF U SAY SO\nI IZ f MKAY", "x R 1",
                     "HOW IZ I f\nI IZ f MKAY\nIF U SAY SO\nI IZ f MKAY", "VISIBLE " + "NOT " * 5000 + "WIN"]:
            self.assertRaises(ValueError, run, body)
        self.assertRaises(ValueError, lolcode_run, "HAI 1.2\nVISIBLE 1\n")
        self.assertRaises(ValueError, lolcode_run, "HAI 1.2\nVISIBLE 1\nKTHXBYE 2")
        self.assertRaises(ValueError, run, "IM IN YR l\nIM OUTTA YR l", max_steps=100)
    
    def test_codec_malbolge(self):
        from codext.esoteric.malbolge import _value, malbolge_run, SIZE
        from unittest.mock import patch
        # with a non-strict errors handling, invalid characters are skipped
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("D\xe9P", "malbolge", e), "")
        # executing a character that is not graphic ASCII ends the program
        self.assertEqual(malbolge_run([_value(0, "o"), 200]), b"")
        self.assertRaises(ValueError, malbolge_run, [ord(c) for c in "(=BA#9\"=<;:3y7x54-21q/p-,+*)\"!h%B0/.~P<<:(8&66#\"!~}|{zyxwvugJ%"],
                          max_steps=100)
        self.assertRaises(ValueError, codecs.decode, "".join(chr(_value(i, "o")) for i in range(SIZE + 1)),
                          "malbolge")
        with patch("codext.esoteric.malbolge.SIZE", 10):
            self.assertRaises(ValueError, codecs.encode, "Hello", "malbolge")
    
    def test_codec_ook(self):
        # with a non-strict errors handling, other characters, an odd last word, "Ook? Ook?" and unmatched brackets are
        #  ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("Ook. Ook. Ook! Ook. Ook? Ook? !? Ook. Ook. ?! Ook!", "ook", e), "\x01")
            self.assertEqual(codecs.decode("Comment: Ook. Ook. Ook! Ook.", "ook-short", e), "\x01")
        self.assertRaises(ValueError, codecs.decode, "Ook. Ook. Ook! Ook.!", "ook")
        self.assertRaises(ValueError, codecs.decode, "Ook? Ook?", "ook", "BAD_ERRORS")
    
    def test_codec_piccolo(self):
        # with a non-strict errors handling, unsupported characters are replaced with "?" (in the figures shift), dropped
        #  or left as is, while bad tones (or the first tone of a bad pair) are skipped one at a time
        for e, enc, dec2, dec1 in [("replace", "460 560 560 560 560 480 540 560 560 480", "T?I??", "T?E"),
                                   ("ignore", "460 560 560 480", "TI", "TE"),
                                   ("leave", "460 560 # 560 480", "T520I480470", "T475E")]:
            self.assertEqual(codecs.encode("a#b", "piccolo", e), enc)
            self.assertEqual(codecs.decode("500 460 520 520 460 480 470", "piccolo", e), dec2)
            self.assertEqual(codecs.decode("620 475 470", "piccolo1", e), dec1)
        self.assertRaises(ValueError, codecs.decode, "500 460 520 520", "piccolo")
        self.assertRaises(ValueError, codecs.decode, "500 460 460", "piccolo", "BAD_ERRORS")
        # every code has its own pair of tones, and every character of both shifts round-trips with each variant
        from codext.frequency._ita2 import CHARS
        from codext.frequency.piccolo import PICCOLO_PAIRS
        self.assertEqual(sorted(PICCOLO_PAIRS), list(range(32)))
        self.assertEqual(len(set(PICCOLO_PAIRS.values())), 32)
        for v in ["piccolo-i", "piccolo-ii", "piccolo-iii"]:
            for chars in CHARS.values():
                text = "".join(c for c in chars if c is not None)
                self.assertEqual(codecs.decode(codecs.encode(text, v), v), text)
    
    def test_codec_piet(self):
        import struct, zlib
        from codext.esoteric.piet import _COLORS, _commands, _program, _read_png, piet_run, BLACK, WHITE
        
        def ppm(rows, maxval=255):
            n = 1 + (maxval > 255)
            return f"P6\n{len(rows[0])} {len(rows)}\n{maxval}\n".encode() + \
                   b"".join((_COLORS[i][k] * maxval // 255).to_bytes(n, "big") for r in rows for i in r for k in range(3))
        
        def png(rows, ctype=2, depth=8, interlace=0, mangle=lambda raw: raw):
            # rows filtered with each filter type in turn, as an image with a palette, in grayscale or in true color
            pal, chunk = sorted({i for r in rows for i in r}), lambda t, d: struct.pack(">I", len(d)) + t + d + b"CRC!"
            px = lambda i: [pal.index(i)] if ctype == 3 else _COLORS[i][:1 + 2 * (ctype & 2)] + (255, ) * (ctype == 6)
            channels, raw, f = {0: 1, 2: 3, 3: 1, 6: 4}[ctype], b"", 0
            bpp = max(1, channels * depth // 8)
            passes = [(0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)] \
                     if interlace else [(0, 0, 1, 1)]
            for x0, y0, dx, dy in passes:
                sub = [r[x0::dx] for r in rows[y0::dy]]
                if not sub or not sub[0]:
                    continue
                prev = None
                for r in sub:
                    samples = [s for i in r for s in px(i)]
                    if depth < 8:
                        samples = [s >> (8 - depth) if ctype == 0 else s for s in samples]
                        bits = "".join(format(s, f"0{depth}b") for s in samples)
                        line = int(bits.ljust((len(bits) + 7) // 8 * 8, "0"), 2).to_bytes((len(bits) + 7) // 8, "big")
                    else:
                        line = b"".join((s * 257 if depth == 16 else s).to_bytes(depth // 8, "big") for s in samples)
                    prev, out = prev or bytes(len(line)), bytearray()
                    for i, x in enumerate(line):
                        a, b_, c = line[i-bpp] if i >= bpp else 0, prev[i], prev[i-bpp] if i >= bpp else 0
                        p = a + b_ - c
                        pa, pb, pc = abs(p - a), abs(p - b_), abs(p - c)
                        out.append((x - [0, a, b_, (a + b_) // 2, a if pa <= pb and pa <= pc else b_ if pb <= pc else c][f])
                                   & 255)
                    raw += bytes([f]) + bytes(out)
                    prev, f = line, (f + 1) % 5
            return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", len(rows[0]), len(rows), depth, ctype, 0,
                   0, interlace)) + (chunk(b"PLTE", bytes(v for i in pal for v in _COLORS[i])) if ctype == 3 else b"") + \
                   chunk(b"tEXt", b"x") + chunk(b"IDAT", zlib.compress(mangle(raw))) + chunk(b"IEND", b"")
        
        def gif(rows, interlace=False, local=False):
            # LZW compression, codes being written from the least significant bits
            pal = sorted({i for r in rows for i in r})
            n = max(2, (len(pal) - 1).bit_length())
            clear, size, table, w, codes = 1 << n, n + 1, {bytes([i]): i for i in range(1 << n)}, b"", []
            codes.append((clear, size))
            order = [y for y0, dy in [(0, 8), (4, 8), (2, 4), (1, 2)] for y in range(y0, len(rows), dy)] if interlace \
                    else range(len(rows))
            for k in [pal.index(i) for y in order for i in rows[y]]:
                if (wk := w + bytes([k])) in table:
                    w = wk
                    continue
                codes.append((table[w], size))
                table[wk], w = len(table) + 2, bytes([k])
                if len(table) + 1 == 1 << size:
                    size += 1
            codes += [(table[w], size)]
            if len(table) + 2 == 1 << size:
                size += 1
            codes += [(clear + 1, size)]
            v = sum(c << sum(s for _, s in codes[:i]) for i, (c, _) in enumerate(codes))
            data = v.to_bytes((sum(s for _, s in codes) + 7) // 8, "little")
            colors = bytes(v for i in pal for v in _COLORS[i]).ljust(3 << n, b"\x00")
            return b"GIF89a" + struct.pack("<HHBBB", len(rows[0]), len(rows), [0x80 | (n - 1), 0][local], 0, 0) + \
                   (b"" if local else colors) + b"\x21\xf9\x04\x00\x00\x00\x00\x00" + b"\x2c" + \
                   struct.pack("<HHHHB", 0, 0, len(rows[0]), len(rows), [0, 0x80 | (n - 1)][local] | 0x40 * interlace) + \
                   (colors if local else b"") + bytes([n]) + \
                   b"".join(bytes([len(data[i:i+255])]) + data[i:i+255] for i in range(0, len(data), 255)) + b"\x00;"
        
        run = lambda cmds, **kw: piet_run(ppm(_program(cmds)), **kw)
        # image formats, codel sizes
        rows = _program(_commands("Hi€"))
        for image in [ppm(rows), ppm(rows, 65535), png(rows), png(rows, 6), png(rows, 2, 16), png(rows, 3),
                      png(rows, 3, 4), png(rows, interlace=1), gif(rows), gif(rows, True, True), gif(_program(
                      _commands("Lorem ipsum dolor sit amet, consectetur adipiscing elit")))[:-2] + b"\x00;"]:
            self.assertIn(piet_run(image), ["Hi€", "Lorem ipsum dolor sit amet, consectetur adipiscing elit"])
        self.assertEqual(piet_run(png(_program(_commands("Hi"), 3), 3, 8, 1)), "Hi")
        self.assertEqual(piet_run(png(_program(_commands("Hi"), 3), 3, 8, 1), codel_size=3), "Hi")
        self.assertEqual(_read_png(png([[WHITE, BLACK, BLACK]], 0, 1)), [[(255, 255, 255), (0, 0, 0), (0, 0, 0)]])
        self.assertEqual(_read_png(png([[WHITE, BLACK]], 0, 16)), [[(255, 255, 255), (0, 0, 0)]])
        self.assertEqual(piet_run(png([[BLACK]], interlace=1)), "")
        # invalid images: unknown format, no image, truncated data, bad PNG filter or LZW code, missing palette
        gif1 = lambda w, data: b"GIF89a" + struct.pack("<HHBBB", w, 1, 0x81, 0, 0) + bytes(12) + b"\x2c" + \
                               struct.pack("<HHHHB", 0, 0, w, 1, 0) + b"\x02" + bytes([len(data)]) + data + b"\x00;"
        self.assertEqual(piet_run(gif1(1, b"\x04\x01")), "")
        for image in [b"GIF89a" + b"\x01\x00\x01\x00\x00\x00\x00;", gif(rows)[:-40], png(rows)[:-30], b"P6\n2 1\n255\n",
                      b"P3 0 0 255\n", png(rows).replace(b"tEXt", b"IEND"), png(rows, mangle=lambda r: r[:-5]),
                      png(rows, mangle=lambda r: b"\x09" + r[1:]), gif1(1, b"\x3c"), gif1(2, b"\x44\x01"),
                      gif1(1, b"\x04\x01").replace(b"\x81", b"\x01", 1), b"BM"]:
            self.assertRaises(ValueError, piet_run, image)
        # commands, the commands that cannot be performed (e.g. division by zero) being ignored
        for cmds, out in [([("push", 7), ("push", 3), ("sub", None), ("dup", None), ("outn", None), ("push", 3),
                            ("greater", None), ("outn", None)], "41"),
                          ([("push", 1), ("push", 3), ("sub", None), ("dup", None), ("push", 3), ("div", None),
                            ("outn", None), ("push", 3), ("mod", None), ("outn", None)], "-11"),
                          ([("push", 1), ("push", 2), ("push", 3), ("push", 3), ("push", 1), ("roll", None),
                            ("outn", None), ("outn", None), ("outn", None)], "213"),
                          ([("push", 5), ("push", 1), ("roll", None), ("outn", None), ("outn", None)], "15"),
                          ([("pop", None), ("push", 5), ("push", 1), ("not", None), ("div", None), ("mod", None),
                            ("outn", None), ("outn", None)], "05"),
                          ([("push", 4), ("pointer", None), ("push", 2), ("switch", None), ("inn", None), ("inc", None),
                            ("push", 1), ("not", None), ("push", 1), ("sub", None), ("outc", None), ("outn", None)],
                           "-1")]:
            self.assertEqual(run(cmds), out)
        self.assertRaises(ValueError, run, [("push", 2)] + [("dup", None), ("mul", None)] * 18)
        # halting on a black codel, when retracing a path through white codels, or not halting
        self.assertEqual(piet_run(b"P3 1 1 255 0 0 0"), "")
        self.assertEqual(piet_run(b"P3 2 1 255 255 255 255 0 0 0"), "")
        self.assertRaises(ValueError, piet_run, b"P3 2 1 255 255 0 0 255 255 0", max_steps=1000)
        self.assertRaises(ValueError, piet_run, b"P3 3 1 255 255 0 0 255 255 255 255 255 0", max_steps=1000)
        self.assertRaises(ValueError, piet_run, b"P3 3 1 255" + b" 255" * 9, max_steps=2)
        # with a non-strict errors handling, other colors are white
        program = "P3 4 2 255\n255 192 192  255 0 0  192 0 192  255 0 255\n255 192 192  0 0 0  255 0 255  255 0 255\n"
        self.assertEqual(codecs.decode(program.replace("255 0 0", "1 2 3"), "piet", "ignore"), "")
        self.assertRaises(ValueError, codecs.decode, program.replace("255 0 0", "1 2 3"), "piet", "BAD_ERRORS")
    
    def test_codec_pikalang(self):
        # with a non-strict errors handling, unknown words and unmatched brackets are ignored
        for e in ["ignore", "replace", "leave"]:
            self.assertEqual(codecs.decode("pi pi pikachu chu ka pikachu pika", "pikalang", e), "\x02\x01")
            self.assertEqual(codecs.decode("pi pikachu bad pi pikachu", "pikalang", e), "\x01\x02")
        self.assertRaises(ValueError, codecs.decode, "pi pika pikachu", "pikalang", "BAD_ERRORS")
        from codext.esoteric._brainfuck import bf_run
        self.assertRaises(ValueError, bf_run, "+[]", max_steps=100)
        self.assertEqual(bf_run("+[-]+.", max_steps=100), b"\x01")
    
    def test_codec_polybius(self):
        from codext.ciphers.polybius import polybius_encode, polybius_decode
        self.assertRaises(LookupError, polybius_encode, "ABC")
        self.assertRaises(ValueError, polybius_decode(), "BAD_")
        self.assertRaises(ValueError, polybius_decode(), "441543441")
        self.assertEqual(codecs.decode("441543445", "polybius", "ignore"), "TEST")
    
    def test_codec_soundex(self):
        from codext.others.soundex import _soundex
        # examples of the US National Archives (first letter with the same digit as the next consonant, consonants
        #  separated by H or W, vowels separating consonants with the same digit)
        for w, c in [("Washington", "W252"), ("Lee", "L000"), ("Gutierrez", "G362"), ("Pfister", "P236"),
                     ("Jackson", "J250"), ("Tymczak", "T522"), ("Ashcraft", "A261"), ("Ashcroft", "A261"),
                     ("Honeyman", "H555"), ("Robert", "R163"), ("Rupert", "R163"), ("Rubin", "R150")]:
            self.assertEqual(_soundex(w), c)
            self.assertEqual(codecs.encode(w.lower(), "soundex"), c)
        # Ciphey's table differs only by not merging the first letter with the next consonant (e.g. "cc" giving "C200")
        self.assertEqual(codecs.encode("cc czech", "soundex"), "C000 C200")
        # with a non-strict errors handling, codes without word are replaced with "?", dropped or left as is
        for e, r in [("replace", "report ?."), ("ignore", "report ."), ("leave", "report T522.")]:
            self.assertEqual(codecs.decode("R163 T522.", "soundex", e), r)
        self.assertRaises(ValueError, codecs.decode, "T522", "soundex")
        self.assertRaises(ValueError, codecs.decode, "T522", "soundex", "BAD_ERRORS")
        # codes within other tokens are left as is, as well as words without ASCII letters
        self.assertEqual(codecs.decode("xR163 R1634 R163", "soundex"), "xR163 R1634 report")
        self.assertEqual(codecs.encode("\u00c9mile \u65e5\u672c", "soundex"), "E540 \u65e5\u672c")
        self.assertEqual(codecs.decode("W643", "soundex-all"), "[world|worldwide|worlds]")
        self.assertEqual(codecs.decode("W643 T522", "soundex-all", "leave"), "[world|worldwide|worlds] T522")
    
    def test_codec_telegraph(self):
        # examples of Wikipedia, the same name being written with simplified and traditional characters
        self.assertEqual(codecs.encode("\u4e2d\u6587\u4fe1\u606f", "telegraph"), "0022 2429 0207 1873")
        self.assertEqual(codecs.encode("\u8427\u7231\u56fd", "telegraph"), "5618 1947 0948")
        self.assertEqual(codecs.encode("\u856d\u611b\u570b", "telegraph-taiwan"), "5618 1947 0948")
        # the two characters with two codes in the codebook of Taiwan are encoded with the first one
        self.assertEqual(codecs.encode("\u5875\u843c", "telegraph-taiwan"), "1057 5501")
        self.assertEqual(codecs.decode("7775 9795", "telegraph-taiwan"), "\u5875\u843c")
        # with a non-strict errors handling, unsupported characters and bad codes are replaced, dropped or left as is
        for e, enc, dec in [("replace", "0022 ? 2429", "\u4e2d??"), ("ignore", "0022 2429", "\u4e2d"),
                            ("leave", "0022 A 2429", "\u4e2d0024abc")]:
            self.assertEqual(codecs.encode("\u4e2dA\u6587", "telegraph", e), enc)
            self.assertEqual(codecs.decode("0022 0024 abc", "telegraph", e), dec)
        self.assertRaises(ValueError, codecs.encode, "\u4e2dA", "telegraph", "BAD_ERRORS")
        self.assertRaises(ValueError, codecs.decode, "0024", "telegraph", "BAD_ERRORS")
    
    def test_codec_letter_indices(self):
        # bad characters are consumed when not raising an error (decoding used to loop forever)
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "ignore"), "BEC")
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "replace"), "BE?C")
        self.assertEqual(codecs.decode("1E!2", "consonant-index", "leave"), "BE!C")
        # the errors handling applies to the encoded text too
        self.assertEqual(codecs.encode("Test!", "consonant-index", "ignore"), "16E1516")
        self.assertEqual(codecs.encode("Test!", "consonant-index", "replace"), "16E1516?")
    
    def test_codec_sms(self):
        self.assertEqual(codecs.decode("A-B-222-3-4-5", "sms", "leave"), "ABcdgj")


class ManualTestCase(TestCase):
    def test_codec_asn1(self):
        # a dump with big and negative integers, bit strings with unused bits or holding a DER structure, an unsorted
        #  set (sorted in DER), tags of other classes (also above 30), strings of other encodings and an empty element
        dump = "\n".join(["SEQUENCE {", "  INTEGER 0x00ffeeddccbbaa99887766554433221100", "  INTEGER -129",
                          "  BIT STRING '101'B", "  BIT STRING {", "    SEQUENCE {", "      NULL", "    }", "  }",
                          "  OCTET STRING {", "    SET {", '      UTF8String "b"', '      UTF8String "a"', "    }",
                          "  }",
                          "  [APPLICATION 5] 'CAFE'H", "  [PRIVATE 300] {", '    BMPString "\\u20ac"',
                          '    UniversalString "\\ud83d\\ude00"', "  }", "  [0] {}", "  RELATIVE-OID 8.571",
                          "  OBJECT IDENTIFIER 1.2.840.113549.1.1.11", '  GeneralizedTime "20260101120000Z"',
                          "  OCTET STRING ''H", "}"])
        der = bytes.fromhex("3063021100ffeeddccbbaa998877665544332211000202ff7f030205a003050030020500040831060c0161"
                            "0c01624502cafeff822c0a1e0220ac1c040001f600a0000d0308843b06092a864886f70d01010b180f3230"
                            "32363031303131323030" "30305a0400")
        self.assertEqual(codecs.encode(dump.encode(), "asn1"), der)
        back = codecs.decode(der, "asn1").decode()
        self.assertIn('UTF8String "a"\n      UTF8String "b"', back)
        self.assertIn("1.2.840.113549.1.1.11  -- sha256WithRSAEncryption", back)
        self.assertEqual(codecs.encode(back.encode(), "asn1"), der)
        # BER forms (indefinite lengths, constructed strings, non-minimal lengths and integers) are dumped by their
        #  value, and encoded back to DER, while non-canonical contents are dumped in hexadecimal
        ber = b"\x30\x80\x24\x80\x04\x01h\x04\x01i\x00\x00\x02\x02\x00\x05\x0c\x81\x02hi\x01\x01\x01\x00\x00"
        self.assertEqual(codecs.decode(ber, "asn1"), b"SEQUENCE {\n  OCTET STRING '6869'H\n  INTEGER '0005'H\n"
                                                     b"  UTF8String \"hi\"\n  BOOLEAN '01'H\n}")
        self.assertEqual(codecs.encode(codecs.decode(ber, "asn1"), "asn1"),
                         b"\x30\x0f\x04\x02hi\x02\x02\x00\x05\x0c\x02hi\x01\x01\x01")
        self.assertEqual(codecs.decode(b"\x0c\x02\xff\xfe", "asn1"), b"UTF8String 'FFFE'H")
        # the der and ber codecs: bit strings, segments of a constructed bit string and character strings of other
        #  types
        self.assertEqual(codecs.decode(b"\x03\x03\x00hi", "der"), b"hi")
        self.assertRaises(ValueError, codecs.decode, b"\x03\x03\x01hi", "der")
        self.assertEqual(codecs.decode(b"\x23\x08\x03\x02\x00h\x03\x02\x00i", "ber"), b"hi")
        self.assertRaises(ValueError, codecs.decode, b"\x23\x08\x03\x02\x01h\x03\x02\x00i", "ber")
        self.assertEqual(codecs.decode(b"\x1c\x08\x00\x00\x00h\x00\x00\x00i", "der"), b"hi")
        self.assertEqual(codecs.decode(b"\x0c\x02\xc3\xa9", "der"), b"\xe9")
        # malformed elements and dumps, whatever the errors handling
        for bad in [b"\x30\x80\x02\x01\x05", b"\x24\x80\x02\x01\x05\x00\x00", b"\x02\x84\xff\xff\xff\xff",
                    b"\x1f\x01\x00", b"\x30\x80" * 300]:
            self.assertRaises(ValueError, codecs.decode, bad, "asn1", "ignore")
        self.assertRaises(ValueError, codecs.decode, b"\x0c\x02hi\x0c\x00", "der")
        self.assertRaises(ValueError, codecs.decode, b"\x1f\x01\x00", "der")
        # truncated tag and length, indefinite length of a primitive element, constructed string in DER, bad BMPString
        for bad, e in [(b"\x1f\x81", "asn1"), (b"\x04", "asn1"), (b"\x04\x80\x00\x00", "asn1"),
                       (b"\x24\x04\x04\x02hi", "der"), (b"\x1e\x01h", "der")]:
            self.assertRaises(ValueError, codecs.decode, bad, e)
        from codext.others.asn1 import _parse, _raise
        self.assertRaises(ValueError, _parse, b"\x1f\x80\x01\x00", False, _raise)
        # non-canonical object identifiers, a string starting like a SEQUENCE but not holding one and elements of
        #  universal types in an unexpected form are dumped in hexadecimal
        for data, dump in [(b"\x06\x00", b"OBJECT IDENTIFIER ''H"),
                           (b"\x06\x02\x80\x01", b"OBJECT IDENTIFIER '8001'H"),
                           (b"\x04\x02\x30\x05", b"OCTET STRING '3005'H"), (b"\x10\x00", b"[UNIVERSAL 16] ''H"),
                           (b"\x22\x00", b"[UNIVERSAL 2] {}")]:
            self.assertEqual(codecs.decode(data, "asn1"), dump)
            self.assertEqual(codecs.encode(dump, "asn1"), data)
        self.assertEqual(codecs.encode(b"-- a comment\nNULL  -- another one", "asn1"), b"\x05\x00")
        for bad, line in [("SEQUENCE {\n  INTEGER 1.2\n}", 2), ("SEQUENCE {\n  FOO 1\n}", 2), ("NULL 'zz'H", 1),
                          ("OBJECT IDENTIFIER 3.1", 1), ("PrintableString \"\\u20ac\"", 1), ("INTEGER {", 1),
                          ("SEQUENCE 5", 1), ("[0] \"x\"", 1), ("INTEGER", 1), ("NULL\nUTF8String \"\\x\"", 2)]:
            with self.assertRaisesRegex(ValueError, f"line {line}"):
                codecs.encode(bad, "asn1", "ignore")
    
    def test_codec_aaencode(self):
        prog = codecs.encode("alert(1)", "aaencode")
        # lone surrogates, a program reformatted with other whitespaces and a program without its last semicolon
        for s in ["\ud800", "a\udc00b", "\U0001f600"]:
            self.assertEqual(codecs.decode(codecs.encode(s, "aaencode"), "aaencode"), s)
        self.assertEqual(codecs.decode(prog.replace(" ", "").replace("+", "+\n  "), "aaencode"), "alert(1)")
        self.assertEqual(codecs.decode(prog[:-1], "aaencode"), "alert(1)")
        # the easter egg of the reference encoder is ignored while decoding
        egg = "ひだまりスケッチ×365 来週も見てくださいね!"
        self.assertIn("X=_=3;", codecs.encode(egg, "aaencode"))
        self.assertEqual(codecs.decode(codecs.encode(egg, "aaencode"), "aaencode"), egg)
        # truncated payload, unexpected token and invalid escape sequence ("\\u141", a JavaScript syntax error),
        #  whatever the errors handling
        for bad in [prog[:-30], prog.replace("(ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ)+", "(ﾟДﾟ)[ﾟεﾟ]+(ﾟΘﾟ)-", 1),
                    prog.replace("(ﾟДﾟ)[ﾟεﾟ]+", "(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ", 1)]:
            self.assertRaises(ValueError, codecs.decode, bad, "aaencode")
            self.assertRaises(ValueError, codecs.decode, bad, "aaencode", "ignore")
        # without its first backslash, the escape sequence of the first character is read as digits
        self.assertEqual(codecs.decode(prog.replace("(ﾟДﾟ)[ﾟεﾟ]+", "", 1), "aaencode"), "141lert(1)")
    
    def test_codec_jjencode(self):
        prog = codecs.encode("alert(1)", "jjencode-abc")
        # lone surrogates, the name of the variable read from the program and a program reformatted with whitespaces
        for s in ["\ud800", "a\udc00b", "\U0001f600"]:
            self.assertEqual(codecs.decode(codecs.encode(s, "jjencode"), "jjencode"), s)
        self.assertTrue(prog.startswith("abc=~[];"))
        self.assertEqual(codecs.decode(prog, "jjencode"), "alert(1)")
        self.assertEqual(codecs.decode(prog.replace("+", "+\n  "), "jjencode-other"), "alert(1)")
        self.assertEqual(codecs.decode(prog[:-1], "jjencode"), "alert(1)")
        # unlike the reference encoder, the escape sequences are padded when needed
        self.assertIn("\"\\\\\"+$.___+$.___+$.__$+$.__$+", codecs.encode("\x011", "jjencode"))
        self.assertIn("\"\\\\\"+$._+$.___+$.___+$.$$$_+$.$__$+", codecs.encode("\xe9", "jjencode"))
        # the reference encoder gives "\ue9" for "é", which is a JavaScript syntax error
        self.assertRaises(ValueError, codecs.decode, codecs.encode("\xe9", "jjencode").replace("$.___+$.___+", "", 1),
                          "jjencode")
        # no variable initialization, truncated payload, unexpected token and unterminated string literal
        for bad in [prog[8:], prog[:-12], prog.replace("abc.__+\"(\"", "abc.x+\"(\""),
                    prog.replace("\"(\"+", "\"(+", 1)]:
            self.assertRaises(ValueError, codecs.decode, bad, "jjencode")
    
    def test_codec_jsfuck(self):
        from codext.web.jsfuck import MAPPING, _jsfuck, jsfuck_run
        S = lambda x: "(" + _jsfuck(x) + ")"
        F = lambda via="at": f"[][{S(via)}][{S('constructor')}]"
        # every character of the reference encoder's table, including those taken from the representation of RegExp,
        #  which the reference encoder gets wrong
        for c, expr in MAPPING.items():
            self.assertEqual(jsfuck_run(expr), c)
        for c in "ER:?\\":
            self.assertIn(c, MAPPING)
        # values as given by Node.js
        for expr, value in [(f"(+{S('255')})[{S('toString')}](+{S('16')})", "ff"),
                            (f"(+{S('-255')})[{S('toString')}](+{S('2')})", "-11111111"),
                            (f"+{S('1e21')}+[]", "1e+21"), (f"+{S('1.5e-7')}+[]", "1.5e-7"),
                            (f"+{S('0.1')}+(+{S('0.2')})", "0.30000000000000004"),
                            (f"(+{S('123.456')})[{S('toFixed')}](+{S('1')})", "123.5"),
                            (f"(+{S('2.5')})[{S('toFixed')}]()", "3"),
                            (f"(+{S('-0.0001')})[{S('toFixed')}](+{S('2')})", "-0.00"),
                            (f"+{S('0x1f')}", "31"), (f"+{S(' 12 ')}", "12"), (f"+{S('abc')}", "NaN"),
                            ("[[]]+[[[]]]", ""), ("!![]+[][[]]", "NaN"), (f"[][{S('entries')}]()+[]",
                                                                         "[object Array Iterator]"),
                            (f"{S('abc')}[{S('at')}]({S('-1')})", "c"), (f"{S('abc')}[{S('charAt')}]({S('-1')})", ""),
                            (f"{S('x')}[{S('fontcolor')}]({S('a' + chr(34) + 'b')})",
                             "<font color=\"a&quot;b\">x</font>"),
                            (f"{F()}({S('return escape')})()({S('<x> é€')})", "%3Cx%3E%20%E9%u20AC"),
                            (f"{F()}({S('return unescape')})()({S('%41%u20AC')})", "A€"),
                            (f"{F()}({S('return/x/')})()[{S('constructor')}]({S('a/b')})+[]", "/a\\/b/"),
                            (f"{F()}({S('return/x/')})()[{S('constructor')}]()+[]", "/(?:)/"),
                            (f"[+!+[]][{S('includes')}](+!+[])", "true"),
                            (f"[+[![]]][{S('includes')}](+[![]])", "true"),
                            (f"[+[![]]][{S('indexOf')}](+[![]])", "-1"),
                            (f"[][{S('at')}][{S('call')}]({S('xyz')})", "x"),
                            (f"[][{S('flat')}]+[]", "function flat() { [native code] }"),
                            (f"{F()}({S('return' + chr(34) + 'q' + chr(34))})+[]",
                             "function anonymous(\n) {\nreturn\"q\"\n}")]:
            self.assertEqual(jsfuck_run(expr), value)
        # other conversions and methods, and unsupported arguments
        from unittest.mock import patch
        for expr, value in [("![][[]]", "true"), ("!([]+[])", "true"), ("!(+[]+[])", "false"),
                            (f"(+[![]])[{S('toString')}](+{S('2')})", "NaN"),
                            (f"(+{S('1e21')})[{S('toFixed')}](+{S('2')})", "1e+21"),
                            (f"(![]+[])[{S('length')}]", "5"),
                            (f"([]+[])[{S('constructor')}][{S('fromCharCode')}](+{S('65')})", "A"),
                            (f"[][{S('constructor')}](+{S('3')})", ",,"), (f"[][{S('constructor')}]({S('a')})", "a"),
                            (f"{F()}({S('return/x/g')})()[{S('source')}]", "x"),
                            (f"{F()}({S('return/x/')})()[{S('constructor')}]({F()}({S('return/y/i')})())", "/y/i")]:
            self.assertEqual(jsfuck_run(expr), value)
        for bad in [f"(+{S('1')})[{S('toString')}](+{S('37')})", f"(+{S('0.5')})[{S('toString')}](+{S('2')})",
                    f"(+{S('1')})[{S('toFixed')}](+{S('101')})", f"[][{S('at')}][{S('call')}](+[])",
                    f"[][{S('at')}][{S('call')}][{S('call')}]([])",
                    f"{F()}({S('return' + chr(34) + chr(92) + 'x4' + chr(34))})"]:
            self.assertRaises(ValueError, jsfuck_run, bad)
        with patch("codext.web.jsfuck.MAX_LENGTH", 4):
            self.assertRaises(ValueError, jsfuck_run, _jsfuck("abcde"))
        # a program running some code gives this code, whatever the way it gets the Function constructor or eval
        code = "alert(\"Hello, World!\")"
        for prog in [codecs.encode(code, "jsfuck-eval"), f"{F()}({S('return eval')})()({S(code)})",
                     f"{F('filter')}({S(code)})()", f"{F('fill')}({S(code)})()"]:
            self.assertEqual(codecs.decode(prog, "jsfuck"), code)
        self.assertEqual(codecs.decode(" \n".join(_jsfuck("hi")), "jsfuck"), "hi")
        # unsupported calls, the result of some code being used, too deep a nesting and too large an array, whatever
        #  the errors handling
        for bad in [f"[][{S('map')}]([])", f"{F()}({S('x')})()+[]", "(" * 100000 + "[]" + ")" * 100000,
                    f"[][{S('constructor')}](+{S('1e9')})", "[]()", "+[]-[]", "+[]+", "[x]"]:
            self.assertRaises(ValueError, codecs.decode, bad, "jsfuck", "ignore")
    
    def test_codec_aer256(self):
        from codext.ciphers._jsfloat import js_str as _js_str
        # numbers formatted as with JavaScript's String(...), as given by Node.js
        for x, r in [(0., "0"), (-0., "0"), (1e21, "1e+21"), (123456789012345680000., "123456789012345680000"),
                     (1e-6, "0.000001"), (1e-7, "1e-7"), (-1.2345e-7, "-1.2345e-7"), (2**60, "1152921504606847000"),
                     (float("nan"), "NaN"), (float("-inf"), "-Infinity"), (.1, "0.1")]:
            self.assertEqual(_js_str(x), r)
        # numbers that are not positive after decryption give no character, as with the original JavaScript
        self.assertEqual(codecs.decode("NaN, -1e+21, 175.10891089108912", "aer256-key"), "th")
        self.assertEqual(codecs.decode("x, 175.10891089108912", "aer256-key", "ignore"), "th")
        # with a long key, blocks exceed the precision of floats
        self.assertNotEqual(codecs.decode(codecs.encode("this is a test", k := "aer256-thisisaverylongkey"), k),
                            "this is a test")
        # with ARMON-64, numbers in exponent notation are not split on their "+"
        v = round((1e21 + 99) * 98 - 97)
        self.assertEqual(codecs.decode("1e+21", "armon64-abc"), bytes.fromhex(f"{v:x}").decode("latin-1"))
        self.assertEqual(codecs.decode("1e+21+1e+21", "armon64-abc"), 2 * codecs.decode("1e+21", "armon64-abc"))
    
    def test_codec_affine(self):
        STR = "this is a test"
        AFF1 = "vjkubkubcbvguv"
        self.assertRaises(LookupError, codecs.encode, STR, "affine-BAD")
        self.assertRaises(LookupError, codecs.encode, STR, "affine-?l?u-BAD")
        # uses by default an alphabet with lowercase, uppercase, whitespace and parameters a=1 and b=2
        self.assertEqual(codecs.encode(STR, "affine"), codecs.encode(STR, "affine-?l?u?s-1,2"))
        self.assertEqual(codecs.encode(STR, "affine"), AFF1)
        self.assertEqual(codecs.encode(b(STR), "affine"), b(AFF1))
        self.assertEqual(codecs.decode(AFF1, "affine"), STR)
        self.assertEqual(codecs.decode(b(AFF1), "affine"), b(STR))
        AFF2 = "ORWJdWJdidOCJO"
        self.assertEqual(codecs.encode(STR, "affine-?l?u?d?s-5,8"), AFF2)
        self.assertEqual(codecs.encode(b(STR), "affine-?l?u?d?s-5,8"), b(AFF2))
        self.assertEqual(codecs.decode(AFF2, "affine-?l?u?d?s-5,8"), STR)
        self.assertEqual(codecs.decode(b(AFF2), "affine-?l?u?d?s-5,8"), b(STR))
        AFF3 = "QsuOcuOcecQmOQ"
        self.assertEqual(codecs.encode(STR, "affine-?l?u?d?s-2,4"), AFF3)
        self.assertEqual(codecs.encode(b(STR), "affine-?l?u?d?s-2,4"), b(AFF3))
        self.assertEqual(codecs.decode(AFF3, "affine-?l?u?d?s-2,4"), STR)
        self.assertEqual(codecs.decode(b(AFF3), "affine-?l?u?d?s-2,4"), b(STR))
        self.assertRaises(ValueError, codecs.decode, ".BAD.", "affine-?l?u?d?s-2,4")
        self.assertIsNotNone(codecs.encode("TEST", "affine_?u-1,2"))
        # example of parameters that cause mapping collisions
        self.assertRaises(LookupError, codecs.encode, STR, "affine-?l?u?d?s-6,8")
    
    def test_codec_atom128(self):
        # the padding is fixed when not in strict mode (an incomplete last character being dropped)
        for s in ["0IHt0/C", "0IHt0/CCC", "0IHt0/C%"]:
            self.assertEqual(codecs.decode(s, "atom128", "ignore"), "test")
        self.assertEqual(codecs.decode("0IHt0/", "atom128", "replace"), "test")
        # ciphertexts made from the UTF-8 bytes of the text (without escape()) are decoded as well (e.g. those of
        #  https://gist.github.com/tunelko/49b7e64c1688d62d0ecd), the text being then unescaped only if it is ASCII
        import base64
        b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        for e, alphabet in [("atom128", "/128GhIoPQROSTeUbADfgHijKLM+n0pFWXY456xyzB7=39VaqrstJklmNuZvwcdEC"),
                            ("zong22", "ZKj9n+yf0wDVX1s/5YbdxSo=ILaUpPBCHg8uvNO4klm6iJGhQ7eFrWczAMEq3RTt2")]:
            for s, r in [("caf\u00e9 \u20ac \U0001f600", "caf\u00e9 \u20ac \U0001f600"),
                         ("Hello, World!", "Hello, World!"), ("x%41y", "xAy")]:
                c = base64.b64encode(s.encode()).decode().translate(str.maketrans(b64, alphabet))
                self.assertEqual(codecs.decode(c, e), r)
    
    def test_codec_arabica_chinzo_japoo(self):
        from codext.obfuscation.arabica2rs import _TABLE as ARABICA
        from codext.obfuscation.chinzo72c import CHINZO
        chinzo = {chr(int(code, 4)): s for code, s in CHINZO}
        # with a non-strict errors handling, unknown characters are replaced, dropped or left as is, and malformed
        #  escape sequences or invalid UTF-8 are replaced
        for e, r in [("replace", "t?st"), ("ignore", "tst"), ("leave", "tXst")]:
            self.assertEqual(codecs.decode("\u5f92 X \u7c21 \u5f92 \u7c7b", "japoo-c2s", e), r)
        self.assertRaises(ValueError, codecs.decode, "\u5f92 X \u7c7b", "japoo-c2s")
        bad = " ".join(chinzo[c] for c in "t%") + " \u5434"
        self.assertRaisesRegex(ValueError, "escape sequence", codecs.decode, bad, "chinzo-72c")
        self.assertEqual(codecs.decode(bad, "chinzo-72c", "replace"), "t%")
        bad = "".join(ARABICA[c] for c in "%C3%28") + "\u0634"
        self.assertRaisesRegex(ValueError, "invalid UTF-8", codecs.decode, bad, "arabica-2rs")
        self.assertEqual(codecs.decode(bad, "arabica-2rs", "replace"), "\ufffd(")
        # CHINZO-72C replaces pairs of letters by 5 Chinese characters, hence a text holding them is not decoded as it
        #  was
        self.assertEqual(codecs.decode(codecs.encode("\u8bb2 oo", "chinzo-72c"), "chinzo-72c"), "oo oo")
    
    def test_codec_hindia_korex(self):
        from codext.obfuscation.hindia4x import HINDIA
        hindia = {chr(int(code, 3)): s for code, s in HINDIA}
        # the characters are substituted in reverse order, HINDIA-4X inserting a space every 4 characters (ignored when
        #  decoding, as the other whitespaces)
        self.assertEqual(codecs.encode("test", "hindia-4x"), "".join(hindia[c] for c in "tset") + "\u09ad")
        self.assertEqual(codecs.encode("abcde", "hindia-4x").split(" ")[0], "".join(hindia[c] for c in "edcb"))
        for e in ["hindia-4x", "korex-3s"]:
            c = codecs.encode("Hello, World!", e)
            self.assertEqual(codecs.decode("\n".join(c.replace(" ", "")), e), "Hello, World!")
        # "\u0985\u0964" (the substitute of "5") is made of 2 characters, neither of them being a substitute
        self.assertEqual(codecs.decode("\u0985\u0964\u0985\u0964\u09ad", "hindia-4x"), "55")
        self.assertRaises(ValueError, codecs.decode, "\u0985\u09ad", "hindia-4x")
        self.assertEqual(codecs.decode("\u0985\u0964\u0985\u09ad", "hindia-4x", "replace"), "?5")
        # with a non-strict errors handling, malformed escape sequences are kept as is
        bad = "".join(hindia[c] for c in "%t") + "\u09ad"
        self.assertRaisesRegex(ValueError, "escape sequence", codecs.decode, bad, "hindia-4x")
        self.assertEqual(codecs.decode(bad, "hindia-4x", "ignore"), "t%")
        self.assertEqual(codecs.decode("\ud55cX \uc9c0", "korex-3s", "ignore"), "t")
        # HINDIA-4X replaces pairs of letters by 5 characters, hence a text holding them is not decoded as it was
        self.assertEqual(codecs.decode(codecs.encode("\u0259 ee", "hindia-4x"), "hindia-4x"), "ee ee")
    
    def test_codec_atbash(self):
        STR = "This is a test"
        ATB1 = "Gsrh rh z gvhg"
        self.assertIsNotNone(codecs.encode("test", "atbash-whatevers"))
        # uses by default an alphabet with lowercase and uppercase
        self.assertEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-?l?u"))
        self.assertNotEqual(codecs.encode(STR, "atbash"), codecs.encode(STR, "atbash-[?l?u]"))
        self.assertEqual(codecs.encode(STR, "atbash_cipher"), ATB1)
        self.assertEqual(codecs.encode(b(STR), "atbash-cipher"), b(ATB1))
        self.assertEqual(codecs.decode(ATB1, "atbash"), STR)
        self.assertEqual(codecs.decode(b(ATB1), "atbash"), b(STR))
        ATB2 = "N^]/a]/a a.{/."
        self.assertEqual(codecs.encode(STR, "atbash-[?l?u?p?s]"), ATB2)
        self.assertEqual(codecs.encode(b(STR), "atbash_cipher-[?l?u?p?s]"), b(ATB2))
        self.assertEqual(codecs.decode(ATB2, "atbash-[?l?u?p?s]"), STR)
        self.assertEqual(codecs.decode(b(ATB2), "atbash_cipher-[?l?u?p?s]"), b(STR))
    
    def test_codec_case_related_manips(self):
        STR = "This is a test"
        self.assertEqual(codecs.encode(STR, "lower"), "this is a test")
        self.assertEqual(codecs.encode(b(STR), "uppercase"), b("THIS IS A TEST"))
        self.assertEqual(codecs.encode(STR, "capitalize"), "This is a test")
        self.assertEqual(codecs.decode(b(STR), "capitalize"), b("this is a test"))
        self.assertEqual(codecs.encode(STR, "title"), "This Is A Test")
        self.assertEqual(codecs.decode(b(STR), "title"), b("this is a test"))
        self.assertEqual(codecs.encode(b(STR), "swapcase"), b("tHIS IS A TEST"))
        self.assertEqual(codecs.encode(b(STR), "camelcase"), b("thisIsATest"))
        self.assertEqual(codecs.encode(b(STR), "kebabcase"), b("this-is-a-test"))
        self.assertEqual(codecs.encode(b(STR), "pascalcase"), b("ThisIsATest"))
        self.assertEqual(codecs.encode(b(STR), "slugify"), b("this-is-a-test"))
        self.assertEqual(codecs.encode(b(STR), "snakecase"), b("this_is_a_test"))
        self.assertRaises(NotImplementedError, codecs.decode, STR, "camel")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "pascal")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "slug")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "snake")
    
    def test_codec_checksum_functions(self):
        from codext.checksums.crc import CRC
        for n, variants in CRC.items():
            for name, params in variants.items():
                enc = ("crc%d-%s" % (n, name) if isinstance(n, int) else "crc-%s" % name).rstrip("-")
                self.assertEqual(codecs.encode("123456789", enc), "%0{}x".format(round((n or 16)/4+.5)) % params[5])
        from codext.checksums.luhn import luhn
        for s, r in [("", ""), ("0", "0"), ("1", "8"), ("7992739871", "3")]:
            self.assertEqual(codecs.encode(s, "luhn"), r)
        self.assertEqual(codecs.encode("-", "luhn", errors="ignore"), "")
        # Fletcher, with the test vectors of Wikipedia ; the width defaults to 16
        for enc, vectors in {
            'fletcher|fletcher-16|fletcher_16|fletcher16': ["0000", "c8f0", "2057", "0627"],
            'fletcher32': ["00000000", "f04fc729", "56502d2a", "ebe19591"],
            'fletcher64': ["0000000000000000", "c8c6c527646362c6", "c8c72b276463c8c6", "312e2b28cccac8c6"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "abcde", "abcdef", "abcdefgh"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        self.assertRaises(LookupError, codecs.encode, "test", "fletcher8")
        self.assertRaises(NotImplementedError, codecs.decode, "c8f0", "fletcher")

    def test_codec_crc_bare_defaults(self):
        # a crc<width> used without a variant suffix must resolve to that family's default ;
        # width 16 and the crc-a family had no default and crashed with KeyError instead
        from codext.checksums.crc import CRC
        for n in CRC.keys():
            name = "crc%d" % n if isinstance(n, int) else "crc"
            expected = "%0{}x".format(round((n or 16)/4+.5)) % CRC[n][""][5]
            self.assertEqual(codecs.encode("123456789", name), expected)
            self.assertEqual(codecs.encode(b"123456789", name), b(expected))
        # bare crc-16 is CRC-16/ARC (poly 0x8005), the same as its arc/ibm/lha aliases
        for name in ["crc16", "crc-16", "crc_16", "crc16-arc", "crc16-ibm", "crc16-lha"]:
            self.assertEqual(codecs.encode("123456789", name), "bb3d")
        # bare crc is CRC-A, the same as the crca alias
        self.assertEqual(codecs.encode("123456789", "crc"), "bf05")
        self.assertEqual(codecs.encode("123456789", "crca"), "bf05")
        # adding a default must not make an unknown variant resolve
        self.assertRaises(LookupError, codecs.encode, "123456789", "crc16-bad")
        self.assertRaises(LookupError, codecs.encode, "123456789", "crc-bad")
    
    def test_codec_dummy_str_manips(self):
        STR = "this is a test"
        self.assertEqual(codecs.decode(STR, "reverse"), "tset a si siht")
        self.assertEqual(codecs.decode(STR, "reverse_words"), "siht si a tset")
        self.assertEqual(codecs.decode(STR.split()[0], "reverse"), codecs.decode(STR.split()[0], "reverse-words"))
        self.assertEqual(codecs.encode(STR, "replace-i1"), STR.replace("i", "1"))
        self.assertEqual(codecs.decode(STR.replace("i", "1"), "replace-1i"), STR)
        self.assertEqual(codecs.encode(STR, "substitute-this/that"), STR.replace("this", "that"))
        self.assertEqual(codecs.decode(STR.replace("this", "that"), "substitute-that/this"), STR)
        self.assertEqual(codecs.encode(STR, "tokenize-2"), "th is  i s  a  te st")
        self.assertRaises(LookupError, codecs.encode, STR, "tokenize-200")
    
    def test_codec_huffman(self):
        import heapq
        from collections import Counter
        # optimal codes: the length of the codes is the sum of the weights of the merged groups
        data = b"The quick brown fox jumps over the lazy dog " * 20
        enc = codecs.encode(data, "huffman")
        weights, total = list(Counter(data).values()), 0
        heapq.heapify(weights)
        while len(weights) > 1:
            w = heapq.heappop(weights) + heapq.heappop(weights)
            total += w
            heapq.heappush(weights, w)
        n = enc[0] + 1
        self.assertEqual(8 * (len(enc) - 2 - 2 * n) - enc[1 + 2 * n], total)
        # text with characters outside latin-1, and malformed data (truncated header, null code length, extra bits,
        #  missing payload) reported with a precise message, or replaced, dropped or left as is (as with gzip and zstd)
        self.assertEqual(codecs.decode(codecs.encode("caf\u00e9 \u20ac", "huffman"), "huffman"), "caf\u00e9 \u20ac")
        for bad, msg in [(b"\x01a", "truncated header"), (b"\x01a\x00b\x01\x05 ", "bad code length"),
                         (enc + b"\xff", "truncated code at the end"), (enc[:2 + 2 * n], "bad padding")]:
            self.assertRaisesRegex(ValueError, msg, codecs.decode, bad, "huffman")
            self.assertEqual(codecs.decode(bad, "huffman", "replace"), b"?")
            self.assertEqual(codecs.decode(bad, "huffman", "ignore"), b"")
            self.assertEqual(codecs.decode(bad, "huffman", "leave"), bad[:1])
        self.assertRaises(ValueError, codecs.decode, b"\x01a", "huffman", "BAD_ERRORS")
    
    def test_codec_zstd(self):
        try:
            from compression import zstd
        except ImportError:
            try:
                from backports import zstd
            except ImportError:
                self.skipTest("neither compression.zstd (Python 3.14+) nor backports.zstd is available")
        # a frame with a raw block (magic number, frame header with the content size, block header), levels and errors
        self.assertEqual(codecs.decode(b"\x28\xb5\x2f\xfd\x20\x04\x21\x00\x00test", "zstd"), b"test")
        data = b"This is a test " * 100
        self.assertLess(len(codecs.encode(data, "zstd-22")), len(data) // 10)
        self.assertEqual(zstd.decompress(codecs.encode(data, "zstd-19")), data)
        for e in ["zstd-0", "zstd-23"]:
            self.assertRaises(LookupError, codecs.encode, data, e)
        self.assertRaises(ValueError, codecs.decode, b"not zstd", "zstd")
        self.assertEqual(codecs.decode(b"not zstd", "zstd", "ignore"), b"")
        self.assertEqual(codecs.decode(b"not zstd", "zstd", "replace"), b"?")
    
    def test_codec_ctph(self):
        # ssdeep, with test vectors of libfuzzy 2.14.1 (including the truncation of the hashes and the halving of the
        #  block size), and CTPH, with test vectors of the ctph.js library (used by CyberChef)
        STR, NUMS = "This is a test string !", "".join(map(str, range(5000)))
        for s, r in [("", "3::"), ("a", "3:E:E"), (STR, "3:hMCEpFZnn:hurJn"),
                     (bytes(range(256)) * 64, "192:z" + "n" * 62 + "b:n"),
                     (NUMS, "384:Lpqp7xl6QPOGKs1iIhwCDHBmTSK0LLqg3vQkwvWgvVIy7uK:Fqp7eGt19HK7lhWoRaK")]:
            self.assertEqual(codecs.encode(s, "ssdeep"), r if isinstance(s, str) else b(r))
        for s, r in [("", "A::"), ("a", "A:F:F"), (STR, "A:4NUFkERB:4BMR"),
                     (NUMS, "H:NAYBrZvwMhar5zhGBT46wNd5dzzzuzj2TkzSvzFp9YBM70t:wYBrKrthAWzBTnFgx0t")]:
            self.assertEqual(codecs.encode(s, "ctph"), r)
        for e in ["ssdeep", "ctph"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
    
    def test_codec_gosthash(self):
        # Streebog (GOST R 34.11-2012), with the test vectors of CyberChef and the first example of RFC 6986 (whose
        #  message and hash codes are written in the reverse byte order)
        M1 = "012345678901234567890123456789012345678901234567890123456789012"
        QB = "The quick brown fox jumps over the lazy dog"
        vectors = {
            'gosthash|gosthash-256|gost-hash256|streebog|streebog_256': {
                '': "3f539a213e97c802cc229d474c6aa32a825a360b2a933a949fd925208d9ce1bb",
                QB: "3e7dea7f2384b6c5a3d0e24aaa29c05e89ddd762145030ec22c71a6db8b2c1f4",
                M1: "9d151eefd8590b89daa6ba6cb74af9275dd051026bb149a452fd84e5e57b5500",
            },
            'gosthash-512|gosthash512|streebog512': {
                '': "8e945da209aa869f0455928529bcae4679e9873ab707b55315f56ceb98bef0a7362f715528356ee83cda5f2aac4c6ad2b"
                    "a3a715c1bcd81cb8e9f90bf4c1c1a8a",
                QB: "d2b793a0bb6cb5904828b5b6dcfb443bb8f33efc06ad09368878ae4cdc8245b97e60802469bed1e7c21a64ff0b179a"
                    "6a1e0bb74d92965450a0adab69162c00fe",
                M1: "1b54d01a4af5b9d5cc3d86d68d285462b19abc2475222f35c085122be4ba1ffa00ad30f8767b3a82384c6574f024c311"
                    "e2a481332b08ef7f41797891c1646f48",
            },
        }
        for enc, v in vectors.items():
            for e in enc.split("|"):
                for s, r in v.items():
                    self.assertEqual(codecs.encode(s, e), r)
        LONG = "The quick brown fox jumps over the lazy dog. " * 3  # > 64 bytes, exercising the block loop
        self.assertEqual(codecs.encode(LONG, "gosthash-256"),
                         "ad3f8045baea445baa48f7ab2eb875ab76a32241972504e357f4771f85f36a45")
        self.assertEqual(codecs.encode(LONG, "gosthash-512"),
                         "85cba09c50849b2e2999ca9c190333e7844015d96057f44ab212169b7aae96c5"
                         "bafdcbaeebba2855fd7894b6b5f2e87dad7c3f68d27c10ebd85527785745465f")
        self.assertRaises(LookupError, codecs.encode, "test", "gosthash-128")
        self.assertRaises(NotImplementedError, codecs.decode, "test", "gosthash")
    
    def test_codec_hmac(self):
        # HMAC, with the second test case of RFC 2202 (MD5, SHA-1) and of RFC 4231 (SHA-2)
        D = "what do ya want for nothing?"
        for e, r in [("hmac-md5-Jefe", "750c783e6ab0b503eaa86e310a5db738"),
                     ("hmac_sha1_Jefe", "effcdf6ae5eb2fa2d27416d5f184df9c259a7c79"),
                     ("hmac-sha224-Jefe", "a30e01098bc6dbbf45690f3a7e9e6d0f8bbea2a39e6148008fd05e44"),
                     ("hmac-sha256-Jefe", "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"),
                     ("hmac-sha512-Jefe", "164b7a7bfcf819e2e395fbe73b56e0a387bd64222e831fd610270cd7ea2505549758bf75c05a99"
                                          "4a6d034f65f8f0e6fdcaeab1a34d4a6b4b636e070a38bce737")]:
            self.assertEqual(codecs.encode(D, e), r)
            self.assertEqual(codecs.encode(b(D), e), b(r))
        # the key is case-sensitive, may be made of digits (with leading zeros) or empty
        import hmac
        for k in ["Key", "1234", "0012", ""]:
            for algo in ["sha3_256", "blake2s"]:
                e = f"hmac-{algo.replace('_', '-')}" + (f"-{k}" if k else "")
                self.assertEqual(codecs.encode("test", e), hmac.new(k.encode(), b"test", algo).hexdigest())
        self.assertRaises(LookupError, codecs.encode, "test", "hmac-md4-key")
        self.assertRaises(NotImplementedError, codecs.decode, "test", "hmac-sha256-key")
    
    def test_codec_password_hashes(self):
        # LDAP, Cisco, PostgreSQL, Oracle, MS-CASH, MSSQL, phpass and the crypt(3) variants, with reference vectors of
        #  passlib (the salted hashes being made deterministic by fixing the random source)
        from unittest.mock import patch
        PW = "password"
        for e, r in [("ldap-md5", "{MD5}X03MO1qnZdYdgyfeuILPmQ=="),
                     ("ldap-sha1", "{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g="),
                     ("cisco-pix", "NuLKvvWGg.x9HEKO"), ("cisco-asa", "NuLKvvWGg.x9HEKO"),
                     ("cisco-pix-user", "A5XOy94YKDPXCo7U"), ("cisco-asa-user", "A5XOy94YKDPXCo7U"),
                     ("postgres-md5-admin", "md580a19f669b02edfbc208a5386ab5036b"),
                     ("oracle10-SYSTEM", "EED9B65CCECDB2E9"),
                     ("mscash-Administrator", "25fd08fa89795ed54207e6e8442a6ca0"),
                     ("mscash2-Administrator", "4c253e4b65c007a8cd683ea57bc43c76"),
                     ("bsd-nthash", "$3$$8846f7eaee8fb117ad06bdd830b7586c")]:
            self.assertEqual(codecs.encode(PW, e), r)
            self.assertEqual(codecs.encode(b(PW), e), b(r))
        # the username is case-sensitive and may be made of digits
        self.assertEqual(codecs.encode("secret", "postgres-md5-0012"),
                         codecs.encode("secret", "postgres_md5_0012"))
        # salted hashes: os.urandom is patched to yield the salts of the passlib reference vectors
        def fixed(data):
            return lambda n: data
        salted = [
            ("ldap-salted-md5", b"\x01\x02\x03\x04", "{SMD5}nXuh5+7dhsJMIAfcer5MygECAwQ="),
            ("ldap-salted-sha1", b"\x01\x02\x03\x04", "{SSHA}ouUZQtFbhkQrfIJ43qx176Wfj4YBAgME"),
            ("mssql2000", bytes.fromhex("01234567"),
             "0x010001234567B9A885497FAE83D470130CA23CBCA4639A9DF3BC1F93DA165CC051F59B15DD39FA68FA55DF187F83"),
            ("mssql2005", bytes.fromhex("01234567"), "0x010001234567B9A885497FAE83D470130CA23CBCA4639A9DF3BC"),
            ("oracle11", bytes.fromhex("0123456789ABCDEF0123"),
             "S:AE921ED081C9797AEB259E2A298E046290C3A5880123456789ABCDEF0123"),
            # phpass and the crypt variants map the random bytes to their alphabet, hence these byte values
            ("phpass-11", bytes([2, 3, 4, 5, 6, 7, 8, 9]), "$P$901234567wC.Gp1jHwxCOz6bwcNIEy0"),
            ("bigcrypt", bytes([38, 39]), "abJnggxhB/yWI"),
            ("crypt16", bytes([38, 39]), "abMi9VfflX1iMmF1QH4PEr.E"),
            ("bsdi-crypt-1001", bytes([38, 39, 40, 41]), "_dD..abcdX70A1RL1usU"),
            ("sun-md5-crypt-0", bytes([38, 39, 40, 41, 42, 43, 44, 45]), "$md5$abcdefgh$$ZxccX5lio58EZKsCI/Peg0"),
            ("sun-md5-crypt-100", bytes([38, 39, 40, 41, 42, 43, 44, 45]),
             "$md5,rounds=100$abcdefgh$$M/k9.q5540c7/LWDsTI8I."),
        ]
        for e, data, r in salted:
            with patch("os.urandom", fixed(data)):
                self.assertEqual(codecs.encode(PW, e), r)
        # the output of a salted hash differs between calls (random salt)
        self.assertNotEqual(codecs.encode(PW, "mssql2000"), codecs.encode(PW, "mssql2000"))
        for e in ["ldap-md5", "cisco-pix", "postgres-md5-x", "oracle10-x", "mscash-x", "mscash2-x", "mssql2000",
                  "mssql2005", "oracle11", "phpass", "bigcrypt", "crypt16", "bsdi-crypt", "bsd-nthash",
                  "sun-md5-crypt"]:
            self.assertRaises(NotImplementedError, codecs.decode, PW, e)
        # long passwords exercise the multi-block paths of bigcrypt and bsdi-crypt
        with patch("os.urandom", fixed(bytes([38, 39]))):
            self.assertEqual(codecs.encode("longpassword1234", "bigcrypt"), "abD6HAB6eqg.kjWpheVLzZOk")
        with patch("os.urandom", fixed(bytes([38, 39, 40, 41]))):
            self.assertEqual(codecs.encode("longpassword1234", "bsdi-crypt-5"), "_3...abcdzZpxxj5o8L.")
        # bad parameters
        self.assertRaises(LookupError, codecs.encode, PW, "phpass-6")
        self.assertRaises(LookupError, codecs.encode, PW, "bsdi-crypt-0")
        self.assertRaises(LookupError, codecs.encode, "a" * 17, "cisco-pix")
    
    def test_codec_argon2(self):
        # Argon2, through the argon2-cffi package (skipped when it is not installed)
        try:
            import argon2  # noqa: F401
        except ImportError:
            self.skipTest("argon2-cffi is not installed")
        for e, ident in [("argon2", "$argon2id$"), ("argon2i", "$argon2i$"), ("argon2d", "$argon2d$"),
                         ("argon2id", "$argon2id$")]:
            h = codecs.encode("password", e)
            self.assertTrue(h.startswith(ident + "v=19$"))
            # the hash validates the password it was made from, and the output is salted (differs between calls)
            self.assertTrue(argon2.PasswordHasher().verify(h, "password") if e in ("argon2", "argon2id") else True)
            self.assertNotEqual(codecs.encode("password", e), h)
        self.assertRaises(NotImplementedError, codecs.decode, "password", "argon2")
    
    def test_codec_hash_functions(self):
        STR = b"This is a test string!"
        for h in ["adler32", "md2", "md5", "sha1", "sha224", "sha256", "sha384", "sha512"]:
            self.assertIsNotNone(codecs.encode(STR, h))
            self.assertRaises(NotImplementedError, codecs.decode, STR, h)
        self.assertEqual(len(codecs.encode(STR, "blake2b_64")), 128)
        self.assertRaises(LookupError, codecs.encode, STR, "blake2b_0")
        self.assertRaises(LookupError, codecs.encode, STR, "blake2b-65")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "blake2b")
        self.assertEqual(len(codecs.encode(STR, "blake2s_32")), 64)
        self.assertRaises(LookupError, codecs.encode, STR, "blake2s_0")
        self.assertRaises(LookupError, codecs.encode, STR, "blake2s-33")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "blake2s")
        self.assertIsNotNone(codecs.encode(STR, "shake128"))
        self.assertRaises(LookupError, codecs.encode, STR, "shake128_0")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "shake128")
        self.assertIsNotNone(codecs.encode(STR, "shake256"))
        self.assertRaises(LookupError, codecs.encode, STR, "shake256-0")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "shake256")
        for h in ["sha3_224", "sha3_256", "sha3_384", "sha3_512"]:
            self.assertIsNotNone(codecs.encode(STR, h))
            self.assertRaises(NotImplementedError, codecs.decode, STR, h)
        # FNV, with test vectors of the reference implementation ; the hash of an empty string is the offset basis,
        #  and the width defaults to 32
        for enc, vectors in {
            'fnv1|fnv-1|fnv_1-32|fnv1_32': ["811c9dc5", "050c5d7e", "31f0b262"],
            'fnv1-64': ["cbf29ce484222325", "af63bd4c8601b7be", "340d8765a4dda9c2"],
            'fnv1a|fnv-1a|fnv_1a-32|fnv1a_32': ["811c9dc5", "e40c292c", "bf9cf968"],
            'fnv1a-64': ["cbf29ce484222325", "af63dc4c8601ec8c", "85944171f73967e8"],
            'fnv1a-128': ["6c62272e07bb014262b821756295c58d"],
            'fnv1-256': ["dd268dbcaac550362d98c384c4e576ccc8b1536847b6bbb31023b4c8caee0535"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "a", "foobar"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        self.assertEqual(len(codecs.encode(STR, "fnv1a-1024")), 256)
        self.assertRaises(LookupError, codecs.encode, STR, "fnv1-16")
        self.assertRaises(LookupError, codecs.encode, STR, "fnv1a-2048")
        self.assertRaises(NotImplementedError, codecs.decode, STR, "fnv1a")
        # SHA-0, Keccak (original padding) and MD6, with test vectors of the specifications and reference
        #  implementations
        for enc, vectors in {
            'sha0': ["f96cea198ad1dd5617ac084a3d92c6107708c0ef", "0164b8a914cd2a5e74c4f7ff082c4d97f1edf880"],
            'keccak|keccak256|keccak-256|keccak_256': [
                "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
                "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"],
            'keccak224': ["f71837502ba8e10837bdd8d365adb85591895602fc552b48b7390abd"],
            'keccak-384': ["2c23146a63a29acf99e73b88f8c24eaa7dc60aa771780ccc006afbfa8fe2479b"
                           "2dd2b21362337441ac12b515911957ff"],
            'keccak_512': ["0eab42de4c3ceb9235fc91acffe746b29c29a8c366b7c60e4e67c466f36a4304"
                           "c00fa9caf9d87976ba469bcbe06713b435f091ef2769fb160cdab33d3670680e"],
            'md6|md6256|md6-256|md6_256': ["bca38b24a804aa37d821d31af00f5598230122c5bbfc4c4ad5ed40e4258f04ca",
                                           "230637d4e6845cf0d092b558e87625f03881dd53a7439da34cf3b94ed0d8b2c5"],
            'md6-224': ["d2091aa2ad17f38c51ade2697f24cafc3894c617c77ffe10fdc7abcb",
                        "510c30e4202a5cdd8a4f2ae9beebb6f5988128897937615d52e6d228"],
            'md6-512': ["6b7f33821a2c060ecdd81aefddea2fd3c4720270e18654f4cb08ece49ccb469f"
                        "8beeee7c831206bd577f9f2630d9177979203a9489e47e04df4e6deaa0f8e0c0",
                        "00918245271e377a7ffb202b90f3bda5477d8feab12d8a3a8994ebc55fe6e74c"
                        "a8341520032eeea3fdef892f2882378f636212af4b2683ccf80bf025b7d9b457"],
        }.items():
            for e in enc.split("|"):
                for s, r in zip(["", "abc"], vectors):
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        # MD6 over several levels of its tree (8192 bytes, i.e. 16 blocks, then 4, then 1)
        self.assertEqual(codecs.encode(bytes(i & 0xff for i in range(8192)), "md6"),
                         b"2a40338156df221b18b20e4003f51f61284cacd01935e9e87414e6ae40a6bd25")
        self.assertEqual(len(codecs.encode(STR, "md6-8")), 2)
        for e in ["keccak-128", "keccak_1024", "md6-0", "md6-12", "md6-520"]:
            self.assertRaises(LookupError, codecs.encode, STR, e)
        for e in ["sha0", "keccak", "md6"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # RIPEMD-160 and Whirlpool, with test vectors of the specifications, through hashlib when available, and in
        #  pure Python (forced by making hashlib fail as with OpenSSL 3 without its legacy provider)
        from contextlib import nullcontext
        from unittest.mock import patch
        from codext.hashing.ripemd import ripemd160
        from codext.hashing.whirlpool import whirlpool
        vectors = {
            'ripemd160|ripemd-160|rmd160': {
                '': "9c1185a5c5e9fc54612808977ee8f548b2258d31",
                'abc': "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc",
                'message digest': "5d0689ef49d2fae572b881b123a85ffa21595f36",
            },
            'whirlpool': {
                '': "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a7"
                    "3e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3",
                'abc': "4e2448a4c6f486bb16b6562c73b4020bf3043e3a731bce721ae1b303d97e6d4c"
                       "7181eebdb6c57e277d0e34957114cbd6c797fc9d95d8b582d225292076d4eef5",
                'The quick brown fox jumps over the lazy dog':
                    "b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8d88e75c4fa854df36725f"
                    "d2b52eb6544edcacd6f8beddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35",
            },
        }
        for unavailable in [False, True]:
            with patch("hashlib.new", side_effect=ValueError) if unavailable else nullcontext():
                for enc, v in vectors.items():
                    for e in enc.split("|"):
                        for s, r in v.items():
                            self.assertEqual(codecs.encode(s, e), r)
                            self.assertEqual(codecs.encode(b(s), e), b(r))
        # multi-block inputs, around the padding boundaries
        for n in [55, 56, 63, 64, 65, 1000]:
            self.assertEqual(ripemd160(b"a" * n), codecs.encode(b"a" * n, "ripemd160").decode())
        # reference value computed with OpenSSL (legacy provider)
        self.assertEqual(whirlpool(b"a" * 1000), "fe24b173807796fdac15ebcaf5769f661695601ffeb64490ec0eecd30bd5b2c3"
                                                 "773b36d4edaf3175378b8df114e9496c833ef13606e7ab3d455681e98ecc818f")
        for e in ["ripemd160", "whirlpool"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # Snefru, with test vectors of crypto-api (used by CyberChef) for its four usual variants, and of PHP ("snefru"
        #  being Snefru-256 with 8 passes) around the block boundaries (blocks of 32 bytes for Snefru-256)
        for enc, v in {
            'snefru|snefru128|snefru-128-8': {'': "8617f366566a011837f4fb4ba5bedea2",
                                              '123456789\n': "6103721ccd8ad565d68e90b0f8906163"},
            'snefru-128-2|snefru128_2': {'': "b67224738c99d0ef185f2e971eb762ae",
                                         '123456789\n': "e699784944ed68a1c762ea1e90c77967"},
            'snefru256-4': {'': "5148516ae7fc7e89ad8e0b0b8d76ac782498615818fb8eeb08cbab9f07c82a73",
                            '123456789\n': "c22422491187baaa9472540008dffd5b38f015579f3f239050969991fdc1a810"},
            'snefru256|snefru_256|snefru-256-8': {
                '': "8617f366566a011837f4fb4ba5bedea2b892f3ed8b894023d16ae344b2be5881",
                '123456789\n': "4ca72639e40e9ab9c0c3f523c4449b3911632d374c124d7702192ec2e4e0b7a3",
                'The quick brown fox jumps over the lazy dog':
                    "674caa75f9d8fd2089856b95e93a4fb42fa6c8702f8980e11d97a142d76cb358",
                'a' * 62: "94682bc46e5fbb8417e2f3e10ed360484048d946bb8cbb0ea4cad2700dbeaab0",
                'a' * 63: "c54c602ac46383716ee7200a76c9c90a7b435bbe31d13f04e0b00a7ea5c347fa",
                'a' * 64: "7a8539c59e192e8d70b1ab82aa86a1b54560d42020bda4e00ddd6d048fe3bcaa",
            },
        }.items():
            for e in enc.split("|"):
                for s, r in v.items():
                    self.assertEqual(codecs.encode(s, e), r)
                    self.assertEqual(codecs.encode(b(s), e), b(r))
        for n in [32, 480]:
            self.assertEqual(len(codecs.encode(STR, f"snefru{n}")), n // 4)
        for e in ["snefru0", "snefru-100", "snefru512", "snefru128-1", "snefru128-9"]:
            self.assertRaises(LookupError, codecs.encode, STR, e)
        self.assertRaises(NotImplementedError, codecs.decode, STR, "snefru")
        # MD4 (through hashlib when available, and in pure Python), the Windows LM and NT hashes (with a DES test vector
        #  of the pure Python implementation) and the MySQL password hashes
        from codext.hashing.md import md4
        from codext.hashing.windows import des_encrypt
        vectors = {
            'md4': {'': "31d6cfe0d16ae931b73c59d7e0c089c0", 'abc': "a448017aaf21d8525fc10ae87aa6729d",
                    'message digest': "d9130a8164549fe818874806e1c7014b"},
            'lm|lmhash|lm-hash': {'': "aad3b435b51404eeaad3b435b51404ee",
                                  'password': "e52cac67419a9a224a3b108f3fa6cb6d",
                                  'Password1234567890': "e52cac67419a9a22c41a0e2828864838"},
            'ntlm|nt|nthash|nt-hash': {'': "31d6cfe0d16ae931b73c59d7e0c089c0",
                                       'password': "8846f7eaee8fb117ad06bdd830b7586c"},
            'mysql323|mysql-3.23|mysql3': {'mypass': "6f8c114b58f2ce9e", 'pass word': "5d2e19393cc5ef67"},
            'mysql41|mysql-4.1|mysql4': {'password': "*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19"},
        }
        for unavailable in [False, True]:
            with patch("hashlib.new", side_effect=ValueError) if unavailable else nullcontext():
                for enc, v in vectors.items():
                    for e in enc.split("|"):
                        for s, r in v.items():
                            self.assertEqual(codecs.encode(s, e), r)
                            self.assertEqual(codecs.encode(b(s), e), b(r))
        for n in [55, 56, 63, 64, 65, 1000]:
            self.assertEqual(md4(b"a" * n), codecs.encode(b"a" * n, "md4").decode())
        self.assertEqual(des_encrypt(bytes.fromhex("133457799bbcdff1"), bytes.fromhex("0123456789abcdef")).hex(),
                         "85e813540f0ab405")
        for e in ["md4", "lm", "ntlm", "mysql323", "mysql41"]:
            self.assertRaises(NotImplementedError, codecs.decode, STR, e)
        # bcrypt, with a test vector of OpenWall's crypt_blowfish (salt decoded from its base64 alphabet), through the
        #  bcrypt package when installed, and in pure Python (forced by making its import fail)
        import sys
        from codext.hashing.bcrypt import _b64, bcrypt, BCRYPT_B64
        salt = int("".join(f"{BCRYPT_B64.index(c):06b}" for c in "CCCCCCCCCCCCCCCCCCCCC."), 2) >> 4
        salt = salt.to_bytes(16, "big")
        self.assertEqual(_b64(salt), "CCCCCCCCCCCCCCCCCCCCC.")
        self.assertEqual(_b64(bcrypt("U*U", salt, 5)), "E5YPO9kmyuRGyh0XouQYb4YMJKvyOeW")
        for unavailable in [False, True]:
            with patch.dict(sys.modules, {'bcrypt': None}) if unavailable else nullcontext():
                for e, c in [("bcrypt-4", "04"), ("bcrypt_5", "05")]:
                    h = codecs.encode(STR.decode(), e)
                    self.assertRegex(h, rf"^\$2b\${c}\$[./A-Za-z0-9]{{53}}$")
                    self.assertNotEqual(h, codecs.encode(STR.decode(), e))
        for e in ["bcrypt-3", "bcrypt-32"]:
            self.assertRaises(LookupError, codecs.encode, STR, e)
        self.assertRaises(NotImplementedError, codecs.decode, STR, "bcrypt")
        if UNIX:
            try:
                import crypt
            except ImportError:
                try:
                    import legacycrypt as crypt
                except ImportError:
                    crypt = None
            METHODS = [x[7:].lower() for x in crypt.__dict__ if x.startswith("METHOD_")] \
                      if crypt is not None else []
            for m in METHODS:
                self.assertIsNotNone(codecs.encode(STR, h := f"crypt-{m}"))
                self.assertRaises(NotImplementedError, codecs.decode, STR, h)
    
    def test_codec_fancy_upsidedown(self):
        import unicodedata
        from string import ascii_letters, digits
        from codext.languages.fancy import ALPHABETS
        from codext.languages.upsidedown import _PAIRS, UPSIDE_DOWN, _VARIANTS
        # complete alphabets (with the letters of the Letterlike Symbols block, e.g. "\u212c" for the script B), each
        #  styled character being decoded back
        math = [s for s in ALPHABETS if s not in ("circled", "parenthesized", "fullwidth", "smallcaps")]
        for style in math + ["circled", "parenthesized"]:
            self.assertTrue(all(c in ALPHABETS[style] for c in ascii_letters))
        self.assertEqual(ALPHABETS["script"]["B"], "\u212c")
        self.assertEqual(ALPHABETS["italic"]["h"], "\u210e")
        self.assertEqual(ALPHABETS["double-struck"]["R"], "\u211d")
        self.assertEqual(sorted(s for s in math if "0" in ALPHABETS[s]),
                         ["bold", "double-struck", "monospace", "sans-serif", "sans-serif-bold"])
        self.assertNotIn("x", ALPHABETS["smallcaps"])
        text = "The quick brown fox jumps over the lazy dog 0123456789"
        # the NFKC normalization also undoes the mathematical, circled and full-width styles, but not the parenthesized
        #  one, the small capitals and the upside-down text
        for style in ALPHABETS:
            enc = codecs.encode(text, f"fancy-{style}")
            self.assertEqual(codecs.decode(enc, f"fancy-{style}"), text)
            self.assertEqual(codecs.decode(enc, "fancy"), text)
            self.assertEqual(unicodedata.normalize("NFKC", enc) == text, style not in ("parenthesized", "smallcaps"))
        self.assertNotEqual(unicodedata.normalize("NFKC", codecs.encode(text, "upsidedown")), text)
        # a style is required for encoding, while decoding without a style handles mixed styles
        self.assertRaises(LookupError, codecs.encode, text, "fancy")
        mixed = "".join(codecs.encode(c, f"fancy-{s}") for c, s in zip("Hello", ALPHABETS))
        self.assertEqual(codecs.decode(mixed, "fancy"), "Hello")
        # small capitals for the lowercase letters only (there is no small capital x)
        self.assertEqual(codecs.encode("Mixed CASE x", "smallcaps"), "M\u026ax\u1d07\u1d05 CASE x")
        # upside-down: pairs of turned characters, used in both directions (turning twice gives the text back), and
        #  the other turned versions of the online generators being decoded
        self.assertEqual(len({c for p in _PAIRS for c in p}), 2 * len(_PAIRS))
        for c in UPSIDE_DOWN:
            if c not in _VARIANTS:
                self.assertEqual(UPSIDE_DOWN[UPSIDE_DOWN[c]], c)
        self.assertEqual(codecs.decode("\u2229\u02e5\ua7fd\u2200", "upsidedown"), "AMLU")
        self.assertEqual(codecs.decode(codecs.encode(text, "upsidedown"), "upsidedown"), text)
        self.assertEqual(codecs.encode(b"Hi!", "upside-down"), "\u00a1\u1d09H".encode("utf-8"))
    
    def test_codec_markdown(self):
        HTM = "<h1>Test title</h1>\n\n<p>Test paragraph</p>\n"
        MD  = "# Test title\n\nTest paragraph"
        TFILE = "test-codec-markdown.html"
        self.assertTrue(isinstance(codecs.encode(MD, "markdown"), str))
        self.assertEqual(codecs.encode(MD, "markdown"), HTM)
        self.assertRaises(NotImplementedError, codecs.decode, MD, "markdown")
        with codecs.open(TFILE, 'w', encoding="markdown") as f:
            f.write(b(MD))
        with codecs.open(TFILE) as f:
            s = f.read()
        self.assertEqual(HTM, ensure_str(s))
        os.remove(TFILE)
    
    def test_codec_tap(self):
        # with a non-strict errors handling, unsupported characters are replaced or ignored, and a word separator
        #  between the row and the column of a letter drops the letter
        self.assertEqual(codecs.encode("a!b", "tap", "replace"), ". .  ?  . ..")
        self.assertEqual(codecs.encode("a!b", "tap", "ignore"), ". .  . ..")
        self.assertEqual(codecs.decode(". / . ..", "tap", "ignore"), " b")
    
    def test_codec_unicode_tags(self):
        # decoding ignores the cover text, hence the hidden message can be inserted anywhere in it
        hidden = codecs.encode("ignore previous instructions", "unicode-tags")
        self.assertEqual(codecs.decode("Please summarize " + hidden + "this.", "unicode-tags"),
                         "ignore previous instructions")
        # the replacement character is hidden too, so that it survives decoding
        replaced = codecs.encode("Caf\u00e9!", "unicode-tags", "replace")
        self.assertEqual(codecs.decode(replaced, "unicode-tags"), "Caf?!")
        # the BEGIN and CANCEL tags are only stripped by the wrapped variant
        wrapped = codecs.encode("Hi", "unicode-tags-wrapped")
        self.assertEqual(codecs.decode(wrapped, "unicode-tags"), "\x01Hi\x7f")
        self.assertEqual(codecs.decode(wrapped, "unicode-tags-wrapped"), "Hi")

    def test_codec_whitespace_after_before(self):
        STR = "test"
        for i in range(100):
            c = "whitespace{}{}*after{}{}*before".format("-+"[random.randint(0, 1)], random.randint(1, 3),
                                                         "-+"[random.randint(0, 1)], random.randint(1, 3))
            self.assertEqual(codecs.decode("\n" + codecs.encode(STR, c) + "\n", c), STR)
        # in this special case, the whitespaces between words cannot be encoded because:
        # - ord(" ") == 32
        # - the next minimal value in the printable characters excluding the latest 6 is ord("!") == 33
        # and therefore ord(" ")-random(0,20)-random(0,20) will never fall into the valid ordinals !
        self.assertRaises(ValueError, codecs.encode, "this is a test", "whitespace-after-before")
        self.assertIn("\x00", codecs.encode("this is a test", "whitespace-after-before", "replace"))
        # characters that no number of spaces can shift to a printable one (this used to loop forever)
        for c in ["\xff", chr(0x141)]:
            self.assertEqual(codecs.decode(codecs.encode("A" + c + "B", "whitespace+after-before", "ignore"),
                                           "whitespace+after-before"), "AB")
        self.assertRaises(ValueError, codecs.encode, "A\xff", "whitespace-2*after+3*before")
        # a division gives non-integer shifts (or divides by zero spaces), hence nothing can be encoded
        self.assertRaises(ValueError, codecs.encode, "A", "whitespace+2/after-before")
        # a line holding more than one character is not decoded at all
        self.assertEqual(codecs.decode(" A \nBC\n D", "whitespace+after-before", "ignore"),
                         codecs.decode(" A \n D", "whitespace+after-before"))

    def test_codec_zero_width(self):
        self.assertRaises(LookupError, codecs.encode, "test", "zero-width-4")
        # decoding ignores the cover text, hence the hidden message can be inserted anywhere in it
        hidden = codecs.encode("secret", "zero-width")
        self.assertEqual(codecs.decode("Nothing " + hidden + "to see here.", "zero-width"), "secret")
        # an invalid UTF-8 byte (0xff) followed by a valid message
        bad = chr(0x200c) * 8 + codecs.encode("ok", "zero-width")
        self.assertEqual(codecs.decode(bad, "zero-width", "replace"), "?ok")
        self.assertEqual(codecs.decode(bad, "zero-width", "ignore"), "ok")
        # code points above 5**7 cannot be encoded with the quinary variant
        STR = "A" + chr(0x1f600) + "B"
        self.assertEqual(codecs.encode(STR, "zero-width-full", "ignore"), codecs.encode("AB", "zero-width-full"))
        self.assertIn(chr(0x1f600), codecs.encode(STR, "zero-width-full", "leave"))
    
    def test_codec_xxencode(self):
        # a bad length character is reported, the number of bytes then being guessed from the length of the line
        self.assertEqual(codecs.decode("!Eq3o", "xx", "ignore"), "Cat")
        # an invalid group of 4 characters is handled as a whole (length "4" means 6 bytes)
        self.assertEqual(codecs.decode("4Eq!oEq3o", "xx", "replace"), "?Cat")
        self.assertEqual(codecs.decode("4Eq!oEq3o", "xx", "ignore"), "Cat")
