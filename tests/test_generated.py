#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Automatically generated codec tests.

"""
from itertools import chain
from random import randint
from string import printable
from unittest import TestCase

from codext.__common__ import *


def make_test(**params):
    """ Test factory function for auto-creating tests for encodings having __examples__ defined. """
    def _template(self):
        tfile = "test-codec-%s.txt" % params['name']
        icase = params.get('ignore_case')
        icdec = lambda s: s.lower() if icase in ["decode", "both"] else s
        icenc = lambda s: s.lower() if icase in ["encode", "both"] else s
        # first, define if only encode is used ; if so, decoding must occur right after encode tests, otherwise just
        #  execute the defined decode tests
        dec = True
        for k in params['examples'].keys():
            if k.startswith("dec"):
                dec = False
        # now execute tests relying on the given examples
        for k, examples in params['examples'].items():
            # multiple encoding names can be given, e.g. 'enc(morse|morse-AB|...)'
            m = re.match(r"(?:dec|enc|enc-dec)\((.*?)(?:\|(.*?))*\)(\*)?", k)
            if m:
                f1 = getattr(codecs, ["decode", "encode"][k.startswith("enc")])
                f2 = getattr(codecs, ["encode", "decode"][k.startswith("enc")])
                for ename in m.groups():
                    if ename == "*":
                        # ignore mode only
                        continue
                    if ename is None:
                        continue
                    # buggy generated encoding names
                    try:
                        lookup(ename)
                    except LookupError:
                        continue
                    # erroneous encoding name test
                    if examples is None:
                        self.assertRaises(LookupError, f1, "test", ename)
                        continue
                    # unhandled character error tests
                    encmap = params.get('encmap')
                    if encmap and params['intype'] not in ["bin", "ord"] and not params['no_error']:
                        if not isinstance(encmap, list):
                            encmap = [encmap]
                        for em in encmap:
                            if k.startswith("dec"):
                                em = {v: k for k, v in em.items()}
                            # find one handled character and one unhandled
                            c1, c2 = None, None
                            p = list(map(ord, printable))
                            for i in chain(p, set(range(256)) - set(p)):
                                if chr(i) in em.keys():
                                    c1 = chr(i)
                                    break
                            for i in chain(set(range(256)) - set(p), p):
                                if chr(i) not in em.keys():
                                    c2 = chr(i)
                                    break
                            # now check that it raises the right error or not given the selected errors handling
                            if c1 and c2:
                                sep = params['sep'][0] if len(params['sep']) > 0 else ""
                                self.assertRaises(ValueError, f1, c2, ename)
                                self.assertRaises(ValueError, f1, c2, ename, "BAD_ERRORS")
                                if not k.startswith("enc-dec"):
                                    self.assertEqual(f1(c1 + c2, ename, "ignore"), f1(c1, ename))
                                    self.assertEqual(f1(c1 + c2, ename, "leave"), f1(c1, ename) + sep + c2)
                                    self.assertEqual(f1(c1 + c2, ename, "replace"), f1(c1, ename) + sep + \
                                                     params.get('repl_minlen', 1) * params['repl_char'])
                    # examples validation tests
                    incr_f1 = codecs.getincrementalencoder(ename)().encode
                    incr_f2 = codecs.getincrementaldecoder(ename)().decode
                    # - "enc-dec" tests (uses a list of values that shall remain the same after encoding and decoding,
                    #    no matter what the encoded value is
                    if k.startswith("enc-dec") and isinstance(examples, list):
                        for e in examples[:]:
                            rd = re.match(r"\@(i?)random(?:\{(\d+(?:,(\d+))*?)\})?$", e)
                            if rd:
                                examples.remove(e)
                                for n in (rd.group(2) or "512").split(","):
                                    s = "".join(chr(randint(0, 255)) for i in range(int(n)))
                                    examples.append(s.lower() if rd.group(1) else s)
                        for s in [""] + examples:
                            self.assertEqual(icdec(f2(icenc(f1(s, ename)), ename)), icdec(s))
                            self.assertEqual(icdec(f2(icenc(f1(b(s), ename)), ename)), b(icdec(s)))
                            # important note: with respect to the original design,
                            #  IncrementalEncoder(...).encode(...) gives bytes
                            #  IncrementalDecoder(...).encode(...) gives str
                            self.assertEqual(icdec(incr_f2(icenc(incr_f1(s, ename)), ename)), icdec(s))
                            self.assertEqual(icdec(incr_f2(icenc(incr_f1(b(s), ename)), ename)), icdec(s))
                            # file tests
                            with codecs.open(tfile, 'wb', encoding=ename) as f:
                                f.write(b(s))
                            with codecs.open(tfile, 'rb', encoding=ename) as f:
                                s2 = f.read()
                            self.assertEqual(b(icdec(s2)), b(icdec(s)))
                            os.remove(tfile)
                    # - "enc" and "dec" tests (uses a dictionary with the value to be encoded and the expected encoded
                    #    value)
                    else:
                        for s1, s2 in examples.items():
                            # willingly erroneous tests
                            if s2 is None:
                                self.assertRaises((ValueError, NotImplementedError), f1, s1, ename)
                                continue
                            # raw text tests
                            self.assertEqual(icenc(f1(s1, ename)), icenc(s2))
                            self.assertEqual(b(icenc(f1(s1, ename))), b(icenc(s2)))
                            # important note: with respect to the original design,
                            #  IncrementalEncoder(...).encode(...) gives bytes
                            #self.assertEqual(icenc(incr_f1(s1, ename)), b(icenc(s2)))
                            #self.assertEqual(icenc(incr_f1(b(s1), ename)), b(icenc(s2)))
                            self.assertIsNotNone(f1(s1, ename, "replace"))
                            self.assertIsNotNone(f1(s1, ename, "ignore"))
                            if dec:
                                self.assertEqual(icdec(f2(s2, ename)), icdec(s1))
                                self.assertEqual(b(icdec(f2(s2, ename))), b(icdec(s1)))
                                # important note: with respect to the original design,
                                #  IncrementalDecoder(...).encode(...) gives str
                                #self.assertEqual(icdec(incr_f2(s2, ename)), icdec(s1))
                                #self.assertEqual(icdec(incr_f2(b(s2), ename)), icdec(s1))
                                self.assertIsNotNone(f2(s2, ename, "replace"))
                                self.assertIsNotNone(f2(s2, ename, "ignore"))
                            if k.startswith("enc"):
                                # file tests
                                with codecs.open(tfile, 'wb', encoding=ename) as f:
                                    f.write(b(s1))
                                with codecs.open(tfile, 'rb', encoding=ename) as f:
                                    s = f.read()
                                self.assertEqual(b(icdec(f2(s2, ename))), b(icdec(s)))
                                os.remove(tfile)
    return _template


class GeneratedTestCase(TestCase):
    pass


for encoding in list_encodings():
    try:
        ci = lookup(encoding)
    except LookupError:
        continue
    # only consider codecs with __examples__ defined in their globals for dynamic tests generation
    if ci.parameters.get('examples') is not None:
        f = make_test(**ci.parameters)
        f.__name__ = n = "test_" + encoding.replace("-", "_")
        setattr(GeneratedTestCase, n, f)

