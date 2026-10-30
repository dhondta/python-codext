# -*- coding: UTF-8 -*-
"""Piet Codec - Piet content encoding.

Piet is an esoteric programming language created by David Morgan-Mar in 2001, whose programs are images looking like
 abstract paintings. They are made of codels (squares of pixels) of 20 colors: 18 colors of 6 hues (red, yellow, green,
 cyan, blue, magenta) in 3 lightnesses (light, normal, dark), white and black. Connected codels of the same color form
 color blocks, through which the interpreter moves according to a direction pointer (DP) and a codel chooser (CC),
 sliding through white codels and being blocked by black codels and the edges ; it halts when it cannot leave a block.
 Moving from a block to another executes a command on a stack of integers, given by the change of hue and lightness:

                  same lightness   1 step darker      2 steps darker
    same hue      -                push (block size)  pop
    1 step        add              subtract           multiply
    2 steps       divide           mod                not
    3 steps       greater          pointer            switch
    4 steps       duplicate        roll               in(number)
    5 steps       in(char)         out(number)        out(char)

Encoding generates a PNG image of a program that prints the text, pushing each character (its code point) as the size
 of a block (or by multiplications and additions above 256) before printing it with out(char). Decoding reads a PNG,
 GIF or PPM image and runs the program, returning its output.

The codel size is given in the codec name (1 by default for encoding), or guessed when decoding as the greatest common
 divisor of the lengths of the runs of pixels of the same color. Colors other than the 20 colors of Piet are only
 accepted (as white) with a non-strict errors handling. No input is available (in(number) and in(char) are ignored), as
 are the commands that cannot be performed (e.g. popping an empty stack or dividing by zero) ; division rounds towards
 negative infinity and mod has the sign of the divisor. A program that does not halt within 1000 steps per color block
 (with a minimum of 1 million) is stopped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dangermouse.net/esoteric/piet.html
"""
import struct
import zlib
from math import gcd

from ._brainfuck import MIN_STEPS, STEPS_PER_COMMAND
from ..__common__ import *


# push 2, out(number), then pop into a block from which the interpreter cannot leave
_PROGRAM = "P3 4 2 255\n255 192 192  255 0 0  192 0 192  255 0 255\n255 192 192  0 0 0  255 0 255  255 0 255\n"
__examples__ = {
    'enc-dec(piet|piet-1|piet-3)': ["", "Hello World!", "@random{64}", "Caf\xe9, \xf1and\xfa & 10€", "\x00a\x00"],
    'dec(piet)': {
        _PROGRAM:                                                   "2",
        # same program, with comments in the PPM header and a white codel to slide through instead of executing
        #  out(number) (moving from or to a white codel executes no command)
        "P3 # comment\n5 2 255\n255 192 192  255 0 0  255 255 255  192 0 192  255 0 255\n"
        "255 192 192  0 0 0  0 0 0  255 0 255  255 0 255\n":       "",
        # unknown format or color, truncated image, bad codel size
        "GIF00a":                                                   None,
        _PROGRAM.replace("255 0 0", "1 2 3"):                        None,
        _PROGRAM[:-10]:                                             None,
    },
    'dec(piet-3)': {_PROGRAM: None},
}
__guess__ = ["piet"]


# colors as (hue, lightness) indices, hue * 3 + lightness, then white and black
_COLORS = [(0xFF, 0xC0, 0xC0), (0xFF, 0x00, 0x00), (0xC0, 0x00, 0x00), (0xFF, 0xFF, 0xC0), (0xFF, 0xFF, 0x00),
           (0xC0, 0xC0, 0x00), (0xC0, 0xFF, 0xC0), (0x00, 0xFF, 0x00), (0x00, 0xC0, 0x00), (0xC0, 0xFF, 0xFF),
           (0x00, 0xFF, 0xFF), (0x00, 0xC0, 0xC0), (0xC0, 0xC0, 0xFF), (0x00, 0x00, 0xFF), (0x00, 0x00, 0xC0),
           (0xFF, 0xC0, 0xFF), (0xFF, 0x00, 0xFF), (0xC0, 0x00, 0xC0), (0xFF, 0xFF, 0xFF), (0x00, 0x00, 0x00)]
WHITE, BLACK = 18, 19
_INDICES = {c: i for i, c in enumerate(_COLORS)}
# commands, indexed by hue change * 3 + lightness change
_CMDS = [None, "push", "pop", "add", "sub", "mul", "div", "mod", "not", "greater", "pointer", "switch", "dup", "roll",
         "inn", "inc", "outn", "outc"]
# directions of the DP: right, down, left, up
_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
MAX_BITS = 1 << 16


def _err(msg):
    raise PietDecodeError(f"'piet' codec can't decode: {msg}")


def _commands(text):
    """ Commands printing the text, as (command, value). """
    cmds = []
    def _push(v):
        if v == 0:
            cmds.extend([("push", 1), ("not", None)])
        elif v <= 256:
            cmds.append(("push", v))
        else:
            q, r = divmod(v, 256)
            _push(q)
            cmds.extend([("push", 256), ("mul", None)] + [("push", r), ("add", None)] * (r > 0))
    for c in text:
        _push(ord(c))
        cmds.append(("outc", None))
    return cmds


def _png(rows):
    """ Write rows of colors (indices) as a PNG image. """
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    raw = b"".join(b"\x00" + bytes(v for i in row for v in _COLORS[i]) for row in rows)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", len(rows[0]), len(rows), 8, 2, 0, 0, 0)) + \
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _program(cmds, codel_size=1):
    """ Rows of colors (indices) of a program executing the given commands, as (command, value pushed), then halting.

    Each block is filled column by column from the first row, which the interpreter follows from left to right (leaving
     each block from its top right codel), the block before a command being as large as the value pushed. """
    # push 1 then pop into the final block, so that the last two blocks before it hold a single codel each
    cmds = cmds + [("push", 1), ("pop", None)]
    sizes = [v if c == "push" else 1 for c, v in cmds]
    h = max(2, int((max(sizes) - 1) ** .5) + 1)
    cols, color = [], 0
    for (c, _), size in zip(cmds, sizes):
        for j in range(0, size, h):
            cols.append([color] * min(h, size - j) + [WHITE] * (h - min(h, size - j)))
        dh, dl = divmod(_CMDS.index(c), 3)
        color = (color // 3 + dh) % 6 * 3 + (color % 3 + dl) % 3
    # the final block (right of the last block, below it and right of it) is surrounded by black codels and the edges,
    #  so that the interpreter halts there
    cols[-2][1:] = [BLACK] + cols[-2][2:]
    cols[-1][1:] = [color] + [BLACK] * (h - 2)
    cols.append([color, color] + [BLACK] * (h - 2))
    return [[c[y] for c in cols for _ in range(codel_size)] for y in range(h) for _ in range(codel_size)]


def piet_encode(codel_size=None):
    def encode(text, errors="strict"):
        return _png(_program(_commands(ensure_str(text)), int(codel_size or 1))), len(text)
    return encode


def _read_png(data):
    w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", data[16:29])
    pos, palette, idat = 8, [], bytearray()
    while pos < len(data):
        n, t = struct.unpack(">I4s", data[pos:pos+8])
        if t == b"PLTE":
            palette = [tuple(data[pos+8+i:pos+11+i]) for i in range(0, n, 3)]
        elif t == b"IDAT":
            idat += data[pos+8:pos+8+n]
        elif t == b"IEND":
            break
        pos += n + 12
    raw, pos = zlib.decompress(bytes(idat)), 0
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    bits, bpp = channels * depth, max(1, channels * depth // 8)
    pixels = [[None] * w for _ in range(h)]
    passes = [(0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)] \
             if interlace else [(0, 0, 1, 1)]
    for x0, y0, dx, dy in passes:
        pw, ph = (w - x0 + dx - 1) // dx, (h - y0 + dy - 1) // dy
        if pw <= 0 or ph <= 0:
            continue
        stride, prev = (pw * bits + 7) // 8, bytearray((pw * bits + 7) // 8)
        for y in range(ph):
            f, line = raw[pos], bytearray(raw[pos+1:pos+1+stride])
            if len(line) < stride:
                raise IndexError
            pos += stride + 1
            if f == 2:
                line = bytearray((a + b) & 255 for a, b in zip(line, prev))
            elif f in (1, 3, 4):
                for i in range(stride):
                    a, b, c = line[i-bpp] if i >= bpp else 0, prev[i], prev[i-bpp] if i >= bpp else 0
                    if f == 1:
                        line[i] = (line[i] + a) & 255
                    elif f == 3:
                        line[i] = (line[i] + (a + b) // 2) & 255
                    else:
                        p = a + b - c
                        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                        line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            elif f != 0:
                raise ValueError
            prev = line
            if depth < 8:
                m = (1 << depth) - 1
                samples = [line[i * depth // 8] >> (8 - depth - i * depth % 8) & m for i in range(pw * channels)]
                if ctype == 0:
                    samples = [s * 255 // m for s in samples]
            else:
                samples = line[::depth // 8]
            for x in range(pw):
                s = samples[x*channels:(x+1)*channels]
                pixels[y0 + y * dy][x0 + x * dx] = palette[s[0]] if ctype == 3 else tuple(s[:3]) if ctype & 2 else \
                                                    (s[0], ) * 3
    return pixels


def _read_gif(data):
    pos, flags, palette = 13, data[10], None
    if flags & 0x80:
        palette, pos = data[13:13 + 3 * (2 << (flags & 7))], 13 + 3 * (2 << (flags & 7))
    while data[pos] == 0x21:
        pos += 2
        while data[pos]:
            pos += data[pos] + 1
        pos += 1
    if data[pos] != 0x2C:
        raise ValueError
    w, h, flags = *struct.unpack("<HH", data[pos+5:pos+9]), data[pos+9]
    pos += 10
    if flags & 0x80:
        palette, pos = data[pos:pos + 3 * (2 << (flags & 7))], pos + 3 * (2 << (flags & 7))
    min_size, pos, stream = data[pos], pos + 1, bytearray()
    while data[pos]:
        stream += data[pos+1:pos+1+data[pos]]
        pos += data[pos] + 1
    # LZW decompression, codes being read from the least significant bits
    clear, out, buf, nbits, prev = 1 << min_size, bytearray(), 0, 0, None
    size, table = min_size + 1, [bytes([i]) for i in range(clear)] + [b"", b""]
    for byte in stream:
        buf, nbits = buf | byte << nbits, nbits + 8
        while nbits >= size:
            code, buf, nbits = buf & ((1 << size) - 1), buf >> size, nbits - size
            if code == clear:
                size, table, prev = min_size + 1, table[:clear + 2], None
                continue
            if code == clear + 1:
                break
            if code < len(table):
                entry = table[code]
                if prev is not None and len(table) < 4096:
                    table.append(prev + entry[:1])
            elif code == len(table) and prev is not None:
                table.append(entry := prev + prev[:1])
            else:
                raise ValueError
            out += entry
            prev = entry
            if len(table) == 1 << size and size < 12:
                size += 1
        else:
            continue
        break
    if len(out) < w * h or 3 * max(out) + 3 > len(palette):
        raise IndexError
    rows = [out[y*w:(y+1)*w] for y in range(h)]
    if flags & 0x40:
        order = [y for y0, dy in [(0, 8), (4, 8), (2, 4), (1, 2)] for y in range(y0, h, dy)]
        rows = [r for _, r in sorted(zip(order, rows))]
    return [[tuple(palette[3*i:3*i+3]) for i in r] for r in rows]


def _read_ppm(data):
    fields, pos = [], 2
    while len(fields) < 3 + (data[:2] == b"P3") * 10 ** 9:
        while data[pos:pos+1].isspace() or data[pos:pos+1] == b"#":
            if data[pos:pos+1] == b"#":
                pos = data.index(b"\n", pos)
            pos += 1
        if pos >= len(data):
            break
        start = pos
        while pos < len(data) and not data[pos:pos+1].isspace() and data[pos:pos+1] != b"#":
            pos += 1
        fields.append(int(data[start:pos]))
    w, h, m = fields[:3]
    if data[:2] == b"P3":
        samples = fields[3:]
    else:
        n = 1 + (m > 255)
        if len(data) < pos + 1 + 3 * w * h * n:
            raise IndexError
        samples = [int.from_bytes(data[pos+1+i:pos+1+i+n], "big") for i in range(0, 3 * w * h * n, n)]
    if len(samples) < 3 * w * h:
        raise IndexError
    samples = [s * 255 // m for s in samples]
    return [[tuple(samples[3*(y*w+x):3*(y*w+x)+3]) for x in range(w)] for y in range(h)]


def piet_run(image, codel_size=None, max_steps=None, errors="strict"):
    """ Run a Piet program from a PNG, GIF or PPM image and return its output.

    :param image:      image, as bytes
    :param codel_size: size of the codels (guessed by default)
    :param max_steps:  maximum number of steps (moves of the interpreter), for stopping programs that do not halt (by
                        default, 1000 per color block, with a minimum of 1 million)
    :param errors:     errors handling, for the colors other than those of Piet
    """
    try:
        if image[:8] == b"\x89PNG\r\n\x1a\n":
            pixels = _read_png(image)
        elif image[:6] in (b"GIF87a", b"GIF89a"):
            pixels = _read_gif(image)
        elif image[:2] in (b"P3", b"P6"):
            pixels = _read_ppm(image)
        else:
            _err("unsupported image format (PNG, GIF or PPM expected)")
    except (IndexError, KeyError, TypeError, ValueError, struct.error, zlib.error) as e:
        if isinstance(e, PietDecodeError):
            raise
        _err("invalid image")
    h, w = len(pixels), len(pixels[0]) if pixels else 0
    if w == 0 or h == 0:
        _err("empty image")
    # the codel size divides the lengths of all the runs of pixels of the same color
    if codel_size is None:
        codel_size = gcd(w, h)
        for lines in [pixels, list(zip(*pixels))]:
            for line in lines:
                n = 1
                for a, b in zip(line, line[1:]):
                    if a == b:
                        n += 1
                    else:
                        codel_size, n = gcd(codel_size, n), 1
                codel_size = gcd(codel_size, n)
    elif w % codel_size or h % codel_size:
        _err(f"bad codel size {codel_size} for an image of {w}x{h} pixels")
    _h, s = handle_error("piet", errors, decode=True, kind="color"), codel_size
    w, h, grid = w // s, h // s, []
    for y in range(h):
        grid.append(row := [])
        for x in range(w):
            if (c := _INDICES.get(pixels[y*s][x*s])) is None:
                _h("#%02x%02x%02x" % pixels[y*s][x*s], f"({x*s},{y*s})")
                c = WHITE
            row.append(c)
    # color blocks, by flood fill
    block, blocks = [[None] * w for _ in range(h)], []
    for y in range(h):
        for x in range(w):
            if grid[y][x] < WHITE and block[y][x] is None:
                codels, todo, block[y][x] = [], [(x, y)], len(blocks)
                while todo:
                    cx, cy = todo.pop()
                    codels.append((cx, cy))
                    for dx, dy in _DIRS:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and block[ny][nx] is None and grid[ny][nx] == grid[y][x]:
                            block[ny][nx] = len(blocks)
                            todo.append((nx, ny))
                blocks.append([grid[y][x], codels, {}])

    def _exit(b, dp, cc):
        """ Exit codel of a block, the furthest in the direction of the DP, then in that of the CC (left meaning
             counterclockwise from the DP). """
        if (dp, cc) not in (exits := blocks[b][2]):
            (dx, dy), (ex, ey) = _DIRS[dp], _DIRS[(dp + [3, 1][cc]) % 4]
            exits[dp, cc] = max(blocks[b][1], key=lambda c: (c[0] * dx + c[1] * dy, c[0] * ex + c[1] * ey))
        return exits[dp, cc]

    free = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] != BLACK
    max_steps = max_steps or max(MIN_STEPS, STEPS_PER_COMMAND * len(blocks))
    x, y, dp, cc, stack, out, steps, attempts = 0, 0, 0, 0, [], [], 0, 0
    while True:
        if (steps := steps + 1) > max_steps:
            raise ValueError(f"program did not halt within {max_steps} steps")
        if grid[y][x] == BLACK:
            break
        if grid[y][x] == WHITE:
            # slide through white codels in the direction of the DP, toggling the CC and rotating the DP clockwise when
            #  blocked, halting when retracing the path
            seen = set()
            while grid[y][x] == WHITE:
                if (steps := steps + 1) > max_steps:
                    raise ValueError(f"program did not halt within {max_steps} steps")
                if (x, y, dp) in seen:
                    return "".join(out)
                seen.add((x, y, dp))
                if free(nx := x + _DIRS[dp][0], ny := y + _DIRS[dp][1]):
                    x, y = nx, ny
                else:
                    cc, dp = 1 - cc, (dp + 1) % 4
            attempts = 0
            continue
        b = block[y][x]
        ex, ey = _exit(b, dp, cc)
        nx, ny = ex + _DIRS[dp][0], ey + _DIRS[dp][1]
        if not free(nx, ny):
            # when blocked, alternately toggle the CC and rotate the DP clockwise, halting after 8 attempts
            if (attempts := attempts + 1) == 8:
                break
            if attempts % 2:
                cc = 1 - cc
            else:
                dp = (dp + 1) % 4
            continue
        x, y, attempts = nx, ny, 0
        if grid[y][x] == WHITE:
            continue
        c1, c2 = blocks[b][0], grid[y][x]
        cmd = (c2 // 3 - c1 // 3) % 6 * 3 + (c2 % 3 - c1 % 3) % 3
        n = len(stack)
        if cmd == 1:
            stack.append(len(blocks[b][1]))
        elif cmd == 2 and n:
            stack.pop()
        elif 3 <= cmd <= 7 and n >= 2 and (cmd < 6 or stack[-1] != 0) or cmd == 9 and n >= 2:
            v2, v1 = stack.pop(), stack.pop()
            v = [v1 + v2, v1 - v2, v1 * v2, v1 // v2 if v2 else 0, v1 % v2 if v2 else 0, 0, int(v1 > v2)][cmd - 3]
            if v.bit_length() > MAX_BITS:
                raise ValueError(f"value larger than {MAX_BITS} bits")
            stack.append(v)
        elif cmd == 8 and n:
            stack.append(int(not stack.pop()))
        elif cmd == 10 and n:
            dp = (dp + stack.pop()) % 4
        elif cmd == 11 and n:
            cc ^= stack.pop() % 2
        elif cmd == 12 and n:
            stack.append(stack[-1])
        elif cmd == 13 and n >= 2 and 0 <= stack[-2] <= n - 2:
            r, d = stack.pop(), stack.pop()
            if d:
                r %= d
                stack[-d:] = stack[-r:] + stack[-d:-r] if r else stack[-d:]
        elif cmd == 16 and n:
            out.append(str(stack.pop()))
        elif cmd == 17 and n and 0 <= stack[-1] <= 0x10ffff:
            out.append(chr(stack.pop()))
    return "".join(out)


def piet_decode(codel_size=None):
    def decode(text, errors="strict"):
        return (r := piet_run(b(text), int(codel_size) if codel_size else None, errors=errors)), len(r)
    return decode


add("piet", piet_encode, piet_decode, r"^piet(?:[-_]([1-9][0-9]*))?$", guess=__guess__, expansion_factor=None)
