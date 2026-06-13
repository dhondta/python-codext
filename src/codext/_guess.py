# -*- coding: UTF-8 -*-
"""Extracted guess/rank/score functionality from __common__.py."""
import codecs
import os
import re
from types import FunctionType

from .__common__ import (
    ensure_str, b, isb, lookup, list_encodings, search,
    CODECS_CACHE, CODECS_CATEGORIES, printable, entropy,
    LANG, decode, stopfunc,
)


def _detect(text):
    _lb, t = stopfunc.LANG_BACKEND, ensure_str(text)
    if _lb is None:
        raise ValueError("No language backend %s" % ["selected", "installed"][len(stopfunc.LANG_BACKENDS) == 0])
    return langid.classify(t)[0] if _lb == "langid" else \
           langdetect.detect(t) if _lb == "langdetect" else \
           pycld2.detect(t)[2][0][1] if _lb == "pycld2" else \
           cld3.get_language(t).language[:2] if _lb == "cld3" else \
           textblob.TextBlob(t).detect_language()[:2]


def _lang(lang):
    def _test(s):
        if not stopfunc.text(s):
            return False
        try:
            return _detect(ensure_str(s))[:2] == lang
        except:
            return False
    return _test


def _load_lang_backend(backend=None):
    # import the requested backend library if not imported yet
    if backend is None or backend in stopfunc.LANG_BACKENDS:
        stopfunc.LANG_BACKEND = backend
        if backend:
            globals()[backend] = __import__(backend)
    else:
        raise ValueError("Unsupported language detection backend")
    # remove language-related stop functions
    for attr in dir(stopfunc):
        if attr.startswith("_") or not isinstance(getattr(stopfunc, attr), FunctionType):
            continue
        if re.match(r"lang_[a-z]{2}$", attr):
            delattr(stopfunc, attr)
    # rebind applicable language-related stop functions
    if stopfunc.LANG_BACKEND:
        _lb = stopfunc.LANG_BACKEND
        if _lb == "langid":
            langid.langid.load_model()
        for lang in (
            langid.langid.identifier.nb_classes if _lb == "langid" else \
            list(set(p[:2] for p in os.listdir(langdetect.PROFILES_DIRECTORY))) if _lb == "langdetect" else \
            list(set(x[1][:2] for x in pycld2.LANGUAGES if x[0] in pycld2.DETECTED_LANGUAGES)) if _lb == "pycld2" else \
            stopfunc.CLD3_LANGUAGES if _lb == "cld3" else \
            stopfunc.TEXTBLOB_LANGUAGES if _lb == "textblob" else \
            []):
            n = f"lang_{lang}"
            setattr(stopfunc, n, _lang(lang))
            getattr(stopfunc, n).__name__ = getattr(stopfunc, n).__qualname__ = n
        if LANG:
            flng = f"lang_{LANG}"
            if getattr(stopfunc, flng, None):
                stopfunc.default = getattr(stopfunc, flng)


def _validate(stop_function, lang_backend="none"):
    s, lb = stop_function, lang_backend
    if isinstance(s, str):
        if re.match(r"lang_[a-z]{2}$", s) and lb != "none" and \
           all(re.match(r"lang_[a-z]{2}$", x) is None for x in dir(stopfunc)):
            stopfunc._reload_lang(lb)
        f = getattr(stopfunc, s, None)
        if f:
            return f
    elif not isinstance(s, FunctionType):
        raise ValueError("Bad stop function")
    return s


def __guess(prev_input, input, stop_func, depth, max_depth, min_depth, encodings, result, found=(),
            stop=True, show=False, scoring_heuristic=False, extended=False, debug=False):
    """ Perform a breadth-first tree search using a ranking logic to select and prune the list of codecs. """
    if depth > min_depth and stop_func(input):
        if not stop and (show or debug) and found not in result:
            s = repr(input)
            s = s[2:-1] if s.startswith("b'") and s.endswith("'") else s
            s = f"[+] {', '.join(found)}: {s}"
            print(s if len(s) <= 80 else f"{s[:77]}...")
        result[found] = input
    if depth >= max_depth or len(result) > 0 and stop:
        return
    prev_enc = found[-1] if len(found) > 0 else ""
    e = encodings.get(depth, encodings.get(-1, []))
    for new_input, encoding in __rank(prev_input, input, prev_enc, e, scoring_heuristic, extended):
        if len(result) > 0 and stop:
            return
        if debug:
            print(f"[*] Depth {depth+1:0{len(str(max_depth))}}/{max_depth}: {encoding}")
        __guess(input, new_input, stop_func, depth+1, max_depth, min_depth, encodings, result, found + (encoding, ),
                stop, show, scoring_heuristic, extended, debug)


def __make_encodings_dict(include, exclude):
    """ Process encodings inclusion and exclusion lists, listing categories and developping codecs' lists of possible
         encoding names. It also creates a cache with the CodecInfo objects for improving performance. """
    def _develop(d, keep=True):
        d = d or {}
        for k, v in d.items():
            l, cc, sc = [], [e for e in v if e in CODECS_CATEGORIES], [e for e in v if e not in CODECS_CATEGORIES]
            # list from in-scope categories and then everything that is not a category
            for enc in ((list_encodings(*cc) if (len(cc) > 0 or keep) and len(sc) == 0 else []) + sc):
                g = []
                for e in (search(enc, False) or [enc]):
                    try:
                        ci = lookup(e, False)
                        g.extend(ci.parameters['guess'])
                    except:
                        pass
                if enc in g:  # e.g. "rot-1" => ["rot-1", "rot-2", ...] ; only "rot-1" is to be selected
                    l.append(enc)
                else:         # e.g. "rot"   => ["rot-1", "rot-2", ...] ; all the "rot-N" shall be selected
                    l.extend(g)
            d[k] = list(set(l))
        return d
    _excl, _incl = _develop(exclude, False), _develop(include)
    return {k: [x for x in v if x not in _excl.get(k, [])] for k, v in _incl.items()}


def __rank(prev_input, input, prev_encoding, encodings, heuristic=False, extended=False, yield_score=False):
    """ Filter valid encodings and rank them by relevance. """
    ranking = {}
    for e in encodings:
        try:
            codec = CODECS_CACHE[e]
        except KeyError:
            try:
                CODECS_CACHE[e] = codec = lookup(e, False)
            except LookupError:
                continue
        t = __score(prev_input, input, prev_encoding, e, codec, heuristic, extended)
        if t:
            ranking[e] = t
    for encoding, result in sorted(ranking.items(), key=lambda x: (-x[1][0], x[0])):
        yield result if yield_score else result[1], encoding


class _Text(object):
    __slots__ = ["entropy", "lcharset", "len", "padding", "printables", "text"]
    
    def __init__(self, text, pad_char=None):
        self.text = ensure_str(text)
        c = self.text[-1]
        pad_char, last_char = (chr(pad_char), chr(c)) if isinstance(c, int) else (pad_char, c)
        self.padding = pad_char is not None and last_char == pad_char
        if self.padding:
            text = text.rstrip(b(pad_char) if isinstance(text, bytes) else pad_char)
        self.len = len(self.text)
        self.lcharset = len(set(self.text))
        self.printables = float(len([c for c in self.text if c in printable])) / self.len
        self.entropy = entropy(self.text)


def __score(prev_input, input, prev_encoding, encoding, codec, heuristic=False, extended=False):
    """ Score relevant encodings given an input. """
    obj = None
    sc = codec.parameters.get('scoring', {})
    no_error, transitive = codec.parameters.get('no_error', False), sc.get('transitive', False)
    # ignore encodings that fail to decode with their default errors handling value
    try:
        new_input = codec.decode(input)[0]
    except:
        return
    # ignore encodings that give an output identical to the input (identity transformation) or to the previous input
    if len(new_input) == 0 or prev_input is not None and b(input) == b(new_input) or b(prev_input) == b(new_input):
        return
    # ignore encodings that transitively give the same output (identity transformation by chaining twice a same
    #  codec (e.g. rot-15 is equivalent to rot-3 and rot-12 or rot-6 and rot-9)
    if transitive and prev_encoding:
        ci_prev = lookup(prev_encoding, False)
        if ci_prev.parameters['name'] == codec.parameters['name']:
            return
    # compute input's characteristics only once and only if the control flow reaches this point
    pad = sc.get('padding_char')
    if obj is None:
        obj = _Text(input, pad)
    if heuristic:
        # from here, the goal (e.g. if the input is Base32) is to rank candidate encodings (e.g. multiple base
        #  codecs) so that we can put the right one as early as possible and eventually exclude bad candidates
        s = -sc.get('penalty', .0)
        # first, apply a bonus if the length of input text's charset is exactly the same as encoding's charset ;
        #  on the contrary, if the length of input text's charset is strictly greater, give a penalty
        lcs = sc.get('len_charset', 256)
        if isinstance(lcs, type(lambda: None)):
            lcs = int(lcs(encoding))
        if (pad and obj.padding and lcs + 1 >= obj.lcharset) or lcs >= obj.lcharset:
            s += max(.0, round(.6 * (.99 ** (lcs - obj.lcharset)), 5) - .1)
        elif (pad and obj.padding and lcs + 1 < obj.lcharset) or lcs < obj.lcharset:
            s -= .2  # this can occur for encodings with no_error set to True
        # then, take padding into account, giving a bonus if padding is to be encountered and effectively present,
        #  or a penalty when it should not be encountered but it is present
        if pad and obj.padding:
            s += .2  # when padding is encountered while it is legitimate, it could be a good indication => bonus
        elif not pad and obj.padding:
            s -= .1  # it could arise a padding character is encountered while not being padding => small penalty
        # give a bonus when the rate of printable characters is greater or equal than expected and a penalty when
        #  lower only for codecs that DO NOT tolerate errors (otherwise, the printables rate can be biased)
        if not no_error:
            pr = sc.get('printables_rate', 0)
            if isinstance(pr, type(lambda: None)):
                pr = float(pr(obj.printables))
            if obj.printables - pr <= .05:
                s += .1
        expf = sc.get('expansion_factor', 1.)
        if expf:
            f = obj.len / float(len(new_input))  # expansion while encoding => at decoding: 1/f
            if isinstance(expf, type(lambda: None)):
                try:  # this case allows to consider the current encoding name from the current codec
                    expf = expf(f, encoding)
                except TypeError:
                    expf = expf(f)
            if isinstance(expf, (int, float)):
                expf = 1/f - .1 <= 1/expf <= 1/f + .1
            elif isinstance(expf, (tuple, list)) and len(expf) == 2:
                expf = 1/f - expf[1] <= 1/expf[0] <= 1/f + expf[1]
            s += [-1., .1][expf]
        # afterwards, if the input text has an entropy close to the expected one, give a bonus weighted on the
        #  number of input characters to take bad entropies of shorter strings into account
        entr = sc.get('entropy', lambda e: e)
        entr = entr.get(encoding, entr.get('default')) if isinstance(entr, dict) else entr
        if isinstance(entr, type(lambda: None)):
            try:  # this case allows to consider the current encoding name from the current codec
                entr = entr(obj.entropy, encoding)
            except TypeError:
                entr = entr(obj.entropy)
        if entr is not None:
            # use a quadratic heuristic to compute a weight for the entropy delta, aligned on (256,.2) and (512,1)
            d_entr = min(3.04575e-06 * obj.len**2 + .000394 * obj.len, 1) * abs(entr - obj.entropy)
            if d_entr <= .5:
                s += .5 - d_entr
        # finally, if relevant, apply a custom bonus (e.g. when a regex pattern is matched)
        bonus = sc.get('bonus_func')
        if bonus is not None:
            if isinstance(bonus, type(lambda: None)):
                bonus = bonus(obj, codec, encoding)
            if bonus:
                s += .2
    else:
        s = 1.
    # exclude negative (and eventually null) scores as they are (hopefully) not relevant
    if extended and s >= .0 or not extended and s > .0:
        return s, new_input


def guess(input, stop_func=stopfunc.default, min_depth=0, max_depth=5, include=None, exclude=None, found=(),
          stop=True, show=False, scoring_heuristic=True, extended=False, debug=False):
    """ Try decoding without the knowledge of the encoding(s).
    
    :param input:             input text to be guessed
    :param stop_func:         function defining the stop condition
    :param min_depth:         minimum search depth
    :param max_depth:         maximum search depth
    ;param include:           inclusion item OR list with category, codec or encoding names OR dictionary with lists per
                               depth (nothing means include every encoding)
    :param exclude:           exclusion item OR list with category, codec or encoding names OR dictionary with lists per
                               depth (nothing means exclude no encoding)
    :param found:             tuple of already found encodings
    :param stop:              whether to stop or not when a valid solution is found
    :param show:              whether to immediately show once a solution is found
    :param scoring_heuristic: whether to apply the scoring heuristic during the search (if disabled, all scores are 1.,
                               meaning that every non-failing encoding will be considered with no order of precedence)
    :param extended:          whether to also consider null scores with the heuristic
    :param debug:             whether to show each attempt at each depth during computation
    """
    if len(input) == 0:
        return ""
    # check for min and max depths
    if max_depth <= 0:
        raise ValueError("Depth must be a non-null positive integer")
    if min_depth > max_depth:
        raise ValueError("Min depth shall be less than or equal to the max depth")
    # take the tuple of found encodings into account
    if len(found) > 0:
        for encoding in found:
            input = decode(input, encoding)
    # handle the stop function as a regex if a string was given
    if isinstance(stop_func, str):
        stop_func = stopfunc.regex(stop_func)
    # reformat include and exclude arguments ; supported formats:
    for n, l in zip(["inc", "exc"], [include, exclude]):
        if l is None:
            if n == "inc":
                include = l = {-1: CODECS_CATEGORIES}
            else:
                exclude = l = {}
        #  "category" OR "enc_name" OR whatever => means a single item for all depths
        if isinstance(l, str):
            if n == "inc":
                include = l = {-1: [l]}
            else:
                exclude = l = {-1: [l]}
        #  ["enc_name1", "enc_name2", ...] => means for all depths
        if isinstance(l, (list, tuple)):
            if n == "inc":
                include = l = {-1: l}
            else:
                exclude = l = {-1: l}
        #  {-1: [...], 2: [...], ...}      => means prefedined depths with their lists of in-/excluded encodings
        if not isinstance(l, dict) or not all(isinstance(k, int) for k in l.keys()):
            raise ValueError("Include argument shall be a list or a dictionary with integer keys")
    # precompute encodings lists per depth and cache the related CodecInfo objects
    encodings, result = __make_encodings_dict(include, exclude), {}
    try:
        # breadth-first search
        for d in range(max_depth):
            __guess("", input, stop_func, 0, d+1, min_depth, encodings, result, tuple(found), stop, show,
                    scoring_heuristic, extended, debug)
            if stop and len(result) > 0:
                break
    except KeyboardInterrupt:
        pass
    CODECS_CACHE = {}
    return result


def rank(input, extended=False, limit=-1, include=None, exclude=None):
    """ Rank the most probable encodings based on the given input.
    
    :param input:    input text to be evaluated
    :param extended: whether to consider null scores too (NB: negative scores are not output !)
    :param limit:    number of encodings to be returned (-1 means all of them)
    :param include:  inclusion list with category, codec or encoding names (nothing means include every encoding)
    :param exclude:  exclusion list with category, codec or encoding names (nothing means exclude no encoding)
    """
    encodings = __make_encodings_dict(include if isinstance(include, dict) else {-1: include or CODECS_CATEGORIES},
                                      exclude if isinstance(exclude, dict) else {-1: exclude or []})
    r = list(__rank(None, input, "", encodings[-1], True, extended, True))
    return r[:limit] if len(r) > 1 else r
