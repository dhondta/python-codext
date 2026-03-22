# -*- coding: UTF-8 -*-
"""Letters Codec - letter indices-related content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import random

from ..__common__ import *


__examples__ = {
    'enc-dec(ipsum|lorem-ipsum)': ["This is a test !"],
    'enc(ipsum)':                 {'Bad test#': None},
}


DICT = {
    'a': ['a', 'ac', 'accumsan', 'ad', 'adipiscing', 'aenean', 'aliquam', 'aliquet', 'amet', 'ante', 'aptent', 'arcu',
          'at', 'auctor', 'augue'],
    'b': ['babel', 'bibendum', 'blandit', 'bomba', 'botum', 'buxus'],
    'c': ['class', 'commodo', 'condimentum', 'congue', 'consectetur', 'consequat', 'conubia', 'convallis', 'cras',
          'cubilia', 'curabitur', 'curae', 'cursus'],
    'd': ['dapibus', 'diam', 'dictum', 'dictumst', 'dignissim', 'dis', 'dolor', 'donec', 'dui', 'duis'],
    'e': ['efficitur', 'egestas', 'eget', 'eleifend', 'elementum', 'elit', 'enim', 'erat', 'eros', 'est', 'et', 'etiam',
          'eu', 'euismod', 'ex'],
    'f': ['facilisis', 'fames', 'faucibus', 'felis', 'fermentum', 'feugiat', 'finibus', 'fringilla', 'fusce'],
    'g': ['gadus', 'galliarus', 'ganeo', 'garba', 'gemma', 'gener', 'genuine', 'gestus', 'gramma', 'gravida', 'grex',
          'gusto', 'guttur', 'gyro'],
    'h': ['habitant', 'habitasse', 'hac', 'haicu', 'halo', 'helleborum', 'hendrerit', 'hilarius', 'himenaeos',
          'horreum', 'hydrus', 'hystericus'],
    'i': ['iaculis', 'id', 'imperdiet', 'in', 'inceptos', 'integer', 'interdum', 'ipsum'],
    'j': ['jaccae', 'jacio', 'jecur', 'jocundiatas', 'jovis', 'juctim', 'juger', 'juno', 'jussum', 'justo'],
    'k': ['kal', 'kalatorium', 'kalium', 'kaput', 'kardo', 'kenia', 'koppa', 'kum'],
    'l': ['lacinia', 'lacus', 'laoreet', 'lectus', 'leo', 'libero', 'ligula', 'litora', 'lobortis', 'lorem', 'luctus'],
    'm': ['maecenas', 'magna', 'magnis', 'malesuada', 'massa', 'mattis', 'mauris', 'maximus', 'metus', 'mi', 'molestie',
          'mollis', 'montes', 'morbi', 'mus'],
    'n': ['nam', 'nascetur', 'natoque', 'nec', 'neque', 'netus', 'nibh', 'nisi', 'nisl', 'non', 'nostra', 'nulla',
          'nullam', 'nunc'],
    'o': ['odio', 'orci', 'ornare'],
    'p': ['parturient', 'pellentesque', 'penatibus', 'per', 'pharetra', 'phasellus', 'placerat', 'platea', 'porta',
          'porttitor', 'posuere', 'potenti', 'praesent', 'pretium', 'primis', 'proin', 'pulvinar', 'purus'],
    'q': ['qua', 'quadrum', 'quam', 'quasi', 'quintum', 'quis', 'quisque', 'quo', 'quom', 'quota', 'qur'],
    'r': ['radicitus', 'radius', 'ratio', 'recidivus', 'rectio', 'rhoncus', 'ridiculus', 'risus', 'ros', 'rutrum'],
    's': ['sagittis', 'sapien', 'scelerisque', 'sed', 'sem', 'semper', 'senectus', 'sit', 'sociosqu', 'sodales',
          'sollicitudin', 'suscipit', 'suspendisse'],
    't': ['taciti', 'tellus', 'tempor', 'tempus', 'tincidunt', 'torquent', 'tortor', 'tristique', 'turpis'],
    'u': ['ullamcorper', 'ultrices', 'ultricies', 'urna', 'ut'],
    'v': ['varius', 'vehicula', 'vel', 'velit', 'venenatis', 'vestibulum', 'vitae', 'vivamus', 'volutpat', 'vulputate'],
    'w': ['wadiarus', 'warantus', 'warra', 'werumensium', 'wormicia'],
    'x': ['xandicus', 'xenon', 'xenium', 'xiphias', 'xvir', 'xylon', 'xysticus', 'xystus'],
    'y': ['yata', 'yatum', 'yatus', 'ypra'],
    'z': ['zamia', 'zelosus', 'zerum', 'zonatus', 'zymus'],
}
SCHARS = "0123456789.,:;!?+=-*/\\"


def ipsum_encode(text, errors="strict"):
    s, strip = "", False
    for i, c in enumerate(text):
        try:
            if c == " " or c in SCHARS:
                s += c
                strip = False
            else:
                w = random.choice(DICT[c.lower()])
                s += (w.capitalize() if c.isupper() else w) + " "
                strip = True
        except KeyError:
            s += handle_error("ipsum", errors, " ")(c, i)
    return s[:-1] if strip else s, len(text)


def ipsum_decode(text, errors="strict"):
    s = ""
    words = text.split(" ")
    for i, w in enumerate(words[:-1] if words[-1] == "" else words):
        if w.strip() == "":
            s += " "
        elif w in SCHARS:
            s += w
        else:
            try:
                if w.lower().strip(SCHARS) not in DICT[w[0].lower()]:
                    raise KeyError
                s += w[:len(w)-len(w.lstrip(SCHARS))] + w.strip(SCHARS)[0] + w[len(w.rstrip(SCHARS)):len(w)]
            except KeyError:
                s += handle_error("ipsum", errors, decode=True, item="word")(w, i)
    return s, len(text)


add("ipsum", ipsum_encode, ipsum_decode, pattern=r"^(?:lorem[-_]?)?ipsum$", printables_rate=1.,
    expansion_factor=(6., .5))

