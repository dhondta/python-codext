# -*- coding: UTF-8 -*-
"""Enigma Codec - Enigma machine content encoding.

The Enigma machine is a rotor cipher machine used by the German armed forces during World War II. Each letter goes
 through the plugboard, the rotors (from right to left), the reflector, then the rotors again (from left to right) and
 the plugboard. Before each letter, the rightmost rotor steps, the middle rotor steps when the rightmost one passes its
 notch, and the leftmost rotor steps when the middle one passes its notch (the middle one then also steps, which is
 known as the double stepping anomaly). As the reflector is an involution, the same settings decrypt the ciphertext.

This codec emulates the Enigma I and M3 (three rotors among I to VIII, with reflector A, B or C) and the M4 (with the
 Beta or Gamma rotor as the fourth one, leftmost and fixed, and the thin reflector B or C). The settings are given with
 the codec name, as "enigma-[reflector]-[rotors]-[rings]-[positions]-[plugboard]" (from the left to the right of the
 machine), each part being optional from the right:
- reflector: "a", "b", "c", "bthin" or "cthin" (default: "b")
- rotors: their numbers (1 to 8), prefixed with "b" (Beta) or "g" (Gamma) for the M4 (default: "123")
- rings: the ring settings, as letters (default: "a" for each rotor)
- positions: the initial positions, as letters (default: "a" for each rotor)
- plugboard: the pairs of swapped letters, concatenated (e.g. "avbscg" for A-V, B-S and C-G ; default: none)

Only the letters are encrypted (keeping their case) ; other characters are left unchanged and do not step the rotors.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Enigma_rotor_details
           https://www.cryptomuseum.com/crypto/enigma/wiring.htm
"""
from string import ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(enigma-d)':                       None,
    'enc(enigma-b-122)':                   None,
    'enc(enigma-b-b123)':                  None,
    'enc(enigma-bthin-123)':               None,
    'enc(enigma-b-123-ab)':                None,
    'enc(enigma-b-123-aaa-aaaa)':          None,
    'enc(enigma-b-123-aaa-aaa-abc)':       None,
    'enc(enigma-b-123-aaa-aaa-abca)':      None,
    'enc(enigma|enigma_cipher|enigma-b-123|enigma-b-123-aaa-aaa)': {'AAAAA': "BDZGO",
                                                                   'Hello, world. This is a test.':
                                                                   "Ilbda, amtaz. Morn zd d iotu."},
    'enc(enigma-b-123-aaa-aaz)':           {'AAAAAAAAAAAAAAAAAAAAAAAAAA': "UBDZGOWCXLTKSBTMCDLPBMUQOF"},
    'enc(enigma-b-123-aaa-adu)':           {'AAAAA': "EQIBM"},
    'enc(enigma-b-123-qch-adf)':           {'AAAAAAAAAAAAAAAAAAAAAAAAAA': "TEVFKUTIIWEDWVIJPMVPGDEZSP"},
    'enc(enigma-bthin-b123-aopd-xefq)':    {'AAAAAAAAAAAAAAAAAAAAAAAAAA': "GZXGXQUSUWJPWVIGVBTUDQZNZJ"},
    'enc(enigma-cthin-g654-aamw-ljgu)':    {'AAAAAAAAAAAAAAAAAAAAAAAAAA': "HZJLPIKWBZXNCWFFIHWLEROOZC"},
    'enc(enigma-bthin-g748-aiou-ivoz-wnmjlxybfpqdusihcegr)':
                                           {'AAAAAAAAAAAAAAAAAAAAAAAAAA': "GHLIMOJIUWDKLWMJGNJKDYJVDK"},
    'enc-dec(enigma-a-678-xyz-qmj-azbycx)': ["ATTACK AT DAWN", "This is a test !", "Café, ñandú & 10€"],
}
__guess__ = []


# rotor wirings and notches (letters in the window when the next rotor steps), the fourth rotors (M4) and reflectors
ROTORS = {
    '1': ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    '2': ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    '3': ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    '4': ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    '5': ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
    '6': ("JPGVOUMFYQBENHZRDKASXLICTW", "ZM"),
    '7': ("NZJHGRCXMYSWBOUFAIVLPEKQDT", "ZM"),
    '8': ("FKQHTLXOCBJSPDZRAMEWNIUYGV", "ZM"),
    'b': ("LEYJVCNIXWPBQMDRTAKZGFUHOS", ""),
    'g': ("FSOKANUERHMBTIYCWLQPZXVGJD", ""),
}
REFLECTORS = {
    'a':     "EJMZALYXVBWFCRQUONTSPIKHGD",
    'b':     "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    'c':     "FVPJIAOYEDRZXWGCTKUQSBNMHL",
    'bthin': "ENKQAUYWJICOPBLMDXZVFTHRGS",
    'cthin': "RDOBJNTKVEHMLFCWZAXGYIPSUQ",
}


def __set_params(reflector, rotors, rings, positions, plugboard):
    # rotors given as digits only are converted to an integer when parsing the codec name
    reflector, rotors = (reflector or "b").lower(), str(rotors or "123").lower()
    m4 = len(rotors) == 4
    if not re.match(r"^[bg]?[1-8]{3}$", rotors) or len(set(rotors)) != len(rotors):
        raise LookupError("Bad parameter for encoding 'enigma': rotors must be 3 distinct numbers from 1 to 8, "
                          "prefixed with 'b' or 'g' for the M4")
    if m4 != reflector.endswith("thin"):
        raise LookupError("Bad parameter for encoding 'enigma': the M4 (4 rotors) requires a thin reflector, and a "
                          "thin reflector requires the M4")
    rings, positions = (rings or "a" * len(rotors)).upper(), (positions or "a" * len(rotors)).upper()
    if len(rings) != len(rotors) or len(positions) != len(rotors):
        raise LookupError("Bad parameter for encoding 'enigma': rings and positions must be given for each rotor")
    plugboard, plugs = (plugboard or "").upper(), list(range(26))
    if len(plugboard) % 2 or len(set(plugboard)) != len(plugboard):
        raise LookupError("Bad parameter for encoding 'enigma': plugboard must be pairs of distinct letters")
    for a, b in zip(plugboard[::2], plugboard[1::2]):
        plugs[UC.index(a)], plugs[UC.index(b)] = UC.index(b), UC.index(a)
    return REFLECTORS[reflector], rotors, rings, positions, plugs


def enigma(reflector=None, rotors=None, rings=None, positions=None, plugboard=None):
    # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
    #  listing the encodings)
    try:
        refl, rotors, rings, positions, plugs = __set_params(reflector, rotors, rings, positions, plugboard)
    except LookupError as e:
        err = e
        def _code(text, errors="strict"):
            raise err
        return _code
    refl = [UC.index(c) for c in refl]
    # wirings (forward and backward), notches and ring settings, from the left to the right of the machine
    fwd = [[UC.index(c) for c in ROTORS[r][0]] for r in rotors]
    bwd = [[w.index(i) for i in range(26)] for w in fwd]
    notches = [{UC.index(c) for c in ROTORS[r][1]} for r in rotors]
    rings = [UC.index(c) for c in rings]
    def _code(text, errors="strict"):
        pos, r = [UC.index(c) for c in positions], []
        # the leftmost rotor of the M4 never steps, hence the rotors that step are always the 3 rightmost ones
        l, m, n = len(pos) - 3, len(pos) - 2, len(pos) - 1
        for c in ensure_str(text):
            if not (c.isascii() and c.isalpha()):
                r.append(c)
                continue
            # stepping, with the double stepping of the middle rotor
            step_m, step_l = pos[n] in notches[n] or pos[m] in notches[m], pos[m] in notches[m]
            pos[n] = (pos[n] + 1) % 26
            if step_m:
                pos[m] = (pos[m] + 1) % 26
            if step_l:
                pos[l] = (pos[l] + 1) % 26
            # plugboard, rotors from the right to the left, reflector, rotors from the left to the right, plugboard
            x = plugs[UC.index(c.upper())]
            for i in range(n, -1, -1):
                s = pos[i] - rings[i]
                x = (fwd[i][(x + s) % 26] - s) % 26
            x = refl[x]
            for i in range(n + 1):
                s = pos[i] - rings[i]
                x = (bwd[i][(x + s) % 26] - s) % 26
            x = UC[plugs[x]]
            r.append(x if c.isupper() else x.lower())
        return (r := "".join(r)), len(r)
    return _code


add("enigma", enigma, enigma, r"^enigma(?:[-_]cipher)?(?:[-_]([a-cA-C]|[bcBC]thin))?(?:[-_]([bgBG]?\d+))?"
    r"(?:[-_]([a-zA-Z]+))?(?:[-_]([a-zA-Z]+))?(?:[-_]([a-zA-Z]+))?$", printables_rate=1., penalty=.1)
