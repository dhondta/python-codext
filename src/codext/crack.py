# -*- coding: UTF-8 -*-
"""Crack feature - recover the key of a keyed cipher from its ciphertext only.

The guess feature cannot follow a keyed cipher whose key is not one of the few tried by default (e.g. "vigenere-key").
 This feature recovers likely keys of a given cipher by cryptanalysis, as FeatherDuster does
 (https://github.com/nccgroup/featherduster), then decodes the input with each of them and ranks the outputs by how much
 they look like a natural language text:

- polyalphabetic substitutions (vigenere, beaufort, gronsfeld): for each key length, each key letter is the shift of
   the corresponding letters (taken every key length letters) that distributes them the most as in a text
- repeating-key XOR (vernam): the most likely key sizes are the ones whose successive blocks are the closest in terms of
   Hamming distance, then each key byte is the one that makes the corresponding characters look the most as a text
- columnar transposition (columnar): all the orders of the columns are tried (brute force) up to a number of columns,
   keeping the outputs whose letters form the most common trigrams
- any other codec: the encodings it lists for the guess feature (e.g. "railfence-1" to "railfence-10") are tried

These statistical attacks need enough ciphertext, e.g. a few tens of letters per key letter for a polyalphabetic
 substitution. It only depends on the registry and ``text`` (it is not used by the guess feature).
"""
import heapq
from collections import Counter
from itertools import permutations
from string import printable
from time import perf_counter

from .__common__ import *
from .text import LETTER_FREQUENCIES, _letter_frequency, _textness


__all__ = ["crack"]

CRACKERS = {}
# characters of the keys of the columnar transposition, in their order (digits only up to 9 columns, e.g. "23541")
COLUMNAR_KEY = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# most common trigrams of English texts (letters only, ignoring spaces and punctuation, hence also across words), by
#  level L of frequency (about 10^(-L/2)), computed on the English documentation and licenses of a Linux system ; the
#  other trigrams are rarer than 10^-4
TRIGRAMS = {
    4: "ion the",
    5: "and are ate ati but cen clu com con cop cpp deb eco ect ens ent ers eso ess est eth fil for fth ght her his "
       "ibs ice igh ile inc ing int ist ith les lib lic lud mpl ncl nse oft ons ont opy pli ppl pro pyr ran rig sin "
       "sio sof str ter tes thi tho tio tri twa ude ver war yri",
    6: "abi abl ack act age ail ain ali all alp ame amp ans ant any app ari arr art ary asi ass ata atf ath aut bco "
       "bel bia bil ble bli boo can cat cco ces cha cla cli cod cor cti dat dby ded der det dif din dis dit doc dth "
       "dto dul ean ear eas ebi ebo eci eda edb ede edi edo edt edw eex efo ein eis eli ema eme enc ene eof eor epr "
       "equ era erc ere eri erm ert erv esa esc ese eta ete eto etr eus eve exa exp ext fre fro ftw gen gin gpl gra "
       "han har hat hea hec hed hef hel hes het hou hpp hth htt ial ian ibu ica icl ide ied ies ifi ili ime imi imp "
       "ina ind ine ins ire isc isi isl isp iss ite iti its ity ive lar lat lco lfi lie lin lis lit llo low mai man "
       "mat men mer met mis mit mod nal nan nce nco nda nde ndi ndo ndt ner nin nof nor not nso nst nta nte nth nti "
       "ntr nts ode odi odu oll ome omm omp ona ond one onf oni ono oos ope ora ore org ori ork orm oro orp ors ort "
       "ose ost oth oti oun our out ove ovi pac par pat pec per pla ple por pos pre pti pub ral rap rat rce rco rea "
       "rec red ree ref rel ren rep res ret rib rin rit rma rmi rms rom rot rov rpo rra rse rsi rth rti san sco sde "
       "sea sec sed see sel seo ser ses set sha sli sma son sor sou spe spr src sre sse ssi sso sta stc ste sth sti "
       "sto sts tab tai tal tan tat tco ted tem ten tex tha tht tic tin tli tno tof tor tot tps tra tre tst tte tth "
       "ttp tyo ubl udi ule ume und urc use ute uti uto ven vid web win wit wor yof you ype yth",
    7: "abe abo acc ace ach aco ada add ade adi aim ake ala alc ald ale alg alo als alt ama ami ana anb anc ane ang "
       "ani ann ano anu apa aph api apt ara arc ard arg ark arp ars asa ase ash asp ast atc ato att atu aty aus ava "
       "ave bab bas bef ber beu bin bje bov bra bsa bsc bsd bsf bsg bsh bsl bsm bsp bss bst bui bus byt cal cas cce "
       "cea cec cei ceo cep cet cew che chi cia cif cis cka cke cma col cov cpl cre cri cte cto cts ctt cul cum cur "
       "dam dan dap dar das dco ddi dea dec def dei del dem den deo des dev dex dfi dfr dic dir dli dma dmo dom don "
       "dor dow dpa dre dso duc dun dve dwa dwi eab eac ead eal eam eap eat eau ebc ebs ebu eby eca ece ech ecp ecu "
       "edf edh edm edp eds edu eed een ees eet efa efe efi efr efu ega ege egi egl egn egp ehp eht eim eit ela ele "
       "elg ell elo elp emo emp ems ena end eng eni eno eom epa epe epl epo ept epu erd erf erg erh erl ern ero erp "
       "err erw esb esd esg esh esi esl esn esp esr esu esw eti ets ett etw eun evi ewe ewi ewo exc exe eyo fac fan "
       "fco fer ffe fic fie fig fin fit fli fme fol fon fou fsu ful fun fus fyo gbu gco gem geo ger ges get gis git "
       "gli gma gnu gor gre gst gth gwi hal has hav hco hee heg hei hem hen heo hep heu hew hic hin hol hom hon hor "
       "how hre hso hsr hta htc hte htm htn hts hub iab iat ibi ibr ich ici ico ict icu ien ify igi ign ila ilc ild "
       "ill ils ilt ima inf ini ink inn inp inu ipt iri isa isd ise isf ish isn isw ita itn itt itu itw iva jec jso "
       "kag ker kin kit kli lab lai lan las lau lbe lcp lda lde lea lec led lef lei lel lem len ler let lex lgo lgp "
       "lia lig lim lla llb llc lle lli llt lly loc log lon lor los lpu lso lsp lte lth lti lug mac mag mak map mar "
       "may mbe mco mea med mes mic min mjs mli mme mmo mon mor mpa mpi mpo msa mso mst mth mul mus nac nam nar nat "
       "nbe nbu nca ncp nct ndc ndl ndr nds nec ned nei nel nen nes net nfi nfo nfr nga ngb ngc ngd nge ngf ngi ngl "
       "ngo ngs ngt ngw nic nis nit nli nma nne nno nod noe non npm npr nre nsa nsc nsi nsp nsu nsy ntc nto ntt nty "
       "nug nul num nus nve nwi nyl nyo nyp nyw oad obj oca oce ock oco ocu oen oev ofa ofc off ofi ofm ofs ogr oin "
       "old olo ols oma omi oml omo omt onc ong onh onl onm onn onp onv onw ool opi opr opt orb orc ord orf orh orl "
       "orr orw ory oss ota ote otl oto ouc oul oum ous owe owi own ows pan pco pen pet pie pil pir plf plo plu pon "
       "ppc ppe ppo pps pri psg pso psr pte pur put pyo pyt que qui rac ram rar rca rcc rch rcp rde rdi rdp reb reg "
       "rei rem reo req rer rew rfo rge rgl rhp ria ric rie rim rip ris riv rks rli rmo rne roc rod rof rog ron rop "
       "ror rou rpr rpu rre rsa rsh rso rst rte rto rty run rus rve rvi rwi ryf ryi ryo sac sal sam sar sas sau sba "
       "sbe sca sch scl scp scr sdi sdo seb sef seg sei sem sen sep seq sev sex sfi sfo sfr sfu sge sgi she sho shp "
       "sht sib sim sis sit slo smp sno soc spa spi spl spo spu srs ssa ssf ssp ssr sst ssu stb std stf stg stl stm "
       "stp stt sty sub suc sun sup svg swi syn syo sys tac tap tar tas tbe tch tcp tde tdo tea tec teg tei tel tet "
       "tfi tfo thm thp thr ths thu tia tie til tim tis tit tiv tma tml tne toa toc tod tom ton too top tou tpr tro "
       "tru try tsa tsc tse tsh tsi tso tsp tsu tto tun tur tut twi two tya typ tyw ual ubc ubs uca uch uct uen uge "
       "ugi uil uir ula uld ult uma unc uni unt upp ups ure urp usi usr ust uta uth utn utw val vec ved vel vic vis "
       "whe whi wil wis wri www xam xce xpa xpr xte xto yan yco ydi yfo yin yor yst yto ywa",
    8: "aba adv agi agr ags ait alf alm alu amc ams ank anp anr aor arb arl asb asc asm aso ats aud aul avi ayb ayn "
       "ayo bac bal bar bea bec bed bee bei ben bit bki bkl bor bse bsi bsr bta bug bun bya byg cab car cau ced cef "
       "ceh cem cer chc chd chm cho chp chr cht cid cin cir cit cks cle cmo cou cpa cro csr css cta cth ctl ctr ctu "
       "cut dac dal dav dbi dbu dcl dcp dde ddo dep dfo dge dha dhp dia dio div dle dno doe dof dot dpr dri dro dsp "
       "dst dte dus dvi dwo eba ebe ebk eck ecl edc edd edr edv eem eer eev ego egr eho eif eiv eja elc els ely emb "
       "emi emu enp enu eon eop erb eru ery esf esm esv esy etc etu ety eva ewa ewh ewx exi fai fau ffi flo fra fri "
       "fte fyi gac gal gan gar gat gba gcc gdi gdo ged gei gex gfr gle gne gno goo gsh gso gte gtk gto gui heh hli "
       "hma hoe hop hos hro htb htf hti htj hto ibe ibl ibt icc icd ick ics ida iel ier iew ifa iff ift ige igt ike "
       "inb inl ino inv inw ior ipp ipr itl ito ivi iza ize jam jav kar kel ken kes ket key kno lac law lay lbu ldi "
       "ldm lds lee leg lev liz lln llr lls lma lno loa lob lop lpl lpr lre lri lsc lse lst ltd lto lue lus lve lwi "
       "lya lyt mad mal mas mec mem meo mfi mma mmu mot mou mov mpu msw nab nad nap nas nch nci ndb ndd ndf ndm ndn "
       "ndp ndu nee neg new nex ngm ngn ngp ngr ngu nif nix nly nob nom now npa npe nsf nsh nsm nss ntl ntm ntp nua "
       "nyc nyd nye nyk nyt oan obe obt oci ocp ocs odo oes ofl ofo ofu ogi oid oje ola ole oli omb onb onr ook orn "
       "oru osi oso otb ots oua oup owh pag pas pea pes phi pho phs pin pll plt ply pmj pol ppr ppt pst psw pta pto "
       "ptr pym qbk qua rad rag rai ras ray rba rbu rci reh rev rex rey rfa rfi rgb rgp rio rka rki rko rme rna rni "
       "rno rob roi roj rol ros rpe rri rro rru rsb rsc rsu rta rtp rtr rts ryn ryt sab sag sap sat sbu sda sdc sew "
       "sey sgr shi sic sid sig siv sla slf sme smo smu sol som ssc ssl stn stq stu sul sur swa swe swh sww tag tao "
       "tax tbo tca tcl tda tdi tep tev tfr tfu tge tif tip tle tly tme tmo tmp tob toe tog toi tos tow tpa tpe tpu "
       "tsd tsm tsr tss tsw tti ttr tup tus twe txt tyf tyl tyt ubj uce ues uff uli ull upl ura uri urn uro urr usa "
       "ush utl utm utp uts utt vai var vat ves vet vie was way wev who wid xcl xer yal ybe yex yfi ygr yit yki yla "
       "yle yli yma yme ymo ync yno ynp ynt ypu yre yte ywh ywi zat",
}
TRIGRAMS = {g: -level / 2 for level, s in TRIGRAMS.items() for g in s.split()}
# mean log10 frequency of the trigrams of an English text and of random letters (the floor being the one of a rare one)
TRIGRAM_TEXT, TRIGRAM_RANDOM, TRIGRAM_FLOOR = -3.8, -5.3, -5.5
# score of a character as part of a text (letters by their frequency, a space as a frequent letter), for the XOR solver
_TEXT_SCORE = [0.] * 256
for _i in range(256):
    _c = chr(_i)
    if _c.isalpha() and _c.isascii():
        _TEXT_SCORE[_i] = LETTER_FREQUENCIES[ord(_c.lower()) - 97]
    elif _c == " ":
        _TEXT_SCORE[_i] = 13.
    elif _c in ".,;:!?'\"-()\n0123456789":
        _TEXT_SCORE[_i] = 1.
    elif _c in printable:
        _TEXT_SCORE[_i] = -2.
    else:
        _TEXT_SCORE[_i] = -10.


def _trigrams(letters):
    """ Mean log10 frequency of the trigrams of the given lowercase letters (in English texts). """
    if (n := len(letters) - 2) <= 0:
        return TRIGRAM_RANDOM
    return sum(TRIGRAMS.get(letters[i:i+3], TRIGRAM_FLOOR) for i in range(n)) / n


def _trigram_rate(text):
    """ Rate in [0, 1] how much the trigrams of the letters of the given text are frequent in English texts (1. for a
         text, 0. for random letters) ; unlike the textness, this does not rely on spaces, hence it distinguishes a text
         without spaces from a rearrangement of its letters (e.g. "ourfriendgoodoldsampletext"). """
    letters = "".join(c for c in ensure_str(text).lower() if "a" <= c <= "z")
    return min(1., max(0., (_trigrams(letters) - TRIGRAM_RANDOM) / (TRIGRAM_TEXT - TRIGRAM_RANDOM)))


def _cracker(*names):
    """ Register a function yielding the likely encodings (with their keys) of the given ciphers for a ciphertext. """
    def _wrapper(f):
        for n in names:
            CRACKERS[n] = f
        return f
    return _wrapper


def _period(key):
    """ Reduce a key to its smallest period (e.g. "rainbowrainbow" to "rainbow"), as a multiple of the key length
         gives the same key repeated. """
    for k in range(1, len(key)):
        if len(key) % k == 0 and key[:k] * (len(key) // k) == key:
            return key[:k]
    return key


@_cracker("beaufort", "gronsfeld", "vigenere")
def _polyalphabetic(cipher, text, max_key_length=None, deadline=None):
    """ For each key length, take each key letter as the shift that distributes the corresponding letters the most as
         in a text (the classic attack of the Vigenere cipher, by frequency analysis of each column). """
    letters = [ord(c) - 97 for c in ensure_str(text).lower() if "a" <= c <= "z"]
    # a Beaufort letter is the key letter minus the plaintext letter, unlike a Vigenere letter (the plaintext letter
    #  plus the key letter) ; a Gronsfeld key is made of digits, that is, of shifts from 0 to 9
    plain = (lambda c, s: (s - c) % 26) if cipher == "beaufort" else (lambda c, s: (c - s) % 26)
    shifts = range(10) if cipher == "gronsfeld" else range(26)
    decode = lambda key: "".join(chr(97 + plain(c, key[i % len(key)])) for i, c in enumerate(letters))
    keys = []
    for k in range(1, min(max_key_length or 20, max(1, len(letters) // 2)) + 1):
        key = []
        for i in range(k):
            counts = Counter(letters[i::k])
            key.append(max(shifts, key=lambda s: sum(n * LETTER_FREQUENCIES[plain(c, s)] for c, n in counts.items())))
        if (key := _period(key)) not in keys:
            keys.append(key)
        if deadline and perf_counter() > deadline:
            break
    # the frequency analysis of a column can miss its shift when the column holds few letters (e.g. "rpinbow" instead of
    #  "rainbow"), hence the best keys are refined letter by letter with the trigrams of the whole output
    keys.sort(key=lambda key: -_trigrams(decode(key)))
    for key in keys[:3]:
        best, improved = _trigrams(decode(key)), True
        while improved and not (deadline and perf_counter() > deadline):
            improved = False
            for i in range(len(key)):
                for s in shifts:
                    if s != key[i] and (score := _trigrams(decode(key[:i] + [s] + key[i+1:]))) > best:
                        best, key[i], improved = score, s, True
    for key in keys:
        yield f"{cipher}-" + "".join(str(s) if cipher == "gronsfeld" else chr(97 + s) for s in key)


@_cracker("vernam")
def _repeating_xor(cipher, text, max_key_length=None, deadline=None, n_sizes=6):
    """ Take the key sizes whose successive blocks are the closest (normalized Hamming distance), then, for each of
         them, each key byte as the one that makes the corresponding characters look the most as a text. """
    values = [ord(c) for c in ensure_str(text)]
    sample, sizes = values[:4096], []
    for k in range(1, min(max_key_length or 32, max(1, len(values) // 2)) + 1):
        blocks = [sample[i:i+k] for i in range(0, len(sample) - k + 1, k)]
        if len(blocks) < 2:
            break
        d = sum(bin(x ^ y).count("1") for b1, b2 in zip(blocks, blocks[1:]) for x, y in zip(b1, b2))
        sizes.append((d / (k * (len(blocks) - 1)), k))
    keys = []
    for _, k in sorted(sizes)[:n_sizes]:
        key = []
        for i in range(k):
            counts = Counter(values[i::k])
            # the key characters cannot be a newline, as the codec name could not hold it
            key.append(max((x for x in range(1, 256) if x != 10), key=lambda x: sum(
                n * (_TEXT_SCORE[c ^ x] if c ^ x < 256 else 0.) for c, n in counts.items())))
        if (key := _period(key)) not in keys:
            keys.append(key)
        if deadline and perf_counter() > deadline:
            break
    for key in keys:
        yield f"{cipher}-" + "".join(map(chr, key))


@_cracker("columnar")
def _columnar(cipher, text, max_key_length=None, deadline=None, n_best=50):
    """ Try all the orders of the columns, up to the given number of columns (7 by default, i.e. 5913 orders), keeping
         the orders whose outputs hold the most common bigrams. """
    text = ensure_str(text)
    l, lower, best = len(text), text.lower(), []
    for n in range(2, min(max_key_length or 7, l, len(COLUMNAR_KEY)) + 1):
        # only the first rows are rated (about 400 characters), as they suffice to tell the right order
        lengths, rows = [l // n + (j < l % n) for j in range(n)], max(1, min(l // n + 1, 400 // n))
        for c, order in enumerate(permutations(range(n))):
            # cut the ciphertext into columns, read in the given order
            cols, i = [None] * n, 0
            for j in order:
                cols[j], i = lower[i:i+lengths[j]], i + lengths[j]
            out = "".join(x for r in range(rows) for j in range(n)
                          if r < lengths[j] and "a" <= (x := cols[j][r]) <= "z")
            score = _trigrams(out)
            item = (score, n, order)
            if len(best) < n_best:
                heapq.heappush(best, item)
            elif item > best[0]:
                heapq.heapreplace(best, item)
            if c % 256 == 255 and deadline and perf_counter() > deadline:
                break
        if deadline and perf_counter() > deadline:
            break
    for _, n, order in sorted(best, reverse=True):
        # the column read in r-th position gets the r-th character of the key
        key = [""] * n
        for r, j in enumerate(order):
            key[j] = COLUMNAR_KEY[r]
        yield f"{cipher}-" + "".join(key)


def _score(text):
    """ Rate in [0, 1] how much an output looks like a text: the mean of its textness and of the rate of its trigrams,
         or only the latter for a text without spaces (as the textness relies on its words), weighted by the fit of its
         letter frequencies (distinguishing the substitutions that are not shifts of its letters). """
    text = ensure_str(text)
    score = _trigram_rate(text)
    if any(c.isspace() for c in text.strip()):
        score = (score + _textness(text)) / 2
    # a text starts with a capital letter rather than with the end of a word (e.g. "t was a bright cold day... him.I",
    #  from a rotation of the columns of a transposition)
    letters = [c for c in text if c.isalpha()]
    if letters and letters[0].islower() and any(c.isupper() for c in letters):
        score *= .97
    return score * _letter_frequency(text)


def _codec_name(cipher):
    """ Get the name of the codec of the given cipher (e.g. "vigenere" for "vigenere-cipher" or "vigenère"). """
    try:
        ci = lookup(cipher, False)
    except LookupError:
        raise LookupError(f"Unknown cipher '{cipher}'")
    return ci.parameters.get('name', ci.name), ci


def crack(text, cipher, limit=10, max_key_length=None, timeout=None):
    """ Recover the most likely keys of the given cipher for the given ciphertext.

    :param text:           ciphertext (str or bytes)
    :param cipher:         name of the cipher (e.g. "vigenere", "vernam" or "columnar"), or of any codec whose encodings
                            listed for the guess feature are tried (e.g. "railfence" or "rot")
    :param limit:          maximum number of results (all of them if None or negative)
    :param max_key_length: maximum length of the key (20 letters for a polyalphabetic substitution, 32 characters for
                            repeating-key XOR and 7 columns for a columnar transposition by default)
    :param timeout:        maximum duration of the key search (in seconds), then using the keys found so far
    :return:               list of (score, encoding, output) tuples, sorted by decreasing score (how much the output
                            looks like a text, from 0 to 1)
    """
    name, ci = _codec_name(cipher)
    deadline = None if timeout is None else perf_counter() + timeout
    if name in CRACKERS:
        encodings = CRACKERS[name](name, text, max_key_length, deadline)
    elif len(guesses := ci.parameters.get('guess') or []) > 0:
        encodings = iter(guesses)
    else:
        raise ValueError(f"Cannot crack '{cipher}': no key recovery for it (supported: {', '.join(sorted(CRACKERS))}) "
                         "and no encoding to be tried")
    results, outputs = [], set()
    for encoding in encodings:
        try:
            out = decode(text, encoding)
        except Exception:
            continue
        if (key := ensure_str(out)) in outputs:
            continue
        outputs.add(key)
        results.append((_score(out), encoding, out))
        if deadline and perf_counter() > deadline:
            break
    results.sort(key=lambda x: (-x[0], len(x[1])))
    return results if limit is None or limit < 0 else results[:limit]


def report(results, width=80):
    """ Format the results of crack for the terminal: the score and the encoding, followed by the output (truncated to
         the given width if there are several results). """
    lines = []
    for score, encoding, out in results:
        out = ensure_str(out).replace("\n", "\\n")
        if len(results) > 1 and len(out) > width - 4:
            out = out[:width - 7] + "..."
        lines += [f"[+] {score:.5f}: {encoding}", f"    {out}"]
    return "\n".join(lines) or "Could not crack :-("


codecs.crack = crack
codecs.crack_report = report
