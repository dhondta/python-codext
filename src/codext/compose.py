# -*- coding: UTF-8 -*-
"""Compose feature - build a strong chain of codecs from the answers to a few assessment questions.

The answers (what is encoded, which characters the output may hold, how much larger it may be, how many layers, whether
 it shall look like text and an optional secret key) define the constraints of the chain. It is then built layer by
 layer: at each layer, codecs are tried in a random order on a few samples, keeping those that round-trip exactly on
 all of them and meet the constraints, and the candidate that ``rank`` (the scoring engine behind ``guess``) ranks the
 lowest on its own output is selected, a candidate it does not surface at all ("blind", e.g. a keyed cipher with the
 user's key) being the best. The resulting chain is finally rated with ``strength``.

As for ``strength``, this rates the resistance to codext's own guessing heuristic and to casual recognition - not
 cryptographic strength. The chain is drawn at random (unless a seed is given), so that it cannot be predicted from the
 answers. It depends on ``guess`` and ``strength``, one-directional.
"""
import random
from string import ascii_letters, digits
from time import perf_counter

from .__common__ import *
from .__common__ import list_categories
from .guess import rank, stopfunc
from .strength import strength
from .utils import PRINTABLES


__all__ = ["compose"]

# the assessment questions: name, question, choices (value: description ; None for a free answer) and default value
QUESTIONS = [
    {'name': "input", 'question': "What will be encoded?", 'default': "text",
     'choices': {'text': "text (letters, digits and punctuation)", 'binary': "any data (bytes)"}},
    {'name': "alphabet", 'question': "Which characters may the encoded output contain?", 'default': "printable",
     'choices': {'any': "any byte", 'printable': "printable characters only", 'alphanumeric': "letters and digits only",
                 'letters': "letters only"}},
    {'name': "expansion", 'question': "How much larger than the input may the output be?", 'default': "5",
     'choices': {'2': "up to 2 times", '5': "up to 5 times", '20': "up to 20 times", 'any': "no limit"}},
    {'name': "layers", 'question': "How many layers (more layers resist better but take longer to compose)?",
     'default': "3", 'choices': {'2': "2 layers", '3': "3 layers", '4': "4 layers", '5': "5 layers"}},
    {'name': "disguise", 'question': "Should the output look like text rather than encoded data?", 'default': "no",
     'choices': {'no': "no", 'yes': "yes (printable, with a low entropy)"}},
    {'name': "key", 'question': "Secret key for a keyed layer, needed to decode (letters only, at least 4 ; empty for "
     "none)?", 'default': "", 'choices': None},
]
ALPHABETS = {'any': None, 'printable': PRINTABLES, 'alphanumeric': frozenset(ascii_letters + digits),
             'letters': frozenset(ascii_letters)}
# expansion kept for the last layer when the output alphabet is restricted (the least expanding codecs whose output
#  meets it: base62 or base58 for alphanumeric characters, base26 for letters)
RESERVE = {'any': 1., 'printable': 1., 'alphanumeric': 1.4, 'letters': 1.7}
# ciphers accepting the user's key as their parameter (e.g. "vigenere-mykey") whatever the input
KEYED = ["autoclave", "beaufort", "columnar", "porta", "vernam", "vigenere"]
# categories whose codecs are lossy (hence not reversible)
LOSSY = ["checksum", "hashing"]
# samples per type of input, all the chosen encodings having to round-trip on each of them ; the first one, which the
#  ranking, the expansion and the strength are measured on, is long enough to be representative of a message, as the
#  guesser misses some codecs on short inputs (e.g. uu, whose header and trailer then dominate the expansion factor)
SAMPLES = {
    'text':   ["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et "
               "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
               "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum "
               "dolore.",
               "The quick brown fox jumps over the lazy dog.", "Attack at dawn: 42 units, ref. #7-B (urgent)!"],
    'binary': [random.Random(0).randbytes(320), bytes(range(256))],
}
SLOW = .2  # maximum duration of an encoding of a sample (in seconds), slower codecs being discarded


def _answers(answers):
    """ Validate the answers, setting the default value of each question not answered. """
    answers, r = dict(answers or {}), {}
    for q in QUESTIONS:
        a = str(answers.pop(q['name'], q['default'])).strip()
        if q['choices'] is not None and a not in q['choices']:
            raise ValueError(f"bad answer for '{q['name']}': {a} (choices: {', '.join(q['choices'])})")
        r[q['name']] = a
    if answers:
        raise ValueError(f"unknown question(s): {', '.join(answers)}")
    if r['key'] and (not r['key'].isalpha() or not r['key'].isascii() or len(r['key']) < 4):
        raise ValueError("the key shall be made of at least 4 letters")
    return r


def _pool(include, exclude):
    """ Get the category and the encodings that may be used in the chain, per codec name ; a codec is represented by
         the encodings it is guessed with, or by its own name if it opts out of guessing (e.g. "cp500"). Also get the
         set of the encodings the guesser tries (any other one is never surfaced). """
    # a name that is a category selects the category only (e.g. "base", also the name of the generic base codec)
    cats = set(list_categories())
    (inc_c, inc_n), (exc_c, exc_n) = [({x for x in l if x in cats}, {x for x in l if x not in cats})
                                      for l in ([x] if isinstance(x, str) else x or [] for x in (include, exclude))]
    pool, guessable = {}, set()
    for name in list_encodings():
        try:
            p = lookup(name, False).parameters
        except LookupError:  # pragma: no cover
            continue
        cat, codec = p.get('category'), p.get('name', name)
        encs = p.get('guess') or [name]
        guessable.update(p.get('guess') or [])
        if cat in LOSSY or cat in exc_c or codec in exc_n:
            continue
        if inc_c or inc_n:
            if cat not in inc_c and codec not in inc_n:
                # possibly selected by encoding names, then only these encodings are used
                encs = [e for e in encs if e in inc_n]
        encs = [e for e in encs if e not in exc_n]
        if encs:
            pool[codec] = (cat, encs)
    return pool, guessable


def _try(encoding, texts, history, budget, samples, last, alphabet, disguise):
    """ Encode each text, checking that the encoding round-trips, is not an identity, is fast enough and meets the
         constraints ; return the outputs, or None if the encoding is not suitable. """
    outs = []
    for i, (text, h, s) in enumerate(zip(texts, history, samples)):
        try:
            t0 = perf_counter()
            out = encode(text, encoding)
            if perf_counter() - t0 > SLOW or b(decode(out, encoding)) != b(text) or b(out) in h:
                return
        except Exception:
            return
        # the expansion is measured on the first sample (a short one would be dominated by a constant overhead)
        if i == 0 and budget is not None and len(b(out)) > budget * len(b(s)):
            return
        if last:
            o = ensure_str(out)
            if alphabet is not None and not alphabet.issuperset(o) or disguise and not stopfunc.text(o):
                return
        outs.append(out)
    return outs


def _rank_of(encoding, out):
    """ 1-based rank of the encoding when ranking its output, None if not surfaced (blind). """
    try:
        return next((i + 1 for i, (_, e) in enumerate(rank(out)) if e == encoding), None)
    except Exception:  # pragma: no cover
        return None


def _select(rnd, found, guessable):
    """ Select the candidate that the guesser ranks the lowest on its own output, one that it does not surface at all
         (blind) being the best: one that it never tries (e.g. "cp500") is blind without ranking (which is costly),
         otherwise the ranking stops at the first blind one. """
    blind = [f for f in found if f[2] not in guessable]
    if blind:
        return rnd.choice(blind)
    best, selected = 0, []
    for f in rnd.sample(found, len(found)):
        if (r := _rank_of(f[2], f[3][0])) is None:
            return f
        if r > best:
            best, selected = r, [f]
        elif r == best:
            selected.append(f)
    return rnd.choice(selected)


def _compose(rnd, a, pool, guessable, samples, candidates):
    """ Build a chain layer by layer ; return it, or None if the constraints could not be met. """
    n, budget = int(a['layers']), None if a['expansion'] == "any" else float(a['expansion'])
    alphabet, disguise = ALPHABETS[a['alphabet']], a['disguise'] == "yes"
    keyed = {c: ("cipher", [f"{c}-{a['key']}"]) for c in KEYED} if a['key'] else {}
    key_at = rnd.randrange(n) if keyed else n
    chain, used, cats, texts, history = [], set(), set(), list(samples), [{b(s)} for s in samples]
    # intermediate layers keep part of the expansion for the last one when the alphabet is restricted
    bgt = None if budget is None else budget / RESERVE[a['alphabet']]
    for i in range(n):
        last, found = i == n - 1, []
        # the keyed layer is placed at a random position, or at the first next one where a keyed cipher suits ; the
        #  layers are preferably of distinct categories (e.g. not two substitutions of bytes, that compose into one)
        groups = ([(keyed, False)] if i >= key_at else []) + [(pool, True), (pool, False)]
        for group, distinct in groups:
            for codec in rnd.sample(sorted(group), len(group)):
                cat, encs = group[codec]
                if codec in used or distinct and cat in cats:
                    continue
                e = rnd.choice(encs)
                outs = _try(e, texts, history, budget if last else bgt, samples, last, alphabet, disguise)
                if outs is not None:
                    found.append((codec, cat, e, outs))
                    if len(found) >= candidates:
                        break
            if found:
                break
        if not found:
            return
        if group is keyed:
            key_at = n  # the keyed layer is placed (the guesser misses the key, hence no ranking is needed)
            codec, cat, e, outs = rnd.choice(found)
        else:
            codec, cat, e, outs = _select(rnd, found, guessable)
        chain.append(e)
        used.add(codec)
        cats.add(cat)
        texts = outs
        for h, o in zip(history, outs):
            h.add(b(o))
    if key_at < n:
        return
    return chain


def compose(answers=None, sample=None, include=None, exclude=None, seed=None, candidates=8, tries=3):
    """ Compose a strong chain of codecs from the answers to the assessment questions (see ``compose.questions``).

    :param answers:    dictionary of answers by question name (input, alphabet, expansion, layers, disguise, key) ;
                        the default value of each question not answered is used
    :param sample:     sample input the chain must work with, in addition to the default samples ; when given, the
                        ranking, the expansion and the strength are measured on it (it should then be representative
                        of the inputs, as the guesser misses some codecs on short ones)
    :param include:    categories/codecs/encodings that may be used in the chain (default: all but the lossy ones)
    :param exclude:    categories/codecs/encodings that may not be used in the chain
    :param seed:       seed for drawing the chain (default: random, so that the chain cannot be predicted) ; a same
                        seed gives a same chain for a same set of available codecs
    :param candidates: number of suitable codecs compared at each layer (more is stronger but slower)
    :param tries:      number of attempts to build a chain meeting the constraints
    :return:           a dict with the chain, the answers, the expansion of the output and the strength rating
    """
    a = _answers(answers)
    if candidates < 1 or tries < 1:
        raise ValueError("'candidates' and 'tries' shall be positive integers")
    samples = ([sample] if sample else []) + SAMPLES[a['input']]
    # the text samples are also given as bytes (e.g. as read from a file or from stdin), as some codecs only encode
    #  str (e.g. utf-16) and others only bytes
    samples += [b(s) for s in samples if isinstance(s, str)]
    (pool, guessable), rnd = _pool(include, exclude), random.Random(seed)
    for _ in range(tries):
        chain = _compose(rnd, a, pool, guessable, samples, candidates)
        if chain:
            break
    else:
        raise ValueError("no chain of codecs meets these constraints ; relax the alphabet, the expansion or the "
                         "disguise, or allow more codecs")
    r = strength(chain, sample=samples[0])
    out = samples[0]
    for e in chain:
        out = encode(out, e)
    notes = r['notes'][:]
    if a['key']:
        notes.append("the chain holds the secret key ('%s') ; keep it secret" % next(e for e in chain
                                                                                     if e.endswith("-" + a['key'])))
    return {'chain': chain, 'answers': a, 'score': r['score'], 'grade': r['grade'], 'strength': r, 'notes': notes,
            'expansion': round(len(b(out)) / len(b(samples[0])), 2)}
compose.questions = QUESTIONS


def report(r):
    """ Human-readable report of a composed chain of codecs (as returned by ``compose``). """
    s = r['strength']
    lines = ["chain: %s" % " · ".join(r['chain']),
             "strength: %d/100  (%s)" % (r['score'], r['grade']),
             "  layer ranks : %s" % s['correct_ranks'],
             "  blind layers: %d / %d" % (s['blind_layers'], s['length']),
             "  expansion   : x%s" % r['expansion'],
             "  disguised   : %s" % s['disguised']]
    lines += ["  note        : %s" % n for n in r['notes']]
    lines += ["encode with: codext encode %s" % " ".join(r['chain']),
              "decode with: codext decode %s" % " ".join(r['chain'][::-1])]
    return "\n".join(lines)


codecs.compose = compose
codecs.compose_report = report
