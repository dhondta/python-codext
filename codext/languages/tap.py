# -*- coding: UTF-8 -*-
"""Tap code - Tap/knock code encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(tap)': {'this is a test' : '.... ....  .. ...  .. ....  .... ...  .. ....  .... ...  . .  .... ....  . .....  .... ...  .... ....'},
    'dec(tap)': {'.... ....  .. ...  .. ....  .... ...  .. ....  .... ...  . .  .... ....  . .....  .... ...  .... ....' : 'thisisatest'}
}


def build_encmap(map) : 
    dict = {}
    i = 0
    for col in range(1,6) : 
        for row in range(1,6) : 
            dict[map[i]] = "" + col * "." + " " + row * "."
            i += 1
    dict['k'] = dict['c']
    return dict

def encode_tap(text, errors = 'strict') : 
    map = 'abcdefghijlmnopqrstuvwxyz'
    ENCMAP = build_encmap(map)
    encoded = ""
    for i, letter in enumerate(text) :
        try : 
            encoded += ENCMAP[letter.lower()]
        except KeyError : 
            pass
        if i != len(text) - 1 and letter != ' ': 
            encoded += '  '
    return encoded, len(text)    


def decode_tap(text, errors = 'ignore') : 
    map = 'abcdefghijlmnopqrstuvwxyz'
    ENCMAP = build_encmap(map)
    decoded = ""
    for elem in text.split("  ") :
        try : 
            decoded += next(key for key, value in ENCMAP.items() if value == elem)
        except StopIteration : 
            print("Invalid character(s) in the input. This is what could be decoded :")
    return decoded, len(text)    
  

add("tap", encode_tap, decode_tap, ignore_case="both")

