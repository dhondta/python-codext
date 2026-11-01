# -*- coding: UTF-8 -*-
"""Text rating functions - how much a string looks like a natural language text.

This module holds the entropy and the "textness" rating used by the guess feature (``guess``, ``rank`` and the
 ``text_strict`` stop function) to score the decoded outputs. It only depends on ``utils``.
"""
import re
import unicodedata
from collections import Counter
from math import log

from .utils import b, ensure_str, PRINTABLES


__all__ = ["entropy", "TEXTNESS_THRESHOLD", "TEXTNESS_WEIGHT"]

# scoring of the decoded outputs: textness above which an output is considered as a text, and weight of its bonus
TEXTNESS_THRESHOLD, TEXTNESS_WEIGHT = .5, 4
# most common bigrams of English texts (a large part being common to other Latin-script languages)
BIGRAMS = frozenset("th he in er an re on at en nd ti es or te of ed is it al ar st to nt ng se ha as ou io le ve co "
                    "me de hi ri ro ic ne ea ra ce li ch ll be ma si om ur ca el ta la ns di fo ho pe ec pr no ct us "
                    "ac ot il tr ly nc et ut ss so rs un lo wa ge ie wh ee wi em ad ol rt po we na ul ni ts mo ow pa "
                    "im mi ai sh".split())
# most common function words of Latin-script languages (English, French, German, Spanish, Italian, Dutch, Portuguese
#  and Latin, as lorem ipsum is a common test text) ; unlike the bigrams, reversed, they reveal a reversed text
STOPWORDS = frozenset("the and of to in is it that for on with as was are be by at or this from an not but have you "
                      "le la les de des du et un une est en que qui dans pour pas sur au il elle "
                      "der die das und ist ein eine zu den mit von nicht sich auf dem des im "
                      "el los las del se por con una para es al lo como su "
                      "il di che non per con sono della una gli le "
                      "het een van dat en op te zijn voor met niet "
                      "os da do em um uma com para por no na "
                      "et in ut ad non est sed cum ex qui quis sit nec aut".split())
# the words that remain function words in a reversed text are left out (palindromes, e.g. "non", and pairs, e.g. "on"
#  and "no")
STOPWORDS = frozenset(w for w in STOPWORDS if w[::-1] not in STOPWORDS)
# a clean word of a text: letters (with an eventual apostrophe, e.g. "don't") or a number (e.g. "1,234.56" or "50%")
TOKEN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?|[$€£]?\d[\d.,:/]*%?")
# scripts of the letters (cache) and scripts whose words are not separated by spaces
SCRIPTS, SCRIPTS_WITHOUT_SPACES = {}, {"CJK", "HIRAGANA", "KATAKANA", "THAI", "LAO", "KHMER", "MYANMAR", "TIBETAN"}


def entropy(s):
    """ Shannon entropy of the given string or bytes, counting the characters in a single pass. """
    n, l = Counter(s), len(s)
    return -sum([p * log(p, 2) for p in [n[c] / l for c in set(s)]])


def _script(c):
    """ Get the script of a letter (e.g. "LATIN", "CYRILLIC" or "CJK"), from its Unicode name. """
    try:
        return SCRIPTS[c]
    except KeyError:
        SCRIPTS[c] = r = unicodedata.name(c, "?").split()[0]
        return r


def _clean_token(w):
    """ Check whether a token (once stripped of its trailing punctuation and its surrounding quotes or brackets) is a
         word or a number. """
    w = w.strip("\"'()[]{}").rstrip(".,;:!?").strip("\"'()[]{}")
    return TOKEN.fullmatch(w) is not None and (w[0].isdigit() or w[0] in "$€£" or w.islower() or w.isupper() or
                                               w.istitle())


def _textness(s, any_script=True):
    """ Rate in [0, 1] how much the given string looks like a natural language text.
    
    For a text mostly made of Latin letters, this is mainly the rate of common bigrams among the pairs of successive
     letters (around 70% for English texts, against around 15% for random letters), weighted by the rates of printable
     characters and of letters and spaces (a text is mostly made of them, at least 60%), by the number of distinct
     letters (a text uses many letters, unlike e.g. digits shifted to letters), by the length of its words and by its
     reversed function words (stopwords) ; this distinguishes a text from a substitution of its letters (e.g. ROT13)
     and from a rearrangement of them (e.g. a reversed text).
    For a text in another script (e.g. Cyrillic, Greek or CJK), this only relies on language-independent features: the
     rate of letters of the dominant script among the letters, the rate of letters, spaces and punctuation, the number
     of distinct letters and the length of the words (for the scripts that separate words with spaces) ; as these
     features cannot distinguish a text from a substitution of its characters, this can be disabled
     (any_script=False), then rating 0. """
    # a decoded output may hold the UTF-8 bytes of a text as Latin-1 characters
    s = ensure_str(b(s))
    if (n := len(s)) < 2:
        return 0.
    letters = [c for c in s if c.isalpha()]
    if len(letters) == 0:
        return 0.
    scripts = Counter(map(_script, letters))
    script, count = scripts.most_common(1)[0]
    if script != "LATIN":
        if not any_script:
            return 0.
        printables = sum(c.isprintable() or c.isspace() for c in s) / n
        rate = sum(c.isalpha() or c.isspace() or unicodedata.category(c)[0] == "P" for c in s) / n
        distinct = min(1., len(set(letters)) / min(10., len(letters) / 2))
        r = printables * (count / len(letters)) ** 2 * rate * distinct
        if script not in SCRIPTS_WITHOUT_SPACES:
            # the mean length of the words is around 5 letters
            words = s.split()
            r *= 1. if 2 <= len(letters) / len(words) <= 12 else .3
        return r
    t = s.lower()
    pairs = [t[i:i+2] for i in range(n - 1) if t[i].isalpha() and t[i+1].isalpha()]
    if len(pairs) == 0:
        return 0.
    bigrams = min(1., sum(map(BIGRAMS.__contains__, pairs)) / len(pairs) / .7)
    printables, rate = sum(map(PRINTABLES.__contains__, s)) / n, sum(c.isalpha() or c == " " for c in s) / n
    # a text holds at least 10 distinct letters (or half of its letters if shorter), unlike e.g. digits shifted to
    #  letters
    distinct = set(c for c in t if c.isalpha())
    expected = min(10., len(letters) / 2)
    r = printables * bigrams * min(1., rate / .6) * min(1., len(distinct) / expected)
    # the words of a text (separated by spaces, or by underscores or hyphens as in identifiers or flags) are around 5
    #  letters long, unlike e.g. digits shifted to letters or a keyboard shift of an encoded string
    tokens = [w for w in re.split(r"[\s_\-]+", t) if w]
    if len(letters) >= 16 and len(letters) / len(tokens) > 12:
        r *= .3
    # most of these words (weighted by their lengths, as short tokens are trivially words) are made of letters only, in
    #  lowercase, capitalized or uppercase (or are numbers), once stripped of their punctuation, unlike the tokens of
    #  e.g. an encoded string that happens to contain separators
    if len(tokens) >= 2:
        tokens = [w for w in s.split() for w in re.split(r"[_\-]+", w) if w]
        clean = sum(len(w) for w in tokens if _clean_token(w)) / sum(map(len, tokens))
        r *= min(1., clean / .7)
    # a reversed text holds reversed function words (e.g. "eht" or "dna") rather than function words, while a text
    #  without any of them (e.g. a short one) is not penalised
    words = re.findall(r"[^\W\d_]+", t)
    sw, rsw = sum(w in STOPWORDS for w in words), sum(w[::-1] in STOPWORDS for w in words)
    if rsw > sw:
        r *= .6 + .4 * sw / rsw
    return r

