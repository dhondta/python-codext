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
# a change from a lowercase to an uppercase letter in a word starting with a lowercase letter (e.g. "gsThe")
CASE_CHANGE = re.compile(r"(?<![A-Za-z])[a-z]+[A-Z]")
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
    # a lowercase letter followed by an uppercase one in a word starting with a lowercase letter (e.g. "sT" in "gsThe",
    #  from a rotation of a text, unlike "JavaScript") does not form a bigram of a text, hence it is not counted as a
    #  common bigram, while it still counts as a pair
    changes = [m.end() - 2 for m in CASE_CHANGE.finditer(s)]
    bigrams = sum(map(BIGRAMS.__contains__, pairs)) - sum(t[i:i+2] in BIGRAMS for i in changes)
    bigrams = min(1., bigrams / len(pairs) / .7)
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
    # such a change of case in a word is rare in a text (only in some names, e.g. "iPhone"), while it reveals a
    #  rearrangement of a text that moved its first letter after its last ones (e.g. "gsThe quick ... lazy do")
    if len(changes) > 0:
        r *= max(.5, 1. - .1 * len(changes))
    # a reversed text holds reversed function words (e.g. "eht" or "dna") rather than function words, while a text
    #  without any of them (e.g. a short one) is not penalised
    words = re.findall(r"[^\W\d_]+", t)
    sw, rsw = sum(w in STOPWORDS for w in words), sum(w[::-1] in STOPWORDS for w in words)
    if rsw > sw:
        r *= .6 + .4 * sw / rsw
    return r


# frequencies of the letters "a" to "z" in English texts (in %) ; other Latin-script languages share most of the frequent
#  letters (e.g. lorem ipsum, French, German or Spanish)
LETTER_FREQUENCIES = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2., 6.1, 7., .15, .8, 4., 2.4, 6.7, 7.5, 1.9, .1, 6., 6.3, 9.1, 2.8, 1.,
                      2.4, .15, 2., .07]


def _letter_frequencies(s, normalize=True):
    """ Get the number of Latin letters of the given string and their mean frequencies (in English texts) for its 26
         shifts (the first one being the string itself), or None if it has no Latin letter. The letters with diacritics
         count as their base letters (e.g. "\u00e9" as "e") unless normalize is False. """
    counts, s = [0] * 26, ensure_str(b(s)).lower()
    for c in (unicodedata.normalize("NFKD", s) if normalize else s):
        if "a" <= c <= "z":
            counts[ord(c) - 97] += 1
    if (n := sum(counts)) == 0:
        return
    return n, [sum(c * LETTER_FREQUENCIES[(i + k) % 26] for i, c in enumerate(counts)) / n for k in range(26)]


def _letter_frequency(s, ref=None):
    """ Rate in [0, 1] how much the letters of the given string are distributed as in a text, relatively to the other
         shifts of its letters (as for cracking a Caesar cipher) and to the ones of the reference string if given.
    
    This is the mean frequency (in English texts) of the letters of the string divided by the best one among the 26
     shifts of these letters (and of the letters of the reference string), squared ; a text is rated 1. (or close to
     it), as it is mostly the best-distributed of its shifts, while a shift of a text gets a lower rate. Unlike the
     bigrams of the textness, this distinguishes a text from the other shifts of its letters, even for a short text
     whose letters happen to form common bigrams once shifted ; and, unlike the mean frequency itself, this does not
     penalise a text with uncommon letters (e.g. "The quick brown fox jumps over the lazy dog"). With the input of a
     decoding as the reference, this also lowers the rate of an output that is not a shift of the input and whose
     letters are distributed worse than the best shift of the input (e.g. the output of a wrong substitution when the
     input is a Caesar cipher) ; the reference only counts its ASCII letters and is only considered when it holds at
     least as many letters as the string, as the shifts of a few letters (e.g. of binary data) can get a better mean
     frequency than a text by chance. A string without Latin letters is rated 1. (not distinguished).
    
    The string and the reference can also be given as their letter frequencies (see _letter_frequencies), e.g. for
     computing these of an input only once. """
    f = s if isinstance(s, tuple) or s is None else _letter_frequencies(s)
    if f is None:
        return 1.
    if ref is not None and not isinstance(ref, tuple):
        ref = _letter_frequencies(ref, False)
    (n, f), best = f, max(f[1])
    if ref is not None and ref[0] >= n:
        best = max(best, max(ref[1]))
    return (f[0] / best) ** 2
