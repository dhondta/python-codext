# -*- coding: UTF-8 -*-
"""Generation of strings matching a regular expression.

This module generates strings from a regex pattern, e.g. for providing examples of valid encoding names given the
 pattern of a codec (see ``examples`` and ``search`` in ``__common__``). It only depends on ``utils``.
"""
import random
import re
from functools import reduce
from itertools import product
from string import ascii_letters, digits, printable, whitespace
try:
    import re._parser as sre_parse
except ImportError:
    import sre_parse

from .utils import b

# from Python 3.11, 'sre_parse' is bound as '_parser' ; monkey-patch it for backward-compatibility
re.sre_parse = sre_parse


__all__ = ["generate_string_from_regex", "generate_strings_from_regex"]


# characters matched by the categories of a regex (e.g. "\d" or "\S"), restricted to printables
RE_CATEGORIES = {
    'digit':     digits,
    'not_digit': reduce(lambda x, c: x.replace(c, ""), digits, printable),
    'space':     whitespace,
    'not_space': reduce(lambda x, c: x.replace(c, ""), whitespace, printable),
    'word':      ascii_letters + digits + '_',
    'not_word':  reduce(lambda x, c: x.replace(c, ""), ascii_letters + digits + '_', printable),
}
REPEAT_MAX    = 10
STAR_PLUS_MAX = 10
YIELD_MAX     = 100


def __gen_str_from_re(regex, star_plus_max, repeat_max, yield_max, parsed=False):
    """ Recursive function to generate strings from a regex pattern. """
    if regex is None:
        return
    __groups = {}
    tokens = []
    negate, last_rand = False, None
    for state in (regex if parsed else re.sre_parse.parse(b(getattr(regex, "pattern", regex)))):
        code = getattr(state[0], "name", state[0]).lower()
        value = getattr(state[1], "name", state[1])
        value = value.lower() if isinstance(value, str) else value
        if code in ["assert_not", "at"]:
            continue
        elif code == "any":
            charset = list(printable.replace("\n", ""))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)  # should be ord(x) with x belongs to [0, 256[
        elif code == "assert":
            tokens.append(list(__gen_str_from_re(value[1], star_plus_max, repeat_max, yield_max, True)))
        elif code == "branch":
            result = []
            for r in value[1]:
                result += list(__gen_str_from_re(r, star_plus_max, repeat_max, yield_max, True)) or [""]
            tokens.append(result)
        elif code == "category":
            charset = list(RE_CATEGORIES[value[9:]])
            if negate:
                negate = False
                charset = list(set(printable).difference(charset))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)
        elif code == "groupref":
            tokens.extend(__groups[value])
        elif code == "in":
            subtokens = list(__gen_str_from_re(value, star_plus_max, repeat_max, yield_max, True))
            subtokens = [x for l in subtokens for x in l]
            tokens.append(subtokens)
        elif code == "literal":
            tokens.append(chr(value))
        elif code in ["max_repeat", "min_repeat"]:
            start, end = value[:2]
            end = min(end, star_plus_max)
            start = min(start, end)
            charset = list(__gen_str_from_re(value[-1], star_plus_max, repeat_max, yield_max, True))
            subtokens = []
            if start == 0 and end == 1:
                subtokens.append("")
                subtokens.extend(charset)
            elif len(charset) ** end > repeat_max:
                for i in range(min(repeat_max, 10 * len(charset))):
                    n = random.randint(start, end + 1)
                    token = "" if n == 0 else "".join(random.choice(charset) for i in range(n))
                    if token not in subtokens:
                        subtokens.append(token)
                    else:
                        i -= 1
            else:
                for n in range(start, end + 1):
                    for c in product(charset, repeat=n):
                        subtokens.append("".join(c))
            tokens.append(subtokens)
        elif code == "negate":
            negate = True
        elif code == "not_literal":
            charset = list(printable.replace(chr(value), ""))
            while charset[0] == last_rand and len(charset) > 1:
                random.shuffle(charset)
            last_rand = charset[0]
            tokens.append(charset)
        elif code == "range":
            tokens.append("".join(chr(i) for i in range(value[0], value[1] + 1)))
        elif code == "subpattern":
            result = list(__gen_str_from_re(value[-1], star_plus_max, repeat_max, yield_max, True))
            if value[0]:
                __groups[value[0]] = result
            tokens.append(result)
        else:
            raise NotImplementedError(f"Unhandled code '{code}'")
    if len(tokens) == 0:
        tokens = [""]
    i = 0
    for result in product(*tokens):
        yield "".join(result)
        i += 1
        if i >= yield_max:
            break


def generate_string_from_regex(regex):
    """ Utility function to generate a single string from a regex pattern. """
    if regex:
        return list(generate_strings_from_regex(regex, yield_max=1))[0]


def generate_strings_from_regex(regex, star_plus_max=STAR_PLUS_MAX, repeat_max=REPEAT_MAX, yield_max=YIELD_MAX):
    """ Utility function to generate strings from a regex pattern. """
    for r in __gen_str_from_re(regex, star_plus_max, repeat_max, yield_max):
        yield r

