# -*- coding: UTF-8 -*-
"""LDAP Hashing Codecs - string hashing with the LDAP password schemes.

The RFC 2307 password schemes store a password in an LDAP directory as a scheme name (e.g. "{MD5}") followed by the
 Base64 digest of the password, the salted variants ("{SMD5}" and "{SSHA}") appending a random salt to the password
 before hashing and to the digest before encoding (hence their output differs between calls). These codecs return the
 hash string (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc2307
"""
import os
from base64 import b64encode

from ..__common__ import *


def ldap_hash(prefix, algo, salted):
    def _hash(text, errors="strict"):
        salt = os.urandom(4) if salted else b""
        return prefix + b64encode(hashlib.new(algo, b(text) + salt).digest() + salt).decode(), len(text)
    return _hash


add("ldap-md5", ldap_hash("{MD5}", "md5", False), pattern=r"^ldap[-_]md5$", guess=None)
add("ldap-sha1", ldap_hash("{SHA}", "sha1", False), pattern=r"^ldap[-_]sha1$", guess=None)
add("ldap-salted-md5", ldap_hash("{SMD5}", "md5", True), pattern=r"^ldap[-_](?:salted[-_]md5|smd5)$", guess=None)
add("ldap-salted-sha1", ldap_hash("{SSHA}", "sha1", True), pattern=r"^ldap[-_](?:salted[-_]sha1|ssha)$", guess=None)
