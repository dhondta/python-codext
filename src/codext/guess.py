# -*- coding: UTF-8 -*-
"""Guess feature - automated decoding without the knowledge of the codec(s).

This module holds the ``stopfunc`` helpers and the scoring/search engine behind the ``guess`` and ``rank``
 functions. It depends on the codec registry and helpers from ``__common__`` (one-directional) and on the text rating
 functions from ``text``, and is wired into the ``codecs`` module on import.
"""
from importlib.util import find_spec
from itertools import chain
from time import perf_counter
from types import FunctionType, ModuleType

from .__common__ import *
from .__common__ import CODECS_CACHE, CODECS_CATEGORIES, _categories, __guess_lists
from .text import TEXTNESS_THRESHOLD, TEXTNESS_WEIGHT, _textness, entropy
from .utils import PRINTABLES


__all__ = ["guess", "rank", "stopfunc"]


def __module_exists(name):
    """ Check if a top-level module is installed, without importing it. """
    try:
        return find_spec(name) is not None
    except (ImportError, ValueError):
        return False


stopfunc = ModuleType("stopfunc", """
    Predefined stop functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This submodule contains stop functions for the guess feature of codext.
    
    - `flag`:       searches for the pattern "[Ff][Ll1][Aa4@][Gg9]" (either UTF-8 or UTF-16)
    - `lang_**`:    checks if the given lang (any from the PROFILES_DIRECTORY of the langdetect module) is detected
    - `printables`: checks that every output character is in the set of printables
    - `regex`:      takes one argument, the regular expression, for checking a string against the given pattern
    - `text`:       checks for printables and an entropy less than 4.6 (empirically determined)
    - `text_strict`: checks for `text` and a textness of at least TEXTNESS_THRESHOLD (rejects encoded-looking strings
                     such as Base64, hence searches deeper ; best used with a bound, e.g. guess(..., timeout=60))
""")
stopfunc.printables = lambda s: PRINTABLES.issuperset(ensure_str(s))
stopfunc.printables.__name__ = stopfunc.printables.__qualname__ = "printables"
stopfunc.regex = lambda p: lambda s: re.search(p, ensure_str(s)) is not None
stopfunc.regex.__name__ = stopfunc.regex.__qualname__ = "regex"
stopfunc.text = lambda s: stopfunc.printables(s) and entropy(s) < 4.6
stopfunc.text.__name__ = stopfunc.text.__qualname__ = "text"
stopfunc.text_strict = lambda s: stopfunc.text(s) and _textness(s) >= TEXTNESS_THRESHOLD
stopfunc.text_strict.__name__ = stopfunc.text_strict.__qualname__ = "text_strict"
stopfunc.flag = lambda x: re.search(r"[Ff][Ll1][Aa4@][Gg96]", ensure_str(x)) is not None
stopfunc.flag.__name__ = stopfunc.flag.__qualname__ = "flag"
stopfunc.default = stopfunc.text

stopfunc.LANG_BACKEND = None
stopfunc.LANG_BACKENDS = [n for n in ["pycld2", "langdetect", "langid", "cld3", "textblob"] if __module_exists(n)]
if len(stopfunc.LANG_BACKENDS) > 0:
    stopfunc.LANG_BACKEND = stopfunc.LANG_BACKENDS[0]
if "cld3" in stopfunc.LANG_BACKENDS:
    stopfunc.CLD3_LANGUAGES = "af|am|ar|bg|bn|bs|ca|ce|co|cs|cy|da|de|el|en|eo|es|et|eu|fa|fi|fr|fy|ga|gd|gl|gu|ha|" \
                              "hi|hm|hr|ht|hu|hy|id|ig|is|it|iw|ja|jv|ka|kk|km|kn|ko|ku|ky|la|lb|lo|lt|lv|mg|mi|mk|" \
                              "ml|mn|mr|ms|mt|my|ne|nl|no|ny|pa|pl|ps|pt|ro|ru|sd|si|sk|sl|sm|sn|so|sq|sr|st|su|sv|" \
                              "sw|ta|te|tg|th|tr|uk|ur|uz|vi|xh|yi|yo|zh|zu".split("|")
if "textblob" in stopfunc.LANG_BACKENDS:
    stopfunc.TEXTBLOB_LANGUAGES = "af|ar|az|be|bg|bn|ca|cs|cy|da|de|el|en|eo|es|et|eu|fa|fi|fr|ga|gl|gu|hi|hr|ht|hu|" \
                                  "id|is|it|iw|ja|ka|kn|ko|la|lt|lv|mk|ms|mt|nl|no|pl|pt|ro|ru|sk|sl|sq|sr|sv|sw|ta|" \
                                  "te|th|tl|tr|uk|ur|vi|yi|zh".split("|")


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
stopfunc._reload_lang = _load_lang_backend


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
stopfunc._validate = _validate


def __guess(input, stop_func, min_depth, max_depth, encodings, result, found=(), stop=True, show=False,
            scoring_heuristic=False, extended=False, debug=False, timeout=None, max_nodes=None, beam=None):
    """ Perform a breadth-first search using a ranking logic to select and prune the list of codecs.
    
    Each level holds the candidate decodings in the order of the ranking of their parents, then of their own ranking,
     so that the first solution found is the same as with a depth-first search with iterative deepening, while every
     node is only decoded and ranked once. A same output reached through different chains is only expanded once (the
     first, hence best-ranked, chain), while still being checked against the stop function for every chain. The nodes
     of the next level are not kept with their outputs (only with those of their parents), these being decoded again
     when expanded.
    
    The search can be bounded with a timeout (in seconds), a maximum number of expanded nodes (each expansion tries
     every encoding on a node) and a beam (only the best-ranked children of each node are kept). It returns True when
     it was interrupted by one of these bounds.
    """
    deadline = None if timeout is None else perf_counter() + timeout
    frontier, seen, nodes, w = [("", input, tuple(found))], {hash(b(input))}, 0, len(str(max_depth))
    for depth in range(max_depth):
        e, next_frontier = encodings.get(depth, encodings.get(-1, [])), []
        for prev_input, inp, path in frontier:
            # the nodes of a level only hold a reference to the output of their parent, their own output being decoded
            #  again when they are expanded ; this keeps the memory bounded by the number of nodes, not by the size of
            #  their outputs (a level can hold millions of them)
            if inp is None:
                try:
                    inp = CODECS_CACHE[path[-1]].decode(prev_input)[0]
                except Exception:
                    continue
            if deadline is not None and perf_counter() >= deadline or max_nodes is not None and nodes >= max_nodes:
                if debug:
                    print("[!] Search bound reached")
                return True
            nodes += 1
            try:
                children = list(__rank(prev_input, inp, path[-1] if path else "", e, scoring_heuristic, extended,
                                       deadline=deadline))
            except _SearchBound:
                if debug:
                    print("[!] Search bound reached")
                return True
            for i, (new_input, encoding) in enumerate(children):
                if beam is not None and i >= beam:
                    break
                if debug:
                    print(f"[*] Depth {depth+1:0{w}}/{max_depth}: {encoding}")
                p = path + (encoding, )
                if depth >= min_depth and stop_func(new_input):
                    if not stop and (show or debug) and p not in result:
                        s = repr(new_input)
                        s = s[2:-1] if s.startswith("b'") and s.endswith("'") else s
                        s = f"[+] {', '.join(p)}: {s}"
                        print(s if len(s) <= 80 else f"{s[:77]}...")
                    result[p] = new_input
                    if stop:
                        return False
                # the last level is only checked against the stop function, not kept for further decoding
                if depth + 1 < max_depth and (h := hash(b(new_input))) not in seen:
                    seen.add(h)
                    next_frontier.append((inp, None, p))
        if len(frontier := next_frontier) == 0:
            break
    return False


def __guess_list(encoding):
    """ Get the list of encoding names to be tried when guessing for the given encoding, cached per state of the
         registry. """
    try:
        return __guess_lists[encoding]
    except KeyError:
        try:
            l = lookup(encoding, False).parameters['guess']
        except Exception:
            l = []
        __guess_lists[encoding] = l
        return l


def __make_encodings_dict(include, exclude):
    """ Process encodings inclusion and exclusion lists, listing categories and developping codecs' lists of possible
         encoding names. It also creates a cache with the CodecInfo objects for improving performance. """
    def _develop(d, keep=True):
        d, names = d or {}, None
        for k, v in d.items():
            v = _categories(v)
            l, cc, sc = [], [e for e in v if e in CODECS_CATEGORIES], [e for e in v if e not in CODECS_CATEGORIES]
            cn = list_encodings(*cc) if (len(cc) > 0 or keep) and len(sc) == 0 else []
            if len(sc) > 0 and names is None:
                names = set(list_encodings())
            # list from in-scope categories and then everything that is not a category
            for enc in cn + sc:
                g = []
                for e in (search(enc, False) or [enc]):
                    g.extend(__guess_list(e))
                # an encoding name selects only itself, while a codec name selects all its encodings, even when it is
                #  one of them (e.g. "base45" => ["base45", "base45-inv"])
                if enc in g and enc not in cn and enc not in names:
                    l.append(enc)  # e.g. "rot-1" => ["rot-1", "rot-2", ...] ; only "rot-1" is to be selected
                else:              # e.g. "rot"   => ["rot-1", "rot-2", ...] ; all the "rot-N" shall be selected
                    l.extend(g)
            d[k] = list(set(l))
        return d
    _excl, _incl = _develop(exclude, False), _develop(include)
    return {k: [x for x in v if x not in _excl.get(k, [])] for k, v in _incl.items()}


class _SearchBound(Exception):
    """ Raised when the deadline of the search is reached while ranking the encodings of a candidate. """


def __rank(prev_input, input, prev_encoding, encodings, heuristic=False, extended=False, yield_score=False,
           deadline=None):
    """ Filter valid encodings and rank them by relevance. """
    # characteristics of the input text, computed once per padding character (see __score)
    ranking, texts = {}, {}
    for e in encodings:
        # trying every encoding on a candidate can take long, hence the deadline is also checked here (a single
        #  decoding cannot be interrupted though)
        if deadline is not None and perf_counter() >= deadline:
            raise _SearchBound
        try:
            codec = CODECS_CACHE[e]
        except KeyError:
            try:
                CODECS_CACHE[e] = codec = lookup(e, False)
            except LookupError:
                continue
        t = __score(prev_input, input, prev_encoding, e, codec, heuristic, extended, texts)
        if t:
            ranking[e] = t
    for encoding, result in sorted(ranking.items(), key=lambda x: (-x[1][0], x[0])):
        yield result if yield_score else result[1], encoding


class _Text(object):
    __slots__ = ["entropy", "lcharset", "len", "len_raw", "padding", "printables", "text", "textness"]
    
    def __init__(self, text, pad_char=None):
        text = ensure_str(text)
        # length of the encoded data as written, with its padding but without line breaks or spaces (e.g. for checking
        #  whether it is made of whole quanta, as for base64)
        self.len_raw = len(re.sub(r"\s", "", text))
        self.padding = pad_char is not None and text[-1] == pad_char
        # the characteristics below describe the encoded data, hence without its padding
        self.text = (text.rstrip(pad_char) or text) if self.padding else text
        self.len = len(self.text)
        self.lcharset = len(set(self.text))
        self.printables = float(sum(map(PRINTABLES.__contains__, self.text))) / self.len
        self.entropy = entropy(self.text)
        self.textness = _textness(self.text)


def __score(prev_input, input, prev_encoding, encoding, codec, heuristic=False, extended=False, texts=None):
    """ Score relevant encodings given an input. """
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
    # compute input's characteristics only once per padding character and only if the control flow reaches this point
    pad, texts = sc.get('padding_char'), {} if texts is None else texts
    try:
        obj = texts[pad]
    except KeyError:
        obj = texts[pad] = _Text(input, pad)
    if heuristic:
        # from here, the goal (e.g. if the input is Base32) is to rank candidate encodings (e.g. multiple base
        #  codecs) so that we can put the right one as early as possible and eventually exclude bad candidates
        s = -sc.get('penalty', .0)
        # first, apply a bonus if the length of input text's charset is exactly the same as encoding's charset ;
        #  on the contrary, if the length of input text's charset is strictly greater, give a penalty
        lcs = sc.get('len_charset', 256)
        if isinstance(lcs, type(lambda: None)):
            lcs = int(lcs(encoding))
        # NB: the padding character is not counted in the input text's charset (see _Text)
        if lcs >= obj.lcharset:
            s += max(.0, round(.6 * (.99 ** (lcs - obj.lcharset)), 5) - .1)
        else:
            s -= .2  # this can occur for encodings with no_error set to True
        # then, check that the input text is made of whole quanta when the encoding uses them, giving a bonus when
        #  it is the case, and a penalty when it is not while being padded (unpadded data is tolerated by the decoders)
        lm = sc.get('len_multiple')
        if lm:
            if obj.len_raw % lm == 0:
                s += .1
            elif obj.padding:
                s -= .3
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
        # eventually, give a bonus when the output looks like a text, and more than the input, as the characteristics
        #  above only describe the input ; this favours the right decoding over transformations that never fail (e.g.
        #  keyboard shifts), while not penalising intermediate decodings (e.g. into compressed data) nor favouring
        #  wrong decodings that only look a bit more like a text (e.g. in a chain of encodings) ; transitive codecs
        #  (substitutions of characters, e.g. rot or xor) also get a penalty when their output looks less like a text
        # NB: the output of a transitive codec is only rated as a text from Latin letters, as a substitution of
        #     characters of another script cannot be distinguished from a text without the knowledge of its language
        t = _textness(new_input, not transitive)
        s += TEXTNESS_WEIGHT * (max(0., t - max(obj.textness, TEXTNESS_THRESHOLD)) +
                                (min(0., t - obj.textness) if transitive else 0.))
    else:
        s = 1.
    # exclude negative (and eventually null) scores as they are (hopefully) not relevant
    if extended and s >= .0 or not extended and s > .0:
        return s, new_input


def guess(input, stop_func=stopfunc.default, min_depth=0, max_depth=5, include=None, exclude=None, found=(),
          stop=True, show=False, scoring_heuristic=True, extended=False, debug=False, timeout=None, max_nodes=None,
          beam=None):
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
    :param timeout:           maximum duration of the search in seconds (nothing means no limit)
    :param max_nodes:         maximum number of expanded nodes, each expansion trying every encoding on a candidate
                               (nothing means no limit)
    :param beam:              number of best-ranked decodings kept per candidate for the next depth (nothing means all)
    
    When a bound (timeout, max_nodes) is reached, the search stops and returns the solutions found so far.
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
    for n, v in zip(["timeout", "max_nodes", "beam"], [timeout, max_nodes, beam]):
        if v is not None and v <= 0:
            raise ValueError(f"{n} must be a positive number")
    try:
        __guess(input, stop_func, min_depth, max_depth, encodings, result, found, stop, show, scoring_heuristic,
                extended, debug, timeout, max_nodes, beam)
    except KeyboardInterrupt:
        pass
    CODECS_CACHE.clear()
    return result
codecs.guess = guess


def rank(input, extended=False, limit=-1, include=None, exclude=None):
    """ Rank the most probable encodings based on the given input.
    
    :param input:    input text to be evaluated
    :param extended: whether to consider null scores too (NB: negative scores are not output !)
    :param limit:    number of encodings to be returned (-1 means all of them)
    :param include:  inclusion item OR list with category, codec or encoding names (nothing means include every
                      encoding)
    :param exclude:  exclusion item OR list with category, codec or encoding names (nothing means exclude no encoding)
    """
    # a single item (category, codec or encoding name) means a list with this item, as for guess
    include, exclude = [[x] if isinstance(x, str) else x for x in (include, exclude)]
    encodings = __make_encodings_dict(include if isinstance(include, dict) else {-1: include or CODECS_CATEGORIES},
                                      exclude if isinstance(exclude, dict) else {-1: exclude or []})
    r = list(__rank(None, input, "", encodings[-1], True, extended, True))
    CODECS_CACHE.clear()
    return r if limit < 0 else r[:limit]
codecs.rank = rank

