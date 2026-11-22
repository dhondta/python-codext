# -*- coding: UTF-8 -*-
"""Analyze feature - describe the statistical properties of an input.

This reports properties of an input that tell what it may be before trying to decode it, as FeatherDuster's analysis
 does (https://github.com/nccgroup/featherduster): its alphabet (e.g. hexadecimal or Base64 characters only), its
 randomness (entropy, byte mean and distribution, compression ratio, longest run of bits, Monte Carlo estimate of Pi),
 a known file signature, repeated blocks (e.g. from a block cipher in ECB mode), the hashes of the same length and, for
 letters, the index of coincidence and the fit of their frequencies with a text (telling a transposition, a Caesar
 cipher, another monoalphabetic substitution or a polyalphabetic one such as Vigenere, with its likely key length).

It returns these properties with a list of human-readable hints, e.g. that the input looks like random or encrypted
 data, on which guessing is pointless. It only depends on ``text`` and ``utils`` (it is not used by the guess feature).
"""
import re
import zlib
from collections import Counter

from .text import LETTER_FREQUENCIES, _letter_frequencies, _textness, entropy
from .utils import b, codecs, ensure_str, PRINTABLES


__all__ = ["analyze"]

# alphabets (as sets of characters, whitespaces being ignored), from the smallest to the largest ; the first one holding
#  all the characters of the input is reported
_B = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALPHABETS = [
    ("binary digits", set("01")),
    ("octal digits", set("01234567")),
    ("decimal digits", set("0123456789")),
    ("hexadecimal", set("0123456789ABCDEF")),
    ("hexadecimal", set("0123456789abcdef")),
    ("Base32", set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=")),
    ("Base32", set("abcdefghijklmnopqrstuvwxyz234567=")),
    ("Base32-hex", set("0123456789ABCDEFGHIJKLMNOPQRSTUV=")),
    ("letters", set(_B[10:])),
    ("Base58", set(_B) - set("0OIl")),
    ("Base62 (alphanumeric)", set(_B)),
    ("Base64", set(_B + "+/=")),
    ("Base64-url", set(_B + "-_=")),
    ("Ascii85", set(map(chr, range(33, 118))) | {"z"}),
    ("printable characters", set(map(chr, range(32, 127)))),
]
# hashes by length of their digest (in bytes)
HASHES = {16: "MD4, MD5, NTLM", 20: "SHA1, RIPEMD-160", 28: "SHA224, SHA3-224", 32: "SHA256, SHA3-256, BLAKE2s",
          48: "SHA384, SHA3-384", 64: "SHA512, SHA3-512, BLAKE2b, Whirlpool"}
# file signatures (magic bytes) of the most common compressed, archive and binary formats
SIGNATURES = [
    (b"\x1f\x8b", "gzip"), (b"BZh", "bzip2"), (b"\xfd7zXZ\x00", "xz"), (b"\x5d\x00\x00", "lzma"),
    (b"\x28\xb5\x2f\xfd", "zstd"), (b"\x04\x22\x4d\x18", "lz4"), (b"PK\x03\x04", "zip"), (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"Rar!\x1a\x07", "rar"), (b"\x89PNG\r\n\x1a\n", "PNG"), (b"\xff\xd8\xff", "JPEG"), (b"GIF8", "GIF"),
    (b"%PDF-", "PDF"), (b"\x7fELF", "ELF"), (b"MZ", "PE (Windows executable)"), (b"\xca\xfe\xba\xbe", "Java class"),
    (b"Salted__", "OpenSSL encrypted data"),
]
# index of coincidence of English texts (letters only) and of random letters
IC_TEXT, IC_RANDOM = .0667, 1 / 26
# mean letter frequency of a text (in %), that is, the sum of the squared frequencies of its letters
LF_TEXT = sum(f * f for f in LETTER_FREQUENCIES) / 100


def _alphabet(text):
    """ Name of the smallest known alphabet holding all the characters of the given text (whitespaces ignored). """
    chars = set(re.sub(r"\s", "", text))
    if len(chars) == 0:
        return
    return next((name for name, alphabet in ALPHABETS if chars <= alphabet), None)


def _index_of_coincidence(letters):
    """ Probability that two letters drawn from the given letters are equal (None if less than 2 letters). """
    if (n := len(letters)) < 2:
        return
    return sum(c * (c - 1) for c in Counter(letters).values()) / (n * (n - 1))


def _key_length(letters, max_length=20):
    """ Estimate the key length of a polyalphabetic substitution (e.g. Vigenere) as the smallest period whose columns
         (the letters taken every period letters, each one being enciphered with a single shift) have a mean index of
         coincidence closer to the one of a text than to the one of random letters (None if the letters themselves
         are distributed as in a text, or if no period fits). """
    threshold = (IC_TEXT + IC_RANDOM) / 2
    if (ioc := _index_of_coincidence(letters)) is None or ioc >= threshold:
        return
    for k in range(2, min(max_length, len(letters) // 5) + 1):
        if sum(_index_of_coincidence(letters[i::k]) for i in range(k)) / k >= threshold:
            return k


def _letter_shift(freqs):
    """ Shift N whose decoding (rot-N) distributes the letters the most as in a text, with the fit of this distribution
         (its mean letter frequency divided by the one of a text, capped to 1 ; random letters fit around .6). """
    if freqs is None:
        return 0, 0.
    k = max(range(26), key=freqs[1].__getitem__)
    return (26 - k) % 26, min(1., freqs[1][k] / LF_TEXT)


def _mostly_letters(n_letters, text, alphabet):
    """ Whether a text is mostly made of letters (at least 20, and half of its characters other than whitespaces), not
         in the alphabet of a known encoding (e.g. Base64), hence possibly the ciphertext of a classical cipher. """
    return n_letters >= 20 and n_letters >= .5 * len(re.sub(r"\s", "", text)) and \
           alphabet in (None, "letters", "printable characters")


def _monte_carlo_pi(data):
    """ Estimate Pi from the successive pairs of 24-bit coordinates taken from the data, as the ratio of the points that
         fall in the quarter circle (close to Pi for random data, as the "ent" tool does). """
    pts = [(int.from_bytes(data[i:i+3], "big"), int.from_bytes(data[i+3:i+6], "big")) for i in
           range(0, len(data) - 5, 6)]
    if len(pts) == 0:
        return
    r = (2 ** 24 - 1) ** 2
    return 4 * sum(x * x + y * y <= r for x, y in pts) / len(pts)


def _repeated_blocks(data):
    """ Number of repeated blocks of 8 and 16 bytes, for the block sizes that divide the length of the data. """
    r = {}
    for bs in (8, 16):
        if len(data) % bs == 0 and len(data) >= 2 * bs:
            blocks = [data[i:i+bs] for i in range(0, len(data), bs)]
            if (n := len(blocks) - len(set(blocks))) > 0:
                r[bs] = n
    return r


def _hints(r, raw, text):
    """ Interpret the properties of the analysis as human-readable hints. """
    h, n, alph = [], r['length'], r['alphabet']
    if n == 0:
        return ["The input is empty"]
    if r['signature']:
        h.append(f"It starts with the signature of {r['signature']} data")
    if r['hashes']:
        h.append(f"It has the length of a hash digest ({r['hashes']})")
    if alph and alph not in ("letters", "printable characters"):
        h.append(f"It only holds {alph} characters, hence it may be encoded with it")
    # random or encrypted data: incompressible binary data (as the entropy of a short input stays below 8 bits per byte
    #  even if random, it is not considered)
    if n >= 64 and r['compression_ratio'] >= .98 and r['printables'] < .9 and not r['signature']:
        h.append("It looks random: encrypted or random data (or compressed data without header), hence guessing an "
                 "encoding is unlikely to help")
    elif r['compression_ratio'] < .5 and n >= 64:
        h.append("It is highly compressible, hence it holds a lot of redundancy (e.g. a text or an encoding of it)")
    if r['repeated_blocks']:
        bs = min(r['repeated_blocks'])
        h.append(f"It holds {r['repeated_blocks'][bs]} repeated block(s) of {bs} bytes, as a block cipher in ECB mode "
                 "gives for repeated plaintext blocks")
    # letters: text, transposition, Caesar shift, monoalphabetic or polyalphabetic substitution
    if r['textness'] >= .5:
        h.append("It looks like a natural language text")
    elif _mostly_letters(r['letters'], text, alph):
        ioc, (shift, fit) = r['index_of_coincidence'], r['letter_shift']
        if ioc >= .055 and shift == 0 and fit >= .9:
            h.append("Its letters are distributed as in a text but do not form words, as with a transposition cipher "
                     "(e.g. columnar, railfence, scytale)")
        elif ioc >= .055 and fit >= .9:
            h.append(f"Its letters are distributed as in a text once shifted, as with a Caesar cipher (decoded with "
                     f"rot-{shift})")
        elif ioc >= .055:
            h.append("Its letters are distributed as in a text but substituted, as with a monoalphabetic substitution "
                     "(e.g. atbash, affine or a keyed alphabet)")
        elif ioc < .05:
            k = r['key_length']
            h.append("Its letters are evenly distributed, as with a polyalphabetic substitution (e.g. vigenere)" +
                     (f" whose key would be {k} letters long" if k else ""))
    return h


def analyze(data):
    """ Analyze the given input (str or bytes) and return a dictionary with its properties and a list of hints:

    - length:              length in bytes (a str being taken as UTF-8)
    - alphabet:            name of the smallest known alphabet holding all its characters (whitespaces ignored), if any
    - printables:          rate of printable characters
    - entropy:             Shannon entropy of its bytes (in bits per byte, 8 at most)
    - mean:                mean of its bytes (127.5 for random data)
    - chi_square:          chi-square of the distribution of its bytes (close to 255 for random data)
    - compression_ratio:   length of its zlib compression divided by its length (close to or above 1 for random data)
    - longest_bit_run:     length of the longest run of identical bits
    - monte_carlo_pi:      Monte Carlo estimate of Pi from its bytes (close to Pi for random data)
    - signature:           format of the file signature it starts with, if any (e.g. gzip)
    - hashes:              hashes whose digest has its length (in bytes, or in hexadecimal characters), if any
    - repeated_blocks:     numbers of repeated blocks by block size (8 or 16 bytes, if it is a multiple of it)
    - letters:             number of Latin letters
    - index_of_coincidence: index of coincidence of its letters (.0667 for English texts, .0385 for random letters)
    - letter_shift:        shift N (0 to 25) whose decoding (rot-N) distributes its letters the most as in a text,
                            with how well they then fit the letter frequencies of a text (from 0 to 1, random letters
                            fitting around .6)
    - key_length:          estimated key length of a polyalphabetic substitution of its letters (e.g. Vigenere), if any
    - textness:            how much it looks like a natural language text (from 0 to 1)
    - hints:               human-readable interpretations of these properties """
    raw = b(data) if isinstance(data, str) else bytes(data)
    if isinstance(raw, str):
        raw = raw.encode("utf-8", errors="surrogatepass")
    text, n = ensure_str(data), len(raw)
    counts = Counter(raw)
    letters = [ord(c) - 97 for c in text.lower() if "a" <= c <= "z"]
    f, alph = _letter_frequencies(text, False), _alphabet(text)
    stripped = re.sub(r"\s", "", text)
    if alph and alph.startswith("hexadecimal") and len(stripped) % 2 == 0:
        hashes = HASHES.get(len(stripped) // 2)
    else:
        hashes = HASHES.get(n) if n > 0 and len(counts) >= n // 2 and alph in (None, "printable characters") else None
    r = {
        'length':            n,
        'alphabet':          alph,
        'printables':        sum(c in PRINTABLES for c in text) / len(text) if text else 0.,
        'entropy':           entropy(raw) if n > 0 else 0.,
        'mean':              sum(raw) / n if n > 0 else 0.,
        'chi_square':        sum((counts[i] - n / 256) ** 2 / (n / 256) for i in range(256)) if n > 0 else 0.,
        'compression_ratio': len(zlib.compress(raw, 9)) / n if n > 0 else 0.,
        'longest_bit_run':   max(map(len, re.findall("0+|1+", "".join(f"{x:08b}" for x in raw))), default=0),
        'monte_carlo_pi':    _monte_carlo_pi(raw),
        'signature':         next((name for sig, name in SIGNATURES if raw.startswith(sig)), None),
        'hashes':            hashes,
        'repeated_blocks':   _repeated_blocks(raw),
        'letters':           len(letters),
        'index_of_coincidence': _index_of_coincidence(letters),
        'letter_shift':      _letter_shift(f),
        'key_length':        _key_length(letters) if _mostly_letters(len(letters), text, alph) else None,
        'textness':          _textness(text) if n > 0 else 0.,
    }
    r['hints'] = _hints(r, raw, text)
    return r


def report(r):
    """ Format the result of the analysis for the terminal. """
    if not isinstance(r, dict):
        r = analyze(r)
    fmt = lambda v: "-" if v is None or v == {} else f"{v:.4f}" if isinstance(v, float) else \
                    ", ".join(f"{k}: {x}" for k, x in v.items()) if isinstance(v, dict) else \
                    f"rot-{v[0]} (fit: {v[1]:.2f})" if isinstance(v, tuple) else str(v)
    lines = [f"{k.replace('_', ' '):<21}: {fmt(v)}" for k, v in r.items() if k != "hints"]
    return "\n".join(lines + [""] + [f"[*] {h}." for h in r['hints']])


codecs.analyze = analyze
codecs.analyze_report = report
