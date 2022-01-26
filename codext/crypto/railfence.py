# -*- coding: UTF-8 -*-
"""Rail Fence Cipher Codec - rail fence encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""



from ..__common__ import *


__examples__ = {
    'enc(rail-5-3|rail_5_3)': {'this is a test' : 'it sss etiath '},
    'enc(rail-5-3-up|rail_5_3-up)' :{'this is a test': 'h tiats e ssit'},
    'dec(rail-7-4|rail_7_4)': {'a  stiet shsti': 'this is a test'}
}



def __buildf(text, rails, offset = 0, up = 0) : 
    l, rail = len(text), offset
    if up != '' :
        dr = -1
        rail = rails - offset - 1
    else : 
        dr = 1

    f = [["#"] * l for i in range(rails)]

    for x in range(l) : 
        f[rail][x] = text[x]
        if rail >= rails - 1:
            dr = -1
        elif rail <= 0:
            dr = 1
        rail += dr
    return f

def railfence_encode(rails = 3, offset = 0, up = 0) :  
    def encode(text, errors="strict") : 
        c,l = '', len(text)
        f = __buildf(text, rails, offset, up)
        for r in range(rails) : 
            for x in range(l) :
                if f[r][x] != '#' : 
                    c += f[r][x]
        return c, l
    return encode

def railfence_decode(rails = 3, offset = 0, up = 0) : 
    def decode(text, errors = 'strict') : 
        f = __buildf("x" * len(text), rails, offset, up)
        plain, i = '', 0
        ra, l = range(rails), range(len(text))

        #Put the characters in the right place
        for r in ra:
            for x in l :            
                if f[r][x] == "x" : 
                    f[r][x] = text[i]
                    i += 1
        #Read the characters in the right order
        for x in l : 
            for r in ra:
                if f[r][x] != '#' : 
                    plain += f[r][x]

        return plain, len(plain)

    return decode

add("rail", railfence_encode, railfence_decode, r"rail[-_](\d+)[-_](\d+)[-_]?(up)?$")
