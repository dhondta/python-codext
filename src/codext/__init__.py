# -*- coding: UTF-8 -*-
"""Codecs extension module.

"""
from .__common__ import *
from .__info__ import __author__, __copyright__, __email__, __license__, __source__, __version__


__all__ = ["add", "add_map", "clear", "decode", "encode", "guess", "lookup",  "open", "rank", "register", "remove",
           "reset"]

decode   = codecs.decode
encode   = codecs.encode
guess    = codecs.guess
lookup   = codecs.lookup
open     = codecs.open

_lst = list
list = list_encodings  # not included in __all__ because of shadow name


reset()


# populate codext with attributes from codecs that were not modified
for attr in codecs.__all__:
    if attr in __all__:
        continue
    locals()[attr] = getattr(codecs, attr)
    __all__.append(attr)
