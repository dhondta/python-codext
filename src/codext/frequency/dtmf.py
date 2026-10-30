# -*- coding: UTF-8 -*-
"""DTMF Codec - Dual-Tone Multi-Frequency content encoding.

Dual-Tone Multi-Frequency (DTMF) signaling, standardised as ITU-T Q.23, is used by telephones to send the keys pressed
 on their keypad: each key is sent as the sum of two tones, one of the 4 tones of the low group (697, 770, 852 and
 941 Hz, for the rows of the keypad) and one of the 4 tones of the high group (1209, 1336, 1477 and 1633 Hz, for its
 columns), giving 16 keys:

            1209 Hz  1336 Hz  1477 Hz  1633 Hz
    697 Hz     1        2        3        A
    770 Hz     4        5        6        B
    852 Hz     7        8        9        C
    941 Hz     *        0        #        D

Encoding gives the frequencies of the tones in Hz, separated by spaces (the low one first, letters being uppercased),
 while decoding accepts both tones of a key in any order. With the "-wav" variant, encoding gives a WAV recording
 (8 kHz, 16 bits, mono) of the keys (each tone lasting 100 ms, followed by a silence of 100 ms), while decoding detects
 the keys in a WAV recording (PCM, of any sample rate, sample width and number of channels) with the Goertzel algorithm.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.itu.int/rec/T-REC-Q.23
"""
import struct
import wave
from math import cos, pi, sin

from ..__common__ import *


__examples__ = {
    'enc(dtmf)': {'1': "697 1209", '*0#D': "941 1209 941 1336 941 1477 941 1633", 'abcd': "697 1633 770 1633 852 1633 "
                  "941 1633", 'E': None},
    'dec(dtmf)': {'697 1209 1336 770': "15", '697': None, '697 770': None, '697 1210': None},
    'enc-dec(dtmf|dtmf-wav)': ["", "0123456789", "*#ABCD", "112233", "5"],
    'dec(dtmf-wav)': {'RIFF': None, 'not a wav file': None},
}
__guess__ = ["dtmf"]


DTMF_LOW, DTMF_HIGH = [697, 770, 852, 941], [1209, 1336, 1477, 1633]
DTMF_KEYS = ["123A", "456B", "789C", "*0#D"]
DTMF_TONES = {k: (DTMF_LOW[r], DTMF_HIGH[c]) for r, row in enumerate(DTMF_KEYS) for c, k in enumerate(row)}
DTMF_PAIRS = {frozenset(map(str, tones)): k for k, tones in DTMF_TONES.items()}
# parameters of the generated recordings
RATE, TONE, PAUSE, AMPLITUDE = 8000, .1, .1, .4
# parameters of the detection: blocks of 25.6 ms (205 samples at 8 kHz, as with the usual detectors) overlapping by
#  half, tolerance on the frequencies (ITU-T Q.24 requiring to accept deviations of 1.5%, tones being accepted up to
#  about 3% and rejected from 4%), minimal energy of the blocks (relative to the loudest one), minimal share of the
#  energy of a block in each tone and in both tones, and minimal ratio between the tone of a group and the other tones
#  of this group
BLOCK, DRIFT, MIN_ENERGY, MIN_SHARE, MIN_SHARES, MIN_RATIO = .0256, .015, 1e-3, .03, .2, 4.


def _err(msg):
    raise DtmfDecodeError(f"'dtmf' codec can't decode: {msg}")


def _to_wav(keys):
    """ Write a WAV recording of the keys. """
    samples, n = [], int(RATE * TONE)
    for k in keys:
        f1, f2 = DTMF_TONES[k]
        samples.extend(round(32767 * AMPLITUDE * (sin(2 * pi * f1 * i / RATE) + sin(2 * pi * f2 * i / RATE)))
                       for i in range(n))
        samples.extend([0] * int(RATE * PAUSE))
    buf = BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def _from_wav(data):
    """ Read the samples of a WAV recording (as integers, averaged on the channels) and its sample rate, averaging the
         samples by groups to bring the sample rate down to about 8 kHz. """
    try:
        with wave.open(BytesIO(data)) as w:
            channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
            frames = w.readframes(w.getnframes())
    except (EOFError, wave.Error) as e:
        _err(f"invalid WAV file ({e})" if str(e) else "invalid WAV file")
    if width == 1:
        samples = [x - 128 for x in frames]
    elif width == 3:
        samples = [int.from_bytes(frames[i:i+3], "little", signed=True) for i in range(0, len(frames) - 2, 3)]
    else:
        samples = struct.unpack(f"<{len(frames) // width}{'h' if width == 2 else 'i'}",
                                frames[:len(frames) // width * width])
    samples = [sum(samples[i:i+channels]) / channels for i in range(0, len(samples) - channels + 1, channels)]
    k = max(1, rate // 8000)
    return [sum(samples[i:i+k]) / k for i in range(0, len(samples) - k + 1, k)], rate / k


def _detect(samples, rate):
    """ Detect the keys in the samples with the Goertzel algorithm (the power of a tone being the largest of those at
         its frequency and at the bounds of its tolerance), a key lasting at least two (overlapping) blocks and a
         dropout of a single block being ignored. """
    n = max(2, round(rate * BLOCK))
    coeffs = [[2 * cos(2 * pi * f * d / rate) for d in (1 - DRIFT, 1, 1 + DRIFT)] for f in DTMF_LOW + DTMF_HIGH]
    blocks = []
    for start in range(0, len(samples) - n + 1, n // 2):
        block, powers = samples[start:start+n], []
        for cs in coeffs:
            p = 0.
            for c in cs:
                s1 = s2 = 0.
                for x in block:
                    s1, s2 = x + c * s1 - s2, s1
                p = max(p, s1 * s1 + s2 * s2 - c * s1 * s2)
            powers.append(p)
        blocks.append((sum(x * x for x in block), powers))
    loudest, keys = max((e for e, _ in blocks), default=0), []
    for e, powers in blocks:
        key = None
        if e > 0 and e >= loudest * MIN_ENERGY:
            # shares of the energy of the block (a tone alone gives 1/2, each tone of a key gives 1/4)
            shares = [p / (n * e) for p in powers]
            low, high = shares[:4], shares[4:]
            r, c = low.index(max(low)), high.index(max(high))
            if low[r] >= MIN_SHARE and high[c] >= MIN_SHARE and low[r] + high[c] >= MIN_SHARES and \
               all(low[r] >= MIN_RATIO * s for i, s in enumerate(low) if i != r) and \
               all(high[c] >= MIN_RATIO * s for i, s in enumerate(high) if i != c):
                key = DTMF_KEYS[r][c]
        keys.append(key)
    # runs of identical detections, keeping the keys of at least two blocks, separated by more than one block
    runs = []
    for k in keys:
        if runs and runs[-1][0] == k:
            runs[-1][1] += 1
        else:
            runs.append([k, 1])
    r, last, gap = "", None, 0
    for k, length in runs:
        if k is not None and length >= 2:
            if k != last or gap > 1:
                r += k
            last, gap = k, 0
        else:
            gap += length
    return r


def dtmf_encode(variant=None):
    def encode(text, errors="strict"):
        _h, r = handle_error("dtmf", errors), []
        for i, c in enumerate(ensure_str(text)):
            c = c.upper() if c in "abcd" else c
            if c in DTMF_TONES:
                r.append(c if variant else "%d %d" % DTMF_TONES[c])
            # a replaced or left character is written as is in the frequencies, while it is dropped from a recording
            elif (c := _h(c, i)) and not variant:
                r.append(c)
        return _to_wav(r) if variant else " ".join(r), len(text)
    return encode


def dtmf_decode(variant=None):
    def decode(text, errors="strict"):
        if variant:
            return (r := _detect(*_from_wav(b(text)))), len(r)
        _h, r, tones = handle_error("dtmf", errors, decode=True, kind="tone"), "", ensure_str(text).split()
        i = 0
        while i < len(tones):
            # the two tones of a key are simultaneous, hence in any order ; otherwise, skip the first tone
            if (k := DTMF_PAIRS.get(frozenset(tones[i:i+2]))) is None or len(tones[i:i+2]) < 2:
                r += _h(tones[i], i, r)
                i += 1
                continue
            r, i = r + k, i + 2
        return r, len(text)
    return decode


add("dtmf", dtmf_encode, dtmf_decode, r"^dtmf(?:[-_](wav))?$", examples=__examples__, guess=__guess__,
    printables_rate=1.)
