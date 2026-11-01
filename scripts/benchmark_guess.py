#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Benchmark of the guess feature.

This encodes lorem ipsum sentences with random chains of codecs (seeded, hence reproducible) and measures:
- guess: how many chains are recovered (the original text is among the results), and how long it takes
- rank:  where the right codec comes in the ranking of a single encoding (mean reciprocal rank, top-1 and top-5 rates)

Each guess runs in a child process, so that a case exceeding the time limit (or running out of memory) is killed and
 counted as a timeout instead of stalling the benchmark.

Usage: python scripts/benchmark_guess.py [-n 30] [-s 42] [-t 60] [--stop text] [--max-nodes N] [--timeout S] ...
"""
import argparse
import multiprocessing as mp
import random
import time
from collections import defaultdict
from statistics import mean

import codext


LOREM = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
         "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
         "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
         "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
         "culpa qui officia deserunt mollit anim id est laborum.").split()


def plaintext(rnd):
    """ Pick a lorem ipsum text of 4 to 24 words, starting at a random word. """
    n = rnd.randint(4, 24)
    i = rnd.randint(0, len(LOREM) - n)
    return " ".join(LOREM[i:i+n])


def encodings_by_codec():
    """ Group the encodings that guess may try (those of the 'guess' lists) and that round-trip by codec name. """
    names, r = set(), defaultdict(list)
    for e in codext.list_encodings():
        try:
            names.update(codext.lookup(e, False).parameters.get('guess') or [])
        except Exception:
            continue
    for e in sorted(names):
        try:
            if codext.decode(codext.encode(LOREM_CHECK, e), e) == LOREM_CHECK:
                r[codext.lookup(e, False).parameters['name']].append(e)
        except Exception:
            continue
    return r


LOREM_CHECK = " ".join(LOREM[:9])


def make_cases(n, seed, max_chain, pool):
    """ Build n cases (text, chain, encoded) with chains of 1 to max_chain codecs, each one round-tripping. """
    rnd, codecs_, cases = random.Random(seed), sorted(pool), []
    while len(cases) < n:
        txt, chain = plaintext(rnd), []
        for _ in range(rnd.randint(1, max_chain)):
            chain.append(rnd.choice(pool[rnd.choice(codecs_)]))
        try:
            enc = txt
            for e in chain:
                enc = codext.encode(enc, e)
            dec = enc
            for e in reversed(chain):
                dec = codext.decode(dec, e)
        except Exception:
            continue
        if dec == txt and enc != txt:
            cases.append((txt, chain, enc))
    return cases


def _guess(queue, enc, kwargs):
    stop = kwargs.pop('stop')
    queue.put(list(codext.guess(enc, getattr(codext.stopfunc, stop), **kwargs).values()))


def run_guess(cases, limit, kwargs, verbose=False):
    ctx = mp.get_context("fork")
    found, timeouts, times = 0, 0, []
    for i, (txt, chain, enc) in enumerate(cases, 1):
        q = ctx.Queue()
        p = ctx.Process(target=_guess, args=(q, enc, dict(kwargs)))
        t0 = time.perf_counter()
        p.start()
        try:
            res = q.get(timeout=limit)
            status = "found" if any(codext.__common__.ensure_str(r) == txt for r in res) else "missed"
        except Exception:
            res, status = [], "timeout"
        p.join(1)
        if p.is_alive():
            p.kill()
            p.join()
        dt = time.perf_counter() - t0
        times.append(dt)
        found += status == "found"
        timeouts += status == "timeout"
        if verbose:
            print(f"[{i:>3}] {status:<7} {dt:6.2f}s  {' > '.join(chain)}")
    return found, timeouts, times


def run_rank(cases):
    """ Rank single encodings ; a codec is right when its name matches (variants of a codec can be equivalent). """
    rr, top1, top5 = [], 0, 0
    for txt, chain, enc in cases:
        name = codext.lookup(chain[0], False).parameters['name']
        names = []
        for _, e in codext.rank(enc):
            n = codext.lookup(e, False).parameters['name']
            if n not in names:
                names.append(n)
        pos = names.index(name) + 1 if name in names else None
        rr.append(1 / pos if pos else 0.)
        top1 += pos == 1
        top5 += pos is not None and pos <= 5
    return mean(rr), top1, top5


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("-n", "--cases", type=int, default=30, help="number of guess cases")
    p.add_argument("-r", "--rank-cases", type=int, default=200, help="number of rank cases (single encodings)")
    p.add_argument("-s", "--seed", type=int, default=42)
    p.add_argument("-c", "--max-chain", type=int, default=3, help="maximum length of a chain of codecs")
    p.add_argument("-t", "--time-limit", type=float, default=60., help="time limit per guess case (kill)")
    p.add_argument("-d", "--max-depth", type=int, default=3, help="max_depth passed to guess")
    p.add_argument("--stop", default="text", help="name of the stop function (from codext.stopfunc)")
    p.add_argument("--no-guess", action="store_true", help="skip the guess benchmark")
    p.add_argument("--no-rank", action="store_true", help="skip the rank benchmark")
    p.add_argument("-v", "--verbose", action="store_true", help="show the outcome of each guess case")
    # search budgets of guess (only passed when set, so that the script also runs against older versions)
    p.add_argument("--timeout", type=float, help="timeout passed to guess")
    p.add_argument("--max-nodes", type=int, help="max_nodes passed to guess")
    p.add_argument("--beam", type=int, help="beam passed to guess")
    a = p.parse_args()
    pool = encodings_by_codec()
    print(f"Pool: {len(pool)} codecs, {sum(map(len, pool.values()))} encodings")
    if not a.no_rank:
        cases = make_cases(a.rank_cases, a.seed, 1, pool)
        t0 = time.perf_counter()
        mrr, top1, top5 = run_rank(cases)
        print(f"rank : MRR={mrr:.3f}  top-1={top1}/{len(cases)}  top-5={top5}/{len(cases)}  "
              f"({time.perf_counter() - t0:.1f}s)")
    if not a.no_guess:
        kw = {'stop': a.stop, 'max_depth': a.max_depth}
        for k in ["timeout", "max_nodes", "beam"]:
            if getattr(a, k) is not None:
                kw[k] = getattr(a, k)
        cases = make_cases(a.cases, a.seed, a.max_chain, pool)
        found, timeouts, times = run_guess(cases, a.time_limit, kw, a.verbose)
        print(f"guess: found={found}/{len(cases)}  timeouts={timeouts}  total={sum(times):.1f}s  "
              f"mean={mean(times):.2f}s  max={max(times):.2f}s")


if __name__ == "__main__":
    main()
