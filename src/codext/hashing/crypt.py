# -*- coding: UTF-8 -*-
"""Crypt Hashing Codec - string hashing with Unix's Crypt.

crypt is the password hashing function of Unix systems, used to store the passwords in /etc/shadow. The method is given
 in the codec name among those available on the system (e.g. "crypt-sha512", "crypt-md5", Blowfish by default), a random
 salt being generated each time, hence the output differs between calls. This codec is only available on Unix, relying
 on the crypt module (or its legacycrypt replacement since Python 3.13), and returns the hash string (one-way), for use
 with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Crypt_(C)
"""
from ..__common__ import add, ensure_str, UNIX


if UNIX:
    try:
        import legacycrypt as crypt
    except ImportError:
        try:
            import crypt
        except ImportError:
            crypt = None
    
    if crypt is not None:
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

