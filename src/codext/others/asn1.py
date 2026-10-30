# -*- coding: UTF-8 -*-
"""ASN.1 Codecs - ASN.1 BER and DER content encoding.

ASN.1 (Abstract Syntax Notation One, ITU-T X.680) describes data structures, that the Basic Encoding Rules (BER) and
 the Distinguished Encoding Rules (DER, a canonical subset of BER, used e.g. by X.509 certificates and keys), defined in
 ITU-T X.690, write as nested type-length-value elements: an identifier (class, primitive or constructed form and tag
 number, e.g. 0x30 for a SEQUENCE), a length (on one byte below 128, otherwise the number of bytes of the length
 followed by these bytes, BER also allowing an indefinite length ended by two null bytes) and the content.

- "der" and "ber" encode the text as a UTF8String element (e.g. "hi" gives b"\\x0c\\x02hi"), and decode an element of a
   string type (e.g. UTF8String, OCTET STRING, PrintableString, IA5String or BMPString), the character strings giving
   text and the octet and bit strings giving their bytes, "ber" also accepting indefinite lengths, strings split into
   segments (constructed form) and non-minimal lengths.
- "asn1" decodes BER or DER elements to a readable dump in a notation close to the ASN.1 value notation (e.g.
   "SEQUENCE {", "INTEGER 5", "OBJECT IDENTIFIER 2.5.4.3  -- commonName", "OCTET STRING '0A1B'H" or "[0] {"), the
   strings and bit strings holding a DER SEQUENCE or SET (e.g. the keys or the extensions of certificates) being dumped
   as well, and encodes such a dump to DER (sorting the elements of the sets), giving back the bytes of DER elements.

Malformed elements and dumps are reported whatever the errors handling.

These codecs:
- en/decode strings from str to str
- en/decode strings from bytes to bytes
- decode file content to str (read)
- encode file content from str to bytes (write)

Reference: https://www.itu.int/rec/T-REC-X.690
"""
import json

from ..__common__ import *


__examples1__ = {
    'enc(der)': {'hi': "\x0c\x02hi", '': "\x0c\x00"},
    'dec(der)': {'\x0c\x02hi': "hi", '\x04\x02hi': "hi", '\x13\x02hi': "hi", '\x1e\x04\x00h\x00i': "hi",
                 '\x0c\x81\x02hi': None, '$\x80\x04\x02hi\x00\x00': None, '\x0c\x03hi': None, '\x02\x01\x05': None},
    'enc-dec(der)': ["", "Hello, World!", "caf\xe9 € \U0001f600", "@random{300}"],
}
__examples2__ = {
    'enc(ber)': {'hi': "\x0c\x02hi"},
    'dec(ber)': {'\x0c\x81\x02hi': "hi", '$\x80\x04\x01h\x04\x01i\x00\x00': "hi", '$\x06\x04\x01h\x04\x01i': "hi",
                 '#\x80\x03\x02\x00h\x03\x02\x00i\x00\x00': "hi", '\x0c\x03hi': None, '$\x80\x04\x01h': None},
    'enc-dec(ber)': ["", "Hello, World!", "@random{300}"],
}
__examples3__ = {
    'enc(asn1)': {'SEQUENCE {\n  INTEGER 5\n  UTF8String "hi"\n}': "0\x07\x02\x01\x05\x0c\x02hi",
                  'NULL': "\x05\x00", 'INTEGER x': None, 'SEQUENCE {': None, '}': None},
    'dec(asn1)': {'0\x07\x02\x01\x05\x0c\x02hi': 'SEQUENCE {\n  INTEGER 5\n  UTF8String "hi"\n}',
                  '0\x05\x02\x01': None},
    'enc-dec(asn1)': ['SEQUENCE {\n  BOOLEAN TRUE\n  INTEGER -129\n  OBJECT IDENTIFIER 2.5.4.3  -- commonName\n}'],
}


UNIVERSAL = {1: "BOOLEAN", 2: "INTEGER", 3: "BIT STRING", 4: "OCTET STRING", 5: "NULL", 6: "OBJECT IDENTIFIER",
             7: "ObjectDescriptor", 8: "EXTERNAL", 9: "REAL", 10: "ENUMERATED", 11: "EMBEDDED PDV", 12: "UTF8String",
             13: "RELATIVE-OID", 16: "SEQUENCE", 17: "SET", 18: "NumericString", 19: "PrintableString",
             20: "T61String", 21: "VideotexString", 22: "IA5String", 23: "UTCTime", 24: "GeneralizedTime",
             25: "GraphicString", 26: "VisibleString", 27: "GeneralString", 28: "UniversalString",
             29: "CHARACTER STRING", 30: "BMPString"}
TAGS = {v.upper(): k for k, v in UNIVERSAL.items()}
TAGS.update({'TELETEXSTRING': 20, 'SET OF': 17, 'SEQUENCE OF': 16})
# character encodings of the string types (their restricted character sets not being checked)
STRINGS = {7: "latin-1", 12: "utf-8", 18: "latin-1", 19: "latin-1", 20: "latin-1", 21: "latin-1", 22: "latin-1",
           23: "latin-1", 24: "latin-1", 25: "latin-1", 26: "latin-1", 27: "latin-1", 28: "utf-32-be", 30: "utf-16-be"}
CONSTRUCTED = {8, 11, 16, 17, 29}
CLASSES = ["UNIVERSAL", "APPLICATION", "", "PRIVATE"]
MAX_DEPTH = 256
# names of common object identifiers, given as comments in the dumps
OIDS = {
    '1.2.840.113549.1.1.1': "rsaEncryption", '1.2.840.113549.1.1.4': "md5WithRSAEncryption",
    '1.2.840.113549.1.1.5': "sha1WithRSAEncryption", '1.2.840.113549.1.1.10': "rsassa-pss",
    '1.2.840.113549.1.1.11': "sha256WithRSAEncryption", '1.2.840.113549.1.1.12': "sha384WithRSAEncryption",
    '1.2.840.113549.1.1.13': "sha512WithRSAEncryption", '1.2.840.113549.1.7.1': "data",
    '1.2.840.113549.1.7.2': "signedData", '1.2.840.113549.1.7.3': "envelopedData", '1.2.840.113549.1.9.1':
    "emailAddress", '1.2.840.113549.1.9.3': "contentType", '1.2.840.113549.1.9.4': "messageDigest",
    '1.2.840.113549.1.9.5': "signingTime", '1.2.840.113549.1.9.14': "extensionRequest",
    '1.2.840.10045.2.1': "ecPublicKey", '1.2.840.10045.3.1.7': "prime256v1", '1.3.132.0.34': "secp384r1",
    '1.3.132.0.35': "secp521r1", '1.2.840.10045.4.3.2': "ecdsa-with-SHA256", '1.2.840.10045.4.3.3':
    "ecdsa-with-SHA384", '1.2.840.10045.4.3.4': "ecdsa-with-SHA512", '1.3.101.110': "X25519", '1.3.101.112': "Ed25519",
    '1.3.14.3.2.26': "sha1", '2.16.840.1.101.3.4.2.1': "sha256", '2.16.840.1.101.3.4.2.2': "sha384",
    '2.16.840.1.101.3.4.2.3': "sha512", '2.5.4.3': "commonName", '2.5.4.4': "surname", '2.5.4.5': "serialNumber",
    '2.5.4.6': "countryName", '2.5.4.7': "localityName", '2.5.4.8': "stateOrProvinceName", '2.5.4.9': "streetAddress",
    '2.5.4.10': "organizationName", '2.5.4.11': "organizationalUnitName", '2.5.4.12': "title", '2.5.4.42':
    "givenName", '2.5.29.14': "subjectKeyIdentifier", '2.5.29.15': "keyUsage", '2.5.29.17': "subjectAltName",
    '2.5.29.19': "basicConstraints", '2.5.29.30': "nameConstraints", '2.5.29.31': "cRLDistributionPoints",
    '2.5.29.32': "certificatePolicies", '2.5.29.35': "authorityKeyIdentifier", '2.5.29.37': "extKeyUsage",
    '1.3.6.1.5.5.7.1.1': "authorityInfoAccess", '1.3.6.1.5.5.7.3.1': "serverAuth", '1.3.6.1.5.5.7.3.2': "clientAuth",
    '1.3.6.1.5.5.7.3.3': "codeSigning", '1.3.6.1.5.5.7.3.4': "emailProtection", '1.3.6.1.5.5.7.48.1': "ocsp",
    '1.3.6.1.5.5.7.48.2': "caIssuers", '1.3.6.1.4.1.11129.2.4.2': "ctPrecertificateSCTs",
    '0.9.2342.19200300.100.1.25': "domainComponent",
}


def _error(ename, msg, decode=True):
    exc = {'asn1': (Asn1DecodeError, Asn1EncodeError), 'ber': (BerDecodeError,), 'der': (DerDecodeError,)}[ename]
    raise exc[0 if decode else 1](f"'{ename}' codec can't {['en', 'de'][decode]}code: {msg}")


# ------------------------------------------------ BER/DER parsing -----------------------------------------------------
def _parse(data, strict, err):
    """ Parse BER (or DER, if strict) elements as nodes [class, constructed, tag, content], the content being the bytes
         of a primitive element or the list of the nodes of a constructed element. """
    def _element(pos, end, depth):
        if depth > MAX_DEPTH:
            err("elements nested too deeply")
        b0, start = data[pos], pos
        cls, cons, tag, pos = b0 >> 6, bool(b0 & 0x20), b0 & 0x1f, pos + 1
        if tag == 0x1f:
            tag = 0
            while True:
                if pos >= end:
                    err(f"truncated tag at offset {start}")
                x = data[pos]
                # X.690 forbids leading zero bits and the long form for tags below 31, in BER as in DER
                if tag == 0 and x == 0x80:
                    err(f"non-minimal tag at offset {start}")
                tag, pos = tag << 7 | x & 0x7f, pos + 1
                if not x & 0x80:
                    break
            if tag < 31:
                err(f"non-minimal tag at offset {start}")
        if pos >= end:
            err(f"truncated length at offset {start}")
        l0, pos = data[pos], pos + 1
        if l0 == 0x80:
            # indefinite length, ended by the end-of-contents element (two null bytes)
            if strict:
                err(f"indefinite length at offset {start}")
            if not cons:
                err(f"indefinite length of a primitive element at offset {start}")
            children = []
            while data[pos:pos+2] != b"\0\0":
                if pos >= end:
                    err(f"missing end-of-contents of the element at offset {start}")
                child, pos = _element(pos, end, depth + 1)
                children.append(child)
            return [cls, cons, tag, children], pos + 2
        length = l0
        if l0 & 0x80:
            n = l0 & 0x7f
            if n == 0x7f or pos + n > end:
                err(f"bad length at offset {start}")
            length = int.from_bytes(data[pos:pos+n], "big")
            if strict and (length < 0x80 or data[pos] == 0):
                err(f"non-minimal length at offset {start}")
            pos += n
        if pos + length > end:
            err(f"truncated content of the element at offset {start}")
        if not cons:
            return [cls, cons, tag, data[pos:pos+length]], pos + length
        children, p = [], pos
        while p < pos + length:
            child, p = _element(p, pos + length, depth + 1)
            children.append(child)
        return [cls, cons, tag, children], pos + length

    nodes, pos = [], 0
    while pos < len(data):
        node, pos = _element(pos, len(data), 0)
        nodes.append(node)
    return nodes


def _flatten(node, err):
    """ Content of a string element, joining the segments of a constructed (BER) string. """
    cls, cons, tag, content = node
    if not cons:
        return content
    segments = []
    for child in content:
        if child[0] != 0 or child[2] not in (tag, 3 if tag == 3 else 4):
            err("bad segment of a constructed string")
        segments.append(_flatten(child, err))
    if tag != 3:
        return b"".join(segments)
    if any(len(s) < 1 or s[0] != 0 for s in segments[:-1]) or segments and len(segments[-1]) < 1:
        err("bad segment of a constructed bit string")
    return (segments[-1][:1] if segments else b"\0") + b"".join(s[1:] for s in segments)


def _input(text, ename, strict):
    """ Parse the elements of the input, as codext gives bytes as str (read as UTF-8, or as latin-1 if not valid),
         trying the bytes as latin-1, then as UTF-8 (e.g. for an element holding "é" in UTF-8). Valid elements read as
         latin-1 are always parsed from their original bytes ; a malformed one may rarely be read as UTF-8. """
    err = lambda msg: _error(ename, msg)
    candidates = [b(text)]
    if (u := text.encode("utf-8", "surrogatepass")) != candidates[0]:
        candidates.append(u)
    errors = []
    for data in candidates:
        try:
            return _parse(data, strict, err)
        except ValueError as e:
            errors.append(e)
    # the error of the first reading of the input is the relevant one
    raise errors[0]


# ------------------------------------------------ DER encoding --------------------------------------------------------
def _identifier(cls, cons, tag):
    if tag < 31:
        return bytes([cls << 6 | cons << 5 | tag])
    t = [tag & 0x7f]
    while tag := tag >> 7:
        t.insert(0, tag & 0x7f | 0x80)
    return bytes([cls << 6 | cons << 5 | 0x1f] + t)


def _length(n):
    if n < 0x80:
        return bytes([n])
    k = (n.bit_length() + 7) // 8
    return bytes([0x80 | k]) + n.to_bytes(k, "big")


def _encode(node):
    """ DER encoding of a node, the content of a primitive string being possibly a list of encapsulated nodes. """
    cls, cons, tag, content = node
    if isinstance(content, list):
        parts = [_encode(child) for child in content]
        # DER sorts the elements of the sets by their encodings
        if cons and cls == 0 and tag == 17 and parts:
            width = max(map(len, parts))
            parts.sort(key=lambda p: p.ljust(width, b"\0"))
        content = (b"\0" if not cons and tag == 3 else b"") + b"".join(parts)
    return _identifier(cls, cons, tag) + _length(len(content)) + content


# ------------------------------------------------ Dump writing --------------------------------------------------------
def _hex(content):
    return f"'{content.hex().upper()}'H"


def _oid(content, relative=False):
    """ Arcs of a canonical (relative) object identifier, or None. """
    if not content or content[-1] & 0x80:
        return
    arcs, v, start = [], 0, True
    for x in content:
        if start and x == 0x80:
            return
        v, start = v << 7 | x & 0x7f, not x & 0x80
        if start:
            arcs.append(v)
            v = 0
    if not relative:
        a = min(arcs[0] // 40, 2)
        arcs[:1] = [a, arcs[0] - 40 * a]
    return ".".join(map(str, arcs))


def _encapsulated(content):
    """ Nodes of a canonical DER SEQUENCE or SET encapsulated in a string, or None. """
    if len(content) >= 2 and content[0] in (0x30, 0x31):
        try:
            nodes = _parse(content, True, _raise)
        except ValueError:
            return
        if len(nodes) == 1 and _encode(nodes[0]) == content:
            return nodes


def _raise(msg):
    raise ValueError(msg)


def _value(tag, content):
    """ Value of a primitive element of a universal type in the dump, as (value, comment), or None for an hexadecimal
         dump of the content. """
    if tag == 1 and content in (b"\0", b"\xff"):
        return ["FALSE", "TRUE"][content == b"\xff"], ""
    if tag in (2, 10) and content and not (len(content) > 1 and (content[0] == 0 and content[1] < 0x80 or
                                                                 content[0] == 0xff and content[1] >= 0x80)):
        n = int.from_bytes(content, "big", signed=True)
        return (str(n) if abs(n) < 1 << 64 else "-" * (n < 0) + hex(abs(n))), ""
    if tag == 3 and content and content[0] < 8 and (len(content) > 1 or content[0] == 0) and \
       not content[-1] & ((1 << content[0]) - 1):
        bits = "".join(f"{x:08b}" for x in content[1:])
        return (_hex(content[1:]) if content[0] == 0 else f"'{bits[:len(bits) - content[0]]}'B"), ""
    if tag == 4:
        return _hex(content), ""
    if tag == 5 and content == b"":
        return "", ""
    if tag in (6, 13) and (oid := _oid(content, tag == 13)) is not None:
        return oid, OIDS.get(oid, "") if tag == 6 else ""
    if tag in STRINGS:
        try:
            s = content.decode(STRINGS[tag])
            if s.encode(STRINGS[tag]) == content:
                return json.dumps(s), ""
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass


def _dump(node, depth, lines, err):
    cls, cons, tag, content = node
    indent, name = "  " * depth, UNIVERSAL.get(tag) if cls == 0 else None
    # constructed (BER) strings are dumped as primitive ones
    if name and cons and tag in STRINGS.keys() | {3, 4}:
        cons, content = False, _flatten(node, err)
    if name and cons != (tag in CONSTRUCTED):
        name = None
    header = name or f"[{(CLASSES[cls] + ' ') * (cls != 2)}{tag}]"
    if cons:
        if not content:
            lines.append(f"{indent}{header} {{}}")
            return
        lines.append(f"{indent}{header} {{")
        for child in content:
            _dump(child, depth + 1, lines, err)
        lines.append(f"{indent}}}")
        return
    # strings holding a DER SEQUENCE or SET (a bit string without unused bits)
    if name and tag in (3, 4) and (nodes := _encapsulated(content[1:] if tag == 3 and content[:1] == b"\0" else
                                                           content if tag == 4 else b"")):
        lines.append(f"{indent}{header} {{")
        for child in nodes:
            _dump(child, depth + 1, lines, err)
        lines.append(f"{indent}}}")
        return
    value, comment = (_value(tag, content) if name else None) or (_hex(content), "")
    lines.append(f"{indent}{header}" + f" {value}" * (value != "") + f"  -- {comment}" * (comment != ""))


# ------------------------------------------------ Dump parsing --------------------------------------------------------
_HEADER = re.compile(r"\[(?:(UNIVERSAL|APPLICATION|CONTEXT|PRIVATE)\s+)?(\d+)\]|(" + "|".join(
                     sorted(map(re.escape, TAGS), key=len, reverse=True)).replace(r"\ ", r"\s+") + r")(?![\w-])", re.I)
_VALUE = re.compile(r"""("(?:[^"\\]|\\.)*")|'([0-9A-Fa-f\s]*)'H|'([01\s]*)'B|(-?0x[0-9A-Fa-f]+|-?\d+)(?![.\d])|"""
                    r"""(TRUE|FALSE)\b|(\d+(?:\.\d+)*)|(\{\s*\}|\{)""", re.I)


def _primitive(named, tag, token, err):
    """ Content of a primitive element from its value in the dump, given by the name of its universal type or by its
         tag (then only with an hexadecimal content). """
    s, hx, bits, num, boolean, oid, _ = token
    hx = None if hx is None else re.sub(r"\s", "", hx)
    if hx is not None and not (named and tag == 3):
        return bytes.fromhex(hx.zfill(len(hx) + len(hx) % 2))
    if not named:
        err("the content of an element given by its tag must be hexadecimal")
    if tag == 3 and (hx is not None or bits is not None):
        bits = re.sub(r"\s", "", bits) if bits is not None else "".join(f"{x:08b}" for x in bytes.fromhex(hx))
        return bytes([-len(bits) % 8]) + int(bits.ljust(-(-len(bits) // 8) * 8, "0") or "0", 2).to_bytes(
               -(-len(bits) // 8), "big")
    if tag == 1 and boolean:
        return b"\xff" if boolean.upper() == "TRUE" else b"\0"
    if tag in (2, 10) and num:
        n = int(num, 0)
        return n.to_bytes(max(1, (n if n >= 0 else ~n).bit_length() // 8 + 1), "big", signed=True)
    if tag in (6, 13) and (oid or num and not num.startswith(("-", "0x"))):
        arcs = list(map(int, (oid or num).split(".")))
        if tag == 6:
            if len(arcs) < 2 or arcs[0] > 2 or arcs[0] < 2 and arcs[1] >= 40:
                err(f"bad object identifier {oid or num}")
            arcs[:2] = [40 * arcs[0] + arcs[1]]
        content = b""
        for a in arcs:
            t = [a & 0x7f]
            while a := a >> 7:
                t.insert(0, a & 0x7f | 0x80)
            content += bytes(t)
        return content
    if s is not None and (tag in STRINGS or tag == 4):
        try:
            return json.loads(s).encode(STRINGS.get(tag, "utf-8"), "surrogatepass")
        except UnicodeEncodeError:
            err(f"string not encodable as {UNIVERSAL[tag]}: {s}")
    err(f"bad value for {UNIVERSAL.get(tag, f'[UNIVERSAL {tag}]')}")


def _parse_dump(text, err):
    """ Parse a dump as nodes, line by line. """
    stack, root = [], []
    for i, line in enumerate(text.splitlines(), 1):
        e = lambda msg: err(f"{msg} (line {i})")
        line = line.strip()
        if line == "" or line.startswith("--"):
            continue
        if line == "}":
            if not stack:
                e("unexpected '}'")
            stack.pop()
            continue
        if not (m := _HEADER.match(line)):
            e(f"unknown type in '{line[:30]}'")
        named = bool(m.group(3))
        if named:
            cls, tag = 0, TAGS[re.sub(r"\s+", " ", m.group(3).upper())]
        else:
            k = (m.group(1) or "CONTEXT").upper()
            cls, tag = 2 if k == "CONTEXT" else CLASSES.index(k), int(m.group(2))
        rest = line[m.end():].strip()
        # the value (or the opening brace), followed by an optional comment
        if rest == "" or rest.startswith("--"):
            if not (named and tag == 5):
                e("missing value")
            content = b""
            token = None
        else:
            if not (mv := _VALUE.match(rest)) or rest[mv.end():].strip() not in ("",) and \
               not rest[mv.end():].strip().startswith("--"):
                e(f"bad value '{rest[:30]}'")
            token = mv.groups()
        if token and token[6]:
            constructed = not named or tag in CONSTRUCTED
            if not constructed and not (named and tag in (3, 4)):
                e(f"{UNIVERSAL.get(tag, tag)} cannot hold elements")
            node = [cls, constructed, tag, []]
            (stack[-1][3] if stack else root).append(node)
            if token[6] == "{":
                stack.append(node)
            continue
        if token:
            if named and tag in CONSTRUCTED:
                e(f"{UNIVERSAL[tag]} must hold elements")
            try:
                content = _primitive(named, tag, token, e)
            except ValueError as x:
                # errors other than those of the codec (e.g. of a JSON string) are reported with the line number
                if isinstance(x, Asn1EncodeError):
                    raise
                e(str(x))
        (stack[-1][3] if stack else root).append([cls, False, tag, content])
    if stack:
        err("missing '}'")
    return root


# ------------------------------------------------ Codecs --------------------------------------------------------------
def string_encode(ename):
    def encode(text, errors="strict"):
        content = ensure_str(text).encode("utf-8", "surrogatepass")
        return _encode([0, False, 12, content]), len(text)
    return encode


def string_decode(ename):
    def decode(text, errors="strict"):
        err = lambda msg: _error(ename, msg)
        nodes = _input(ensure_str(text), ename, ename == "der")
        if len(nodes) != 1:
            err("expected a single element")
        cls, cons, tag, _ = node = nodes[0]
        if cls != 0 or tag not in STRINGS.keys() | {3, 4}:
            err("not an element of a string type")
        if cons and ename == "der":
            err("constructed string")
        content = _flatten(node, err)
        # octet and bit strings give their bytes, character strings their text
        if tag == 3:
            if content[:1] != b"\0":
                err("bit string with unused bits")
            content = content[1:]
        elif tag != 4:
            try:
                content = content.decode(STRINGS[tag])
            except UnicodeDecodeError:
                err(f"bad {UNIVERSAL[tag]}")
        return content, len(text)
    return decode


def asn1_encode(text, errors="strict"):
    nodes = _parse_dump(ensure_str(text), lambda msg: _error("asn1", msg, False))
    return b"".join(map(_encode, nodes)), len(text)


def asn1_decode(text, errors="strict"):
    lines = []
    for node in _input(ensure_str(text), "asn1", False):
        _dump(node, 0, lines, lambda msg: _error("asn1", msg))
    return "\n".join(lines), len(text)


der_encode, der_decode = string_encode("der"), string_decode("der")
ber_encode, ber_decode = string_encode("ber"), string_decode("ber")


add("der", der_encode, der_decode, r"^der$", examples=__examples1__, guess=["der"])
add("ber", ber_encode, ber_decode, r"^ber$", examples=__examples2__, guess=["ber"])
add("asn1", asn1_encode, asn1_decode, r"^asn[-_.]?1$", examples=__examples3__, guess=None)
