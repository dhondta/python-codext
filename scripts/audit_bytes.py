import json, sys
from functools import wraps
import codext, codext.__common__ as C, codext.utils as U

variant = sys.argv[1]
orig = C.fix_inout_formats

def make(variant):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            a0, enc = a[0], None
            if isinstance(a0, bytes):
                if variant == "p1":
                    x = a0.decode("latin-1")
                else:
                    try:
                        x, enc = a0.decode("utf-8"), "utf-8"
                    except UnicodeDecodeError:
                        x, enc = a0.decode("latin-1"), "latin-1"
            else:
                x = U.ensure_str(a0) if isinstance(a0, str) else a0
            r = f(x, *a[1:], **k)
            out = r[0] if isinstance(r, (tuple, list)) else r
            if isinstance(a0, bytes):
                if variant == "p2" and isinstance(out, str):
                    try:
                        out = out.encode(enc)
                    except UnicodeEncodeError:
                        out = U.b(out)
                else:
                    out = U.fix(out, a0)
            else:
                out = U.fix(out, a0)
            if isinstance(r, (tuple, list)):
                return (out, len(a0) if isinstance(a0, bytes) else r[1]) + tuple(r[2:])
            return out
        return w
    return deco

if variant != "current":
    C.fix_inout_formats = make(variant)
    codext.reset()

BYTES = [b"8\xc2\xb96", b"\xff\x00\x80abc", bytes(range(256))]
TEXT = ["café ça", "naïve résumé", "日本 ok"]
res = {}
names = set()
for e in codext.list_encodings():
    try:
        p = codext.lookup(e, False).parameters
    except Exception:
        continue
    if p.get("category") in ("native", "hashing", "checksum"):
        continue
    for g in (p.get("guess") or [e])[:2]:
        names.add((g, p.get("category")))
for e, cat in sorted(names):
    exact, textok, tested_b, tested_t = 0, 0, 0, 0
    for x in BYTES:
        try:
            enc = codext.encode(x, e)
            if codext.decode(enc, e) is None: continue
        except Exception:
            continue
        tested_b += 1
        try:
            d = codext.decode(enc, e); d = d if isinstance(d, bytes) else U.b(d)
            exact += d == x
        except Exception:
            pass
    for s in TEXT:
        try:
            ref = codext.encode(s, e)
            refb = ref if isinstance(ref, bytes) else ref.encode("utf-8")
            got = codext.encode(s.encode("utf-8"), e)
        except Exception:
            continue
        tested_t += 1
        textok += got == refb
    res[e] = {"cat": cat, "exact": [exact, tested_b], "text": [textok, tested_t]}
json.dump(res, open(sys.argv[2], "w"))
