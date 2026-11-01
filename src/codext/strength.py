# -*- coding: UTF-8 -*-
"""Strength feature - evaluate how hard a chain of codecs is to reverse.

This rates a chain of encodings by how well it resists codext's own guessing heuristic (the canonical adversary) and
 casual recognition - not cryptographic strength. It encodes a sample through the chain, then walks the true decoding
 path and, at each layer, uses ``rank`` (the very scoring engine behind ``guess``) to measure how high the correct
 codec is ranked: a layer ranked first is an obvious give-away, a deeply-ranked or non-surfaced ("blind") layer is one
 the guesser cannot greedily follow. It also checks whether the output still looks like text (a disguise that may evade
 notice) and whether the chain is reversible at all (a lossy step such as a hash cannot be recovered).

The per-layer ranking is used on purpose instead of the full recursive ``guess``: the latter is combinatorially
 explosive on some chains, while the ranker applies the same heuristic deterministically and in bounded time.

It returns a score from 0 (trivially reversible) to 100 (resists the guesser), a letter grade, the breakdown and
 human-readable notes pointing at the weakest layer. It depends on ``guess`` and the registry, one-directional.
"""
from .__common__ import *
from .guess import rank, stopfunc


__all__ = ["strength"]

# samples tried in order until one encodes cleanly through the chain (kept diverse: letters, digits, punctuation)
_SAMPLES = ["The quick brown fox jumps over the lazy dog.", "Attack at dawn, 42 times!", "0123456789", "test"]
_GRADES = [(85, "A"), (70, "B"), (55, "C"), (40, "D"), (20, "E"), (0, "F")]
_RANK_CAP = 6  # a correct codec ranked at or below this is considered effectively hidden from a greedy guesser


def _correct_ranks(names, ct, include, exclude):
    """ Walk the true decoding path ; for each layer, the 1-based rank of the correct codec (None if not surfaced). """
    ranks, cur = [], ct
    for name in reversed(names):
        try:
            ranked = rank(cur, limit=-1, include=include, exclude=exclude)
        except Exception:  # pragma: no cover
            ranked = []
        ranks.append(next((i + 1 for i, item in enumerate(ranked) if item[1] == name), None))
        try:
            cur = decode(cur, name)
        except Exception:  # pragma: no cover
            break
    ranks.reverse()  # report in chain order (innermost first)
    return ranks


def _encode_chain(names, sample):
    out = sample
    for name in names:
        out = encode(out, name)
    return out


def _grade(score):
    return next(g for threshold, g in _GRADES if score >= threshold)


def _normalize(chain):
    """ Turn a macro name, a single name or a list into a validated list of codec names. """
    if isinstance(chain, str):
        try:
            chain = [c.parameters['name'] for c in CodecMacro(chain).codecs]  # a macro name expands to its codecs
        except LookupError:
            chain = [chain]
    names = []
    for c in chain:
        names.append(c.parameters['name'] if hasattr(c, "parameters") else c)
        lookup(names[-1])  # raises LookupError on an unknown codec
    if not names:
        raise ValueError("'strength' needs at least one codec")
    return names


def _pick_sample(names, sample):
    for s in ([sample] if sample is not None else _SAMPLES):
        try:
            _encode_chain(names, s)
            return s
        except Exception:
            continue
    raise ValueError("'strength' could not encode any sample through the chain ; provide a compatible sample")


def _reversible(names, sample, ct):
    try:
        out = ct
        for name in reversed(names):
            out = decode(out, name)
        return b(out) == b(sample)
    except Exception:
        return False


def _notes(names, ranks, disguised):
    notes = []
    surfaced = [(r, i) for i, r in enumerate(ranks) if r is not None]
    if surfaced and all(r == 1 for r, _ in surfaced) and len(surfaced) == len(ranks):
        notes.append("every layer is ranked first by the guesser: trivially peelable")
    elif surfaced:
        r, i = min(surfaced)
        if r == 1:
            notes.append("weakest layer: '%s' (step %d) is ranked first by the guesser - an obvious give-away"
                         % (names[i], i + 1))
    blind = [names[i] for i, r in enumerate(ranks) if r is None]
    if blind:
        notes.append("layers the guesser cannot follow: %s" % ", ".join(blind))
    if disguised:
        notes.append("the output still looks like text, which may evade casual notice")
    return notes


def report(chain, **kwargs):
    """ Human-readable strength report for a chain of codecs. """
    r = strength(chain, **kwargs)
    lines = ["chain: %s" % " · ".join(r['chain']),
             "strength: %d/100  (%s)" % (r['score'], r['grade']),
             "  reversible  : %s" % r['reversible'],
             "  layer ranks : %s" % r['correct_ranks'],
             "  blind layers: %d / %d" % (r['blind_layers'], r['length']),
             "  disguised   : %s" % r['disguised']]
    lines += ["  note        : %s" % n for n in r['notes']]
    return "\n".join(lines)


def strength(chain, sample=None, stop_func=stopfunc.default, include=None, exclude=None):
    """ Evaluate the strength of a chain of codecs.

    :param chain:     a macro name, a codec name or a list of codec names (applied in order)
    :param sample:    sample input to encode through the chain (a compatible default is chosen if None)
    :param stop_func: function telling whether the output "looks like" a plaintext (default: looks like a text)
    :param include:   categories/codecs/encodings the guessing adversary may use (default: all)
    :param exclude:   categories/codecs/encodings the guessing adversary may not use
    :return:          a dict with the score, grade, breakdown and notes
    """
    names = _normalize(chain)
    sample = _pick_sample(names, sample)
    ct = _encode_chain(names, sample)
    reversible = _reversible(names, sample, ct)
    result = {'chain': names, 'reversible': reversible, 'length': len(names)}
    if not reversible:
        result.update(score=100, grade="A", blind_layers=len(names), worst_rank=None, disguised=False,
                      correct_ranks=[None] * len(names),
                      notes=["lossy chain (e.g. a hash): the plaintext cannot be recovered"])
        return result
    ranks = _correct_ranks(names, ct, include, exclude)
    surfaced = [r for r in ranks if r is not None]
    blind = len(ranks) - len(surfaced)
    worst = max(surfaced) if surfaced else None
    try:
        disguised = bool(stop_func(ensure_str(ct)))
    except Exception:  # pragma: no cover
        disguised = False
    # scoring: trivially peelable chains (every layer ranked first) are weak ; deeply-ranked, blind or longer chains,
    #  and outputs that still look like text, resist the guesser more
    score = 12 + 4 * (len(names) - 1) + 24 * min(blind, 3) + (8 if disguised else 0)
    if worst is not None:
        score += 9 * (min(worst, _RANK_CAP) - 1)
    score = min(100, round(score))
    result.update(score=score, grade=_grade(score), blind_layers=blind, worst_rank=worst, disguised=disguised,
                  correct_ranks=ranks, notes=_notes(names, ranks, disguised))
    return result


codecs.strength = strength
codecs.strength_report = report
