# -*- coding: UTF-8 -*-
"""Route Cipher Codec - route transposition content encoding.

The route cipher is a transposition cipher: the text is written in a grid of N columns (by rows, or down the columns
 with "-down"), then read along a route starting from a corner (top-left by default, or "-tr", "-bl", "-br"):
- "spiral" (default) and "spiral-ccw": inwards, clockwise or counter-clockwise ;
- "rows" and "columns": row by row or column by column, in the same direction (the "lines" of dCode) ;
- "snake-rows" and "snake-columns": row by row or column by column, alternating directions (the "routes" of dCode).
The grid has as many rows as needed ; when the text does not fill it, its last cells remain empty and are skipped by the
 route (a full grid is obtained by padding the text beforehand, e.g. with "." as dCode or "X"). Every character is
 transposed, including whitespaces and punctuation.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Transposition_cipher#Route_cipher
           https://www.dcode.fr/route-cipher
"""
from math import ceil

from ..__common__ import *


__examples__ = {
    'enc(route-0|route-3-diagonal|route-3-spiral-xx|route)': None,
    # Wikipedia's example: 3 rows of 9 columns written downwards, read in a clockwise spiral from the top-right corner
    'enc(route-9-down-spiral-tr|route_cipher_9_down_spiral_tr)': {
        'WEAREDISCOVEREDFLEEATONCEJX': "EJXCTEDECDAEWRIORFEONALEVSE"},
    # dCode's example: 4 columns, padded with ".", read along the vertical route from the top-left corner
    'enc(route-4-snake-columns|route4_snake_columns-tl)': {'DCODEROUTE..': "DETERCOO..UD", 'DCODEROUTE': "DETERCOOUD"},
    'enc(route-3|route-3-spiral|route-3-spiral-tl)': {'ABCDEFGHI': "ABCFIHGDE", 'ABCDEFGH': "ABCFHGDE"},
    'enc(route-3-spiral-ccw)': {'ABCDEFGHI': "ADGHIFCBE"},
    'enc(route-3-spiral-br)': {'ABCDEFGHI': "IHGDABCFE"},
    'enc(route-3-rows-br)': {'ABCDEFGHI': "IHGFEDCBA"},
    'enc(route-3-columns)': {'ABCDEFGHI': "ADGBEHCFI"},
    'enc(route-3-snake-rows-tr)': {'ABCDEFGHI': "CBADEFIHG"},
    'enc(route-3-down-rows)': {'ABCDEFGHI': "ADGBEHCFI"},
    'enc-dec(route-2|route-5-down|route-4-snake-rows-bl|route-7-spiral-ccw-br|route-3-down-snake-columns-tr)': [
        "", "a", "Hello, World!", "We are discovered, flee at once!", "@random{512,1024,2048}"],
}
__guess__ = ["route-%d" % n for n in range(2, 9)] + ["route-%d-spiral-ccw" % n for n in range(2, 9)]


# directions (row, column) in clockwise order, and the first direction of a clockwise spiral by starting corner
CW, FIRST = [(0, 1), (1, 0), (0, -1), (-1, 0)], {'tl': 0, 'tr': 1, 'br': 2, 'bl': 3}


def _route(rows, cols, path, corner):
    """ Get the positions (row, column) of a grid in the order of the given route from the given corner. """
    bottom, right = corner[0] == "b", corner[1] == "r"
    rs, cs = range(rows)[::-1 if bottom else 1], range(cols)[::-1 if right else 1]
    if path.startswith("spiral"):
        ccw = path.endswith("ccw")
        # a counter-clockwise spiral goes along the other side of its corner first, turning the other way
        d, step = (FIRST[corner] + ccw) % 4, -1 if ccw else 1
        r, c, seen, route = rs[0], cs[0], set(), []
        for _ in range(rows * cols):
            route.append((r, c))
            seen.add((r, c))
            for _ in range(4):
                nr, nc = r + CW[d][0], c + CW[d][1]
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                    break
                d = (d + step) % 4
            r, c = nr, nc
        return route
    snake, by_rows = path.startswith("snake"), path.endswith("rows")
    outer, inner = (rs, cs) if by_rows else (cs, rs)
    route = []
    for i, x in enumerate(outer):
        for y in (inner[::-1] if snake and i % 2 else inner):
            route.append((x, y) if by_rows else (y, x))
    return route


def _order(n, length, down, path, corner):
    """ Get the indices of the characters of the text in the order of the route. """
    if n <= 0:
        raise LookupError("Bad parameter for encoding 'route': the number of columns must be a positive integer")
    if length == 0:
        return []
    rows = ceil(length / n)
    # positions of the characters in the grid, written by rows or down the columns
    fill = [(i % rows, i // rows) if down else (i // n, i % n) for i in range(length)]
    index = {p: i for i, p in enumerate(fill)}
    return [index[p] for p in _route(rows, n, path, corner) if p in index]


def _params(n, down, path, corner):
    return int(n or 0), down == "down", (path or "spiral").replace("_", "-"), corner or "tl"


def route_encode(n, down="", path="", corner=""):
    n, down, path, corner = _params(n, down, path, corner)
    def encode(text, errors="strict"):
        return "".join(text[i] for i in _order(n, len(text), down, path, corner)), len(text)
    return encode


def route_decode(n, down="", path="", corner=""):
    n, down, path, corner = _params(n, down, path, corner)
    def decode(text, errors="strict"):
        r = [""] * len(text)
        for c, i in zip(text, _order(n, len(text), down, path, corner)):
            r[i] = c
        return "".join(r), len(text)
    return decode


add("route", route_encode, route_decode, r"^route(?:[-_]cipher)?[-_]?(\d+)(?:[-_](down))?"
    r"(?:[-_](spiral[-_]ccw|spiral|snake[-_]rows|snake[-_]columns|rows|columns))?(?:[-_](tl|tr|bl|br))?$")
