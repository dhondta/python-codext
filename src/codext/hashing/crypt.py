# -*- coding: UTF-8 -*-
"""Case Codecs - string hashing with Unix's Crypt.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
from ..__common__ import add, ensure_str, PY3, UNIX


if PY3 and UNIX:
    import crypt
    
    METHODS = [x[7:].lower() for x in crypt.__dict__ if x.startswith("METHOD_")]
    
    def crypt_hash(method):
        method = (method or "").lstrip("-_") or "blowfish"
        if method not in METHODS:
            raise NotImplementedError("method '%s' is not implemented" % method)
        def _encode(input, error="strict"):
            m = getattr(crypt, "METHOD_" + method.upper())
            return crypt.crypt(ensure_str(input), crypt.mksalt(m)), len(input)
        return _encode
    
    add("crypt", crypt_hash, pattern=r"^crypt(|[-_](?:%s))$" % "|".join(METHODS), guess=None)

