# -*- coding: UTF-8 -*-
from .gzipp import *
from .lz77 import *
from .lz78 import *
from .pkzip import *


for e in list_encodings("compression"):
    ci = lookup(e, False)
    ci.parameters['scoring']['entropy'] = 7.9
    ci.parameters['scoring']['expansion_factor'] = lambda f: f

