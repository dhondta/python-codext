# -*- coding: UTF-8 -*-
"""Keyed squares, shared by the ciphers of the Playfair family (Playfair, Two-square, Four-square) and Bazeries.

A square holds a 5x5 alphabet (a letter being replaced by another one, I and J sharing a cell by default) or a 6x6
 alphabet (letters and digits). It is filled row by row with the distinct letters of a keyword, then with the remaining
 ones of the alphabet.
"""
from string import ascii_uppercase as UC, digits as DG

from ..__common__ import ensure_str, handle_error


def keyed_square(key, alphabet, replace=None):
    """ Fill a square, row by row, with the distinct characters of the key that belong to the alphabet (after replacing
         the given (letter, substitute) pair), then with the remaining ones of the alphabet. """
    seen, grid = set(), []
    for c in key.upper() + alphabet:
        if replace and c == replace[0]:
            c = replace[1]
        if c in alphabet and c not in seen:
            seen.add(c)
            grid.append(c)
    return grid


def square_params(name, grid_size=None, replace_char=None):
    """ Check the grid size and the replaced pair of letters (only for a 5x5 grid, None otherwise), then get the
         alphabet. """
    gs = int(grid_size or 5)
    if gs == 6 and replace_char:
        raise LookupError(f"Bad parameter for encoding '{name}': replaced char only applies to a 5x5 grid")
    if len(rc := str(replace_char or "JI").upper()) != 2 or rc[0] == rc[1]:
        raise LookupError(f"Bad parameter for encoding '{name}': replaced char must be a pair of distinct letters")
    return (gs, tuple(rc), UC.replace(rc[0], "")) if gs == 5 else (gs, None, UC + DG)


def digraph_codec(name, pair, alphabet, replace, decode=False):
    """ Make a codec function substituting the digraphs of the letters of the text with the given pair function.

    The text is uppercased and its whitespace removed ; characters that are not in the alphabet are handled as errors
     and do not take part in the digraphs. When encoding, a text with an odd number of letters is padded with an
     "X". """
    def _code(text, errors="strict"):
        _h = handle_error(name, errors, decode=decode)
        out, slots, letters, where = [], [], [], []
        for i, c in enumerate("".join(ensure_str(text).upper().split())):
            if replace and c == replace[0]:
                c = replace[1]
            if c in alphabet:
                slots.append(len(out))
                letters.append(c)
                where.append(i)
                out.append(c)
            else:
                out.append(_h(c, i))
        if len(letters) % 2:
            if decode:
                # a ciphertext always holds an even number of letters ; the last one is then handled as an error
                out[slots.pop()] = _h(letters.pop(), where[-1])
            else:
                slots.append(len(out))
                letters.append(replace[1] if replace and replace[0] == "X" else "X")
                out.append(None)
        for k in range(0, len(letters), 2):
            out[slots[k]], out[slots[k+1]] = pair(letters[k], letters[k+1])
        return (r := "".join(out)), len(r)
    return _code
