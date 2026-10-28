# -*- coding: UTF-8 -*-
"""HTML entity Codec - html entity content encoding.

HTML character references represent characters that are reserved or hard to type in HTML, such as the named entities
 defined by the HTML5 specification (e.g. "&lt;" for "<", "&Tab;" for a tab). This codec replaces the characters having
 a named entity by this entity, and the other characters beyond U+00FF by "&" followed by their hexadecimal code point
 and ";" (e.g. "&1234;", a non-standard form without "#x") ; decoding supports both forms, but not the standard numeric
 references ("&#...;").

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://html.spec.whatwg.org/multipage/named-characters.html
"""
from ..__common__ import *


__examples__ = {
    'enc(html_entities|html-entity)': {'<This\tis\na test>': "&lt;This&Tab;is&NewLine;a test&gt;"},
    'enc(html)':                      {'\u1234': "&1234;"},
    'dec(html|html_entity)':          {'&DoesNotExist;': None},
    'dec(html_entities|html-entity)': {
        '&lt;This&Tab;is&NewLine;a test&gt;': "<This\tis\na test>",
        '&lt;This&Tab;is&NewLine;a&nbsp;test&gt;': "<This\tis\na test>",
    },
}


# source: https://dev.w3.org/html5/html-author/charref
ENCMAP = {
    '\t': "&Tab;", '\n': "&NewLine;", '!': "&excl;", '"': "&quot;", '#': "&num;", '$': "&dollar;", '%': "&percnt;",
    '&': "&amp;", '\'': "&apos;", '(': "&lpar;", ')': "&rpar;", '*': "&ast;", '+': "&plus;", ',': "&comma;",
    '.': "&period;", '/': "&sol;", ':': "&colon;", ';': "&semi;", '<': "&lt;", '=': "&equals;", '>': "&gt;",
    '?': "&quest;", '@': "&commat;", '[': "&lsqb;", '\\': "&bsol;", ']': "&rsqb;", '^': "&Hat;", '_': "&lowbar;",
    '`': "&grave;", '{': "&lcub;", '|': "&verbar;", '}': "&rcub;", '¡': "&iexcl;", '¢': "&cent;",
    '£': "&pound;", '¤': "&curren;", '¥': "&yen;", '¦': "&brvbar;", '§': "&sect;", '¨': "&Dot;", '©': "&copy;",
    'ª': "&ordf;", '«': "&laquo;", '¬': "&not;", '­': "&shy;", '®': "&reg;", '¯': "&macr;", '°': "&deg;",
    '±': "&plusmn;", '²': "&sup2;", '³': "&sup3;", '´': "&acute;", 'µ': "&micro;", '¶': "&para;", '·': "&middot;",
    '¸': "&cedil;", '¹': "&sup1;", 'º': "&ordm;", '»': "&raquo;", '¼': "&frac14;", '½': "&frac12;", '¾': "&frac34;",
    '¿': "&iquest;", 'À': "&Agrave;", 'Á': "&Aacute;", 'Â': "&Acirc;", 'Ã': "&Atilde;", 'Ä': "&Auml;", 'Å': "&Aring;",
    'Æ': "&AElig;", 'Ç': "&Ccedil;", 'È': "&Egrave;", 'É': "&Eacute;", 'Ê': "&Ecirc;", 'Ë': "&Euml;", 'Ì': "&Igrave;",
    'Í': "&Iacute;", 'Î': "&Icirc;", 'Ï': "&Iuml;", 'Ð': "&ETH;", 'Ñ': "&Ntilde;", 'Ò': "&Ograve;", 'Ó': "&Oacute;",
    'Ô': "&Ocirc;", 'Õ': "&Otilde;", 'Ö': "&Ouml;", '×': "&times;", 'Ø': "&Oslash;", 'Ù': "&Ugrave;", 'Ú': "&Uacute;",
    'Û': "&Ucirc;", 'Ü': "&Uuml;", 'Ý': "&Yacute;", 'Þ': "&THORN;", 'ß': "&szlig;", 'à': "&agrave;", 'á': "&aacute;",
    'â': "&acirc;", 'ã': "&atilde;", 'ä': "&auml;", 'å': "&aring;", 'æ': "&aelig;", 'ç': "&ccedil;", 'è': "&egrave;",
    'é': "&eacute;", 'ê': "&ecirc;", 'ë': "&euml;", 'ì': "&igrave;", 'í': "&iacute;", 'î': "&icirc;", 'ï': "&iuml;",
    'ð': "&eth;", 'ñ': "&ntilde;", 'ò': "&ograve;", 'ó': "&oacute;", 'ô': "&ocirc;", 'õ': "&otilde;", 'ö': "&ouml;",
    '÷': "&divide;", 'ø': "&oslash;", 'ù': "&ugrave;", 'ú': "&uacute;", 'û': "&ucirc;", 'ü': "&uuml;", 'ý': "&yacute;",
    'þ': "&thorn;", 'ÿ': "&yuml;", 'Ā': "&Amacr;", 'ā': "&amacr;", 'Ă': "&Abreve;", 'ă': "&abreve;", 'Ą': "&Aogon;",
    'ą': "&aogon;", 'Ć': "&Cacute;", 'ć': "&cacute;", 'Ĉ': "&Ccirc;", 'ĉ': "&ccirc;", 'Ċ': "&Cdot;", 'ċ': "&cdot;",
    'Č': "&Ccaron;", 'č': "&ccaron;", 'Ď': "&Dcaron;", 'ď': "&dcaron;", 'Đ': "&Dstrok;", 'đ': "&dstrok;",
    'Ē': "&Emacr;", 'ē': "&emacr;", 'Ė': "&Edot;", 'ė': "&edot;", 'Ę': "&Eogon;", 'ę': "&eogon;", 'Ě': "&Ecaron;",
    'ě': "&ecaron;", 'Ĝ': "&Gcirc;", 'ĝ': "&gcirc;", 'Ğ': "&Gbreve;", 'ğ': "&gbreve;", 'Ġ': "&Gdot;", 'ġ': "&gdot;",
    'Ģ': "&Gcedil;", 'Ĥ': "&Hcirc;", 'ĥ': "&hcirc;", 'Ħ': "&Hstrok;", 'ħ': "&hstrok;", 'Ĩ': "&Itilde;",
    'ĩ': "&itilde;", 'Ī': "&Imacr;", 'ī': "&imacr;", 'Į': "&Iogon;", 'į': "&iogon;", 'İ': "&Idot;", 'ı': "&imath;",
    'Ĳ': "&IJlig;", 'ĳ': "&ijlig;", 'Ĵ': "&Jcirc;", 'ĵ': "&jcirc;", 'Ķ': "&Kcedil;", 'ķ': "&kcedil;", 'ĸ': "&kgreen;",
    'Ĺ': "&Lacute;", 'ĺ': "&lacute;", 'Ļ': "&Lcedil;", 'ļ': "&lcedil;", 'Ľ': "&Lcaron;", 'ľ': "&lcaron;",
    'Ŀ': "&Lmidot;", 'ŀ': "&lmidot;", 'Ł': "&Lstrok;", 'ł': "&lstrok;", 'Ń': "&Nacute;", 'ń': "&nacute;",
    'Ņ': "&Ncedil;", 'ņ': "&ncedil;", 'Ň': "&Ncaron;", 'ň': "&ncaron;", 'ŉ': "&napos;", 'Ŋ': "&ENG;", 'ŋ': "&eng;",
    'Ō': "&Omacr;", 'ō': "&omacr;", 'Ő': "&Odblac;", 'ő': "&odblac;", 'Œ': "&OElig;", 'œ': "&oelig;", 'Ŕ': "&Racute;",
    'ŕ': "&racute;", 'Ŗ': "&Rcedil;", 'ŗ': "&rcedil;", 'Ř': "&Rcaron;", 'ř': "&rcaron;", 'Ś': "&Sacute;",
    'ś': "&sacute;", 'Ŝ': "&Scirc;", 'ŝ': "&scirc;", 'Ş': "&Scedil;", 'ş': "&scedil;", 'Š': "&Scaron;",
    'š': "&scaron;", 'Ţ': "&Tcedil;", 'ţ': "&tcedil;", 'Ť': "&Tcaron;", 'ť': "&tcaron;", 'Ŧ': "&Tstrok;",
    'ŧ': "&tstrok;", 'Ũ': "&Utilde;", 'ũ': "&utilde;", 'Ū': "&Umacr;", 'ū': "&umacr;", 'Ŭ': "&Ubreve;",
    'ŭ': "&ubreve;", 'Ů': "&Uring;", 'ů': "&uring;", 'Ű': "&Udblac;", 'ű': "&udblac;", 'Ų': "&Uogon;", 'ų': "&uogon;",
    'Ŵ': "&Wcirc;", 'ŵ': "&wcirc;", 'Ŷ': "&Ycirc;", 'ŷ': "&ycirc;", 'Ÿ': "&Yuml;", 'Ź': "&Zacute;", 'ź': "&zacute;",
    'Ż': "&Zdot;", 'ż': "&zdot;", 'Ž': "&Zcaron;", 'ž': "&zcaron;", 'ƒ': "&fnof;", 'Ƶ': "&imped;", 'ǵ': "&gacute;",
    'ȷ': "&jmath;", 'ˆ': "&circ;", 'ˇ': "&caron;", '˘': "&breve;", '˙': "&dot;", '˚': "&ring;", '˛': "&ogon;",
    '˜': "&tilde;", '˝': "&dblac;", '̑': "&DownBreve;", '̲': "&UnderBar;", 'Α': "&Alpha;", 'Β': "&Beta;",
    'Γ': "&Gamma;", 'Δ': "&Delta;", 'Ε': "&Epsilon;", 'Ζ': "&Zeta;", 'Η': "&Eta;", 'Θ': "&Theta;", 'Ι': "&Iota;",
    'Κ': "&Kappa;", 'Λ': "&Lambda;", 'Μ': "&Mu;", 'Ν': "&Nu;", 'Ξ': "&Xi;", 'Ο': "&Omicron;", 'Π': "&Pi;",
    'Ρ': "&Rho;", 'Σ': "&Sigma;", 'Τ': "&Tau;", 'Υ': "&Upsilon;", 'Φ': "&Phi;", 'Χ': "&Chi;", 'Ψ': "&Psi;",
    'Ω': "&Omega;", 'α': "&alpha;", 'β': "&beta;", 'γ': "&gamma;", 'δ': "&delta;", 'ε': "&epsiv;", 'ζ': "&zeta;",
    'η': "&eta;", 'θ': "&theta;", 'ι': "&iota;", 'κ': "&kappa;", 'λ': "&lambda;", 'μ': "&mu;", 'ν': "&nu;",
    'ξ': "&xi;", 'ο': "&omicron;", 'π': "&pi;", 'ρ': "&rho;", 'ς': "&sigmav;", 'σ': "&sigma;", 'τ': "&tau;",
    'υ': "&upsi;", 'φ': "&phi;", 'χ': "&chi;", 'ψ': "&psi;", 'ω': "&omega;", 'ϑ': "&thetav;", 'ϒ': "&Upsi;",
    'ϕ': "&straightphi;", 'ϖ': "&piv;", 'Ϝ': "&Gammad;", 'ϝ': "&gammad;", 'ϰ': "&kappav;", 'ϱ': "&rhov;",
    'ϵ': "&epsi;", '϶': "&bepsi;", 'Ё': "&IOcy;", 'Ђ': "&DJcy;", 'Ѓ': "&GJcy;", 'Є': "&Jukcy;", 'Ѕ': "&DScy;",
    'І': "&Iukcy;", 'Ї': "&YIcy;", 'Ј': "&Jsercy;", 'Љ': "&LJcy;", 'Њ': "&NJcy;", 'Ћ': "&TSHcy;", 'Ќ': "&KJcy;",
    'Ў': "&Ubrcy;", 'Џ': "&DZcy;", 'А': "&Acy;", 'Б': "&Bcy;", 'В': "&Vcy;", 'Г': "&Gcy;", 'Д': "&Dcy;", 'Е': "&IEcy;",
    'Ж': "&ZHcy;", 'З': "&Zcy;", 'И': "&Icy;", 'Й': "&Jcy;", 'К': "&Kcy;", 'Л': "&Lcy;", 'М': "&Mcy;", 'Н': "&Ncy;",
    'О': "&Ocy;", 'П': "&Pcy;", 'Р': "&Rcy;", 'С': "&Scy;", 'Т': "&Tcy;", 'У': "&Ucy;", 'Ф': "&Fcy;", 'Х': "&KHcy;",
    'Ц': "&TScy;", 'Ч': "&CHcy;", 'Ш': "&SHcy;", 'Щ': "&SHCHcy;", 'Ъ': "&HARDcy;", 'Ы': "&Ycy;", 'Ь': "&SOFTcy;",
    'Э': "&Ecy;", 'Ю': "&YUcy;", 'Я': "&YAcy;", 'а': "&acy;", 'б': "&bcy;", 'в': "&vcy;", 'г': "&gcy;", 'д': "&dcy;",
    'е': "&iecy;", 'ж': "&zhcy;", 'з': "&zcy;", 'и': "&icy;", 'й': "&jcy;", 'к': "&kcy;", 'л': "&lcy;", 'м': "&mcy;",
    'н': "&ncy;", 'о': "&ocy;", 'п': "&pcy;", 'р': "&rcy;", 'с': "&scy;", 'т': "&tcy;", 'у': "&ucy;", 'ф': "&fcy;",
    'х': "&khcy;", 'ц': "&tscy;", 'ч': "&chcy;", 'ш': "&shcy;", 'щ': "&shchcy;", 'ъ': "&hardcy;", 'ы': "&ycy;",
    'ь': "&softcy;", 'э': "&ecy;", 'ю': "&yucy;", 'я': "&yacy;", 'ё': "&iocy;", 'ђ': "&djcy;", 'ѓ': "&gjcy;",
    'є': "&jukcy;", 'ѕ': "&dscy;", 'і': "&iukcy;", 'ї': "&yicy;", 'ј': "&jsercy;", 'љ': "&ljcy;", 'њ': "&njcy;",
    'ћ': "&tshcy;", 'ќ': "&kjcy;", 'ў': "&ubrcy;", 'џ': "&dzcy;", '\u2002': "&ensp;", '\u2003': "&emsp;",
    '\u2004': "&emsp13;", '\u2005': "&emsp14;", '\u2007': "&numsp;", '\u2008': "&puncsp;", '\u2009': "&thinsp;",
    '\u200a': "&hairsp;", '​\u200b': "&ZeroWidthSpace;", '\u200c': "&zwnj;", '\u200d': "&zwj;", '\u200e': "&lrm;",
    '\u200f': "&rlm;", '‐': "&hyphen;", '–': "&ndash;", '—': "&mdash;",
    '―': "&horbar;", '‖': "&Verbar;", '‘': "&lsquo;", '’': "&rsquo;", '‚': "&lsquor;", '“': "&ldquo;", '”': "&rdquo;",
    '„': "&ldquor;", '†': "&dagger;", '‡': "&Dagger;", '•': "&bull;", '‥': "&nldr;", '…': "&hellip;", '‰': "&permil;",
    '‱': "&pertenk;", '′': "&prime;", '″': "&Prime;", '‴': "&tprime;", '‵': "&bprime;", '‹': "&lsaquo;",
    '›': "&rsaquo;", '‾': "&oline;", '⁁': "&caret;", '⁃': "&hybull;", '⁄': "&frasl;", '⁏': "&bsemi;", '⁗': "&qprime;",
    '\u205f': "&MediumSpace;", '⁠': "&NoBreak;", '⁡': "&ApplyFunction;", '⁢': "&InvisibleTimes;", '⁣': "&InvisibleComma;",
    '€': "&euro;", '⃛': "&tdot;", '⃜': "&DotDot;", 'ℂ': "&Copf;", '℅': "&incare;", 'ℊ': "&gscr;", 'ℋ': "&hamilt;",
    'ℌ': "&Hfr;", 'ℍ': "&quaternions;", 'ℎ': "&planckh;", 'ℏ': "&planck;", 'ℐ': "&Iscr;", 'ℑ': "&image;",
    'ℒ': "&Lscr;", 'ℓ': "&ell;", 'ℕ': "&Nopf;", '№': "&numero;", '℗': "&copysr;", '℘': "&weierp;", 'ℙ': "&Popf;",
    'ℚ': "&rationals;", 'ℛ': "&Rscr;", 'ℜ': "&real;", 'ℝ': "&reals;", '℞': "&rx;", '™': "&trade;", 'ℤ': "&integers;",
    'Ω': "&ohm;", '℧': "&mho;", 'ℨ': "&Zfr;", '℩': "&iiota;", 'Å': "&angst;", 'ℬ': "&bernou;", 'ℭ': "&Cfr;",
    'ℯ': "&escr;", 'ℰ': "&Escr;", 'ℱ': "&Fscr;", 'ℳ': "&phmmat;", 'ℴ': "&order;", 'ℵ': "&alefsym;", 'ℶ': "&beth;",
    'ℷ': "&gimel;", 'ℸ': "&daleth;", 'ⅅ': "&CapitalDifferentialD;", 'ⅆ': "&DifferentialD;", 'ⅇ': "&ExponentialE;",
    'ⅈ': "&ImaginaryI;", '⅓': "&frac13;", '⅔': "&frac23;", '⅕': "&frac15;", '⅖': "&frac25;", '⅗': "&frac35;",
    '⅘': "&frac45;", '⅙': "&frac16;", '⅚': "&frac56;", '⅛': "&frac18;", '⅜': "&frac38;", '⅝': "&frac58;",
    '⅞': "&frac78;", '←': "&larr;", '↑': "&uarr;", '→': "&rarr;", '↓': "&darr;", '↔': "&harr;", '↕': "&varr;",
    '↖': "&nwarr;", '↗': "&nearr;", '↘': "&searr;", '↙': "&swarr;", '↚': "&nlarr;", '↛': "&nrarr;", '↝': "&rarrw;",
    '↞': "&Larr;", '↟': "&Uarr;", '↠': "&Rarr;", '↡': "&Darr;", '↢': "&larrtl;", '↣': "&rarrtl;",
    '↤': "&LeftTeeArrow;", '↥': "&UpTeeArrow;", '↦': "&map;", '↧': "&DownTeeArrow;", '↩': "&larrhk;", '↪': "&rarrhk;",
    '↫': "&larrlp;", '↬': "&rarrlp;", '↭': "&harrw;", '↮': "&nharr;", '↰': "&lsh;", '↱': "&rsh;", '↲': "&ldsh;",
    '↳': "&rdsh;", '↵': "&crarr;", '↶': "&cularr;", '↷': "&curarr;", '↺': "&olarr;", '↻': "&orarr;", '↼': "&lharu;",
    '↽': "&lhard;", '↾': "&uharr;", '↿': "&uharl;", '⇀': "&rharu;", '⇁': "&rhard;", '⇂': "&dharr;", '⇃': "&dharl;",
    '⇄': "&rlarr;", '⇅': "&udarr;", '⇆': "&lrarr;", '⇇': "&llarr;", '⇈': "&uuarr;", '⇉': "&rrarr;", '⇊': "&ddarr;",
    '⇋': "&lrhar;", '⇌': "&rlhar;", '⇍': "&nlArr;", '⇎': "&nhArr;", '⇏': "&nrArr;", '⇐': "&lArr;", '⇑': "&uArr;",
    '⇒': "&rArr;", '⇓': "&dArr;", '⇔': "&hArr;", '⇕': "&vArr;", '⇖': "&nwArr;", '⇗': "&neArr;", '⇘': "&seArr;",
    '⇙': "&swArr;", '⇚': "&lAarr;", '⇛': "&rAarr;", '⇝': "&zigrarr;", '⇤': "&larrb;", '⇥': "&rarrb;", '⇵': "&duarr;",
    '⇽': "&loarr;", '⇾': "&roarr;", '⇿': "&hoarr;", '∀': "&forall;", '∁': "&comp;", '∂': "&part;", '∃': "&exist;",
    '∄': "&nexist;", '∅': "&empty;", '∇': "&nabla;", '∈': "&isin;", '∉': "&notin;", '∋': "&niv;", '∌': "&notni;",
    '∏': "&prod;", '∐': "&coprod;", '∑': "&sum;", '−': "&minus;", '∓': "&mnplus;", '∔': "&plusdo;", '∖': "&setmn;",
    '∗': "&lowast;", '∘': "&compfn;", '√': "&radic;", '∝': "&prop;", '∞': "&infin;", '∟': "&angrt;", '∠': "&ang;",
    '∡': "&angmsd;", '∢': "&angsph;", '∣': "&mid;", '∤': "&nmid;", '∥': "&par;", '∦': "&npar;", '∧': "&and;",
    '∨': "&or;", '∩': "&cap;", '∪': "&cup;", '∫': "&int;", '∬': "&Int;", '∭': "&tint;", '∮': "&conint;",
    '∯': "&Conint;", '∰': "&Cconint;", '∱': "&cwint;", '∲': "&cwconint;", '∳': "&awconint;", '∴': "&there4;",
    '∵': "&becaus;", '∶': "&ratio;", '∷': "&Colon;", '∸': "&minusd;", '∺': "&mDDot;", '∻': "&homtht;", '∼': "&sim;",
    '∽': "&bsim;", '∾': "&ac;", '∿': "&acd;", '≀': "&wreath;", '≁': "&nsim;", '≂': "&esim;", '≃': "&sime;",
    '≄': "&nsime;", '≅': "&cong;", '≆': "&simne;", '≇': "&ncong;", '≈': "&asymp;", '≉': "&nap;", '≊': "&ape;",
    '≋': "&apid;", '≌': "&bcong;", '≍': "&asympeq;", '≎': "&bump;", '≏': "&bumpe;", '≐': "&esdot;", '≑': "&eDot;",
    '≒': "&efDot;", '≓': "&erDot;", '≔': "&colone;", '≕': "&ecolon;", '≖': "&ecir;", '≗': "&cire;", '≙': "&wedgeq;",
    '≚': "&veeeq;", '≜': "&trie;", '≟': "&equest;", '≠': "&ne;", '≡': "&equiv;", '≢': "&nequiv;", '≤': "&le;",
    '≥': "&ge;", '≦': "&lE;", '≧': "&gE;", '≨': "&lnE;", '≩': "&gnE;", '≪': "&Lt;", '≫': "&Gt;", '≬': "&twixt;",
    '≭': "&NotCupCap;", '≮': "&nlt;", '≯': "&ngt;", '≰': "&nle;", '≱': "&nge;", '≲': "&lsim;", '≳': "&gsim;",
    '≴': "&nlsim;", '≵': "&ngsim;", '≶': "&lg;", '≷': "&gl;", '≸': "&ntlg;", '≹': "&ntgl;", '≺': "&pr;", '≻': "&sc;",
    '≼': "&prcue;", '≽': "&sccue;", '≾': "&prsim;", '≿': "&scsim;", '⊀': "&npr;", '⊁': "&nsc;", '⊂': "&sub;",
    '⊃': "&sup;", '⊄': "&nsub;", '⊅': "&nsup;", '⊆': "&sube;", '⊇': "&supe;", '⊈': "&nsube;", '⊉': "&nsupe;",
    '⊊': "&subne;", '⊋': "&supne;", '⊍': "&cupdot;", '⊎': "&uplus;", '⊏': "&sqsub;", '⊐': "&sqsup;", '⊑': "&sqsube;",
    '⊒': "&sqsupe;", '⊓': "&sqcap;", '⊔': "&sqcup;", '⊕': "&oplus;", '⊖': "&ominus;", '⊗': "&otimes;", '⊘': "&osol;",
    '⊙': "&odot;", '⊚': "&ocir;", '⊛': "&oast;", '⊝': "&odash;", '⊞': "&plusb;", '⊟': "&minusb;", '⊠': "&timesb;",
    '⊡': "&sdotb;", '⊢': "&vdash;", '⊣': "&dashv;", '⊤': "&top;", '⊥': "&bottom;", '⊧': "&models;", '⊨': "&vDash;",
    '⊩': "&Vdash;", '⊪': "&Vvdash;", '⊫': "&VDash;", '⊬': "&nvdash;", '⊭': "&nvDash;", '⊮': "&nVdash;",
    '⊯': "&nVDash;", '⊰': "&prurel;", '⊲': "&vltri;", '⊳': "&vrtri;", '⊴': "&ltrie;", '⊵': "&rtrie;", '⊶': "&origof;",
    '⊷': "&imof;", '⊸': "&mumap;", '⊹': "&hercon;", '⊺': "&intcal;", '⊻': "&veebar;", '⊽': "&barvee;",
    '⊾': "&angrtvb;", '⊿': "&lrtri;", '⋀': "&xwedge;", '⋁': "&xvee;", '⋂': "&xcap;", '⋃': "&xcup;", '⋄': "&diam;",
    '⋅': "&sdot;", '⋆': "&sstarf;", '⋇': "&divonx;", '⋈': "&bowtie;", '⋉': "&ltimes;", '⋊': "&rtimes;",
    '⋋': "&lthree;", '⋌': "&rthree;", '⋍': "&bsime;", '⋎': "&cuvee;", '⋏': "&cuwed;", '⋐': "&Sub;", '⋑': "&Sup;",
    '⋒': "&Cap;", '⋓': "&Cup;", '⋔': "&fork;", '⋕': "&epar;", '⋖': "&ltdot;", '⋗': "&gtdot;", '⋘': "&Ll;", '⋙': "&Gg;",
    '⋚': "&leg;", '⋛': "&gel;", '⋞': "&cuepr;", '⋟': "&cuesc;", '⋠': "&nprcue;", '⋡': "&nsccue;", '⋢': "&nsqsube;",
    '⋣': "&nsqsupe;", '⋦': "&lnsim;", '⋧': "&gnsim;", '⋨': "&prnsim;", '⋩': "&scnsim;", '⋪': "&nltri;", '⋫': "&nrtri;",
    '⋬': "&nltrie;", '⋭': "&nrtrie;", '⋮': "&vellip;", '⋯': "&ctdot;", '⋰': "&utdot;", '⋱': "&dtdot;", '⋲': "&disin;",
    '⋳': "&isinsv;", '⋴': "&isins;", '⋵': "&isindot;", '⋶': "&notinvc;", '⋷': "&notinvb;", '⋹': "&isinE;",
    '⋺': "&nisd;", '⋻': "&xnis;", '⋼': "&nis;", '⋽': "&notnivc;", '⋾': "&notnivb;", '⌅': "&barwed;", '⌆': "&Barwed;",
    '⌈': "&lceil;", '⌉': "&rceil;", '⌊': "&lfloor;", '⌋': "&rfloor;", '⌌': "&drcrop;", '⌍': "&dlcrop;",
    '⌎': "&urcrop;", '⌏': "&ulcrop;", '⌐': "&bnot;", '⌒': "&profline;", '⌓': "&profsurf;", '⌕': "&telrec;",
    '⌖': "&target;", '⌜': "&ulcorn;", '⌝': "&urcorn;", '⌞': "&dlcorn;", '⌟': "&drcorn;", '⌢': "&frown;",
    '⌣': "&smile;", '⌭': "&cylcty;", '⌮': "&profalar;", '⌶': "&topbot;", '⌽': "&ovbar;", '⌿': "&solbar;",
    '⍼': "&angzarr;", '⎰': "&lmoust;", '⎱': "&rmoust;", '⎴': "&tbrk;", '⎵': "&bbrk;", '⎶': "&bbrktbrk;",
    '⏜': "&OverParenthesis;", '⏝': "&UnderParenthesis;", '⏞': "&OverBrace;", '⏟': "&UnderBrace;", '⏢': "&trpezium;",
    '⏧': "&elinters;", '␣': "&blank;", 'Ⓢ': "&oS;", '─': "&boxh;", '│': "&boxv;", '┌': "&boxdr;", '┐': "&boxdl;",
    '└': "&boxur;", '┘': "&boxul;", '├': "&boxvr;", '┤': "&boxvl;", '┬': "&boxhd;", '┴': "&boxhu;", '┼': "&boxvh;",
    '═': "&boxH;", '║': "&boxV;", '╒': "&boxdR;", '╓': "&boxDr;", '╔': "&boxDR;", '╕': "&boxdL;", '╖': "&boxDl;",
    '╗': "&boxDL;", '╘': "&boxuR;", '╙': "&boxUr;", '╚': "&boxUR;", '╛': "&boxuL;", '╜': "&boxUl;", '╝': "&boxUL;",
    '╞': "&boxvR;", '╟': "&boxVr;", '╠': "&boxVR;", '╡': "&boxvL;", '╢': "&boxVl;", '╣': "&boxVL;", '╤': "&boxHd;",
    '╥': "&boxhD;", '╦': "&boxHD;", '╧': "&boxHu;", '╨': "&boxhU;", '╩': "&boxHU;", '╪': "&boxvH;", '╫': "&boxVh;",
    '╬': "&boxVH;", '▀': "&uhblk;", '▄': "&lhblk;", '█': "&block;", '░': "&blk14;", '▒': "&blk12;", '▓': "&blk34;",
    '□': "&squ;", '▪': "&squf;", '▫': "&EmptyVerySmallSquare;", '▭': "&rect;", '▮': "&marker;", '▱': "&fltns;",
    '△': "&xutri;", '▴': "&utrif;", '▵': "&utri;", '▸': "&rtrif;", '▹': "&rtri;", '▽': "&xdtri;", '▾': "&dtrif;",
    '▿': "&dtri;", '◂': "&ltrif;", '◃': "&ltri;", '◊': "&loz;", '○': "&cir;", '◬': "&tridot;", '◯': "&xcirc;",
    '◸': "&ultri;", '◹': "&urtri;", '◺': "&lltri;", '◻': "&EmptySmallSquare;", '◼': "&FilledSmallSquare;",
    '★': "&starf;", '☆': "&star;", '☎': "&phone;", '♀': "&female;", '♂': "&male;", '♠': "&spades;", '♣': "&clubs;",
    '♥': "&hearts;", '♦': "&diams;", '♪': "&sung;", '♭': "&flat;", '♮': "&natur;", '♯': "&sharp;", '✓': "&check;",
    '✗': "&cross;", '✠': "&malt;", '✶': "&sext;", '❘': "&VerticalSeparator;", '❲': "&lbbrk;", '❳': "&rbbrk;",
    '⟦': "&lobrk;", '⟧': "&robrk;", '⟨': "&lang;", '⟩': "&rang;", '⟪': "&Lang;", '⟫': "&Rang;", '⟬': "&loang;",
    '⟭': "&roang;", '⟵': "&xlarr;", '⟶': "&xrarr;", '⟷': "&xharr;", '⟸': "&xlArr;", '⟹': "&xrArr;", '⟺': "&xhArr;",
    '⟼': "&xmap;", '⟿': "&dzigrarr;", '⤂': "&nvlArr;", '⤃': "&nvrArr;", '⤄': "&nvHarr;", '⤅': "&Map;", '⤌': "&lbarr;",
    '⤍': "&rbarr;", '⤎': "&lBarr;", '⤏': "&rBarr;", '⤐': "&RBarr;", '⤑': "&DDotrahd;", '⤒': "&UpArrowBar;",
    '⤓': "&DownArrowBar;", '⤖': "&Rarrtl;", '⤙': "&latail;", '⤚': "&ratail;", '⤛': "&lAtail;", '⤜': "&rAtail;",
    '⤝': "&larrfs;", '⤞': "&rarrfs;", '⤟': "&larrbfs;", '⤠': "&rarrbfs;", '⤣': "&nwarhk;", '⤤': "&nearhk;",
    '⤥': "&searhk;", '⤦': "&swarhk;", '⤧': "&nwnear;", '⤨': "&nesear;", '⤩': "&seswar;", '⤪': "&swnwar;",
    '⤳': "&rarrc;", '⤵': "&cudarrr;", '⤶': "&ldca;", '⤷': "&rdca;", '⤸': "&cudarrl;", '⤹': "&larrpl;",
    '⤼': "&curarrm;", '⤽': "&cularrp;", '⥅': "&rarrpl;", '⥈': "&harrcir;", '⥉': "&Uarrocir;", '⥊': "&lurdshar;",
    '⥋': "&ldrushar;", '⥎': "&LeftRightVector;", '⥏': "&RightUpDownVector;", '⥐': "&DownLeftRightVector;",
    '⥑': "&LeftUpDownVector;", '⥒': "&LeftVectorBar;", '⥓': "&RightVectorBar;", '⥔': "&RightUpVectorBar;",
    '⥕': "&RightDownVectorBar;", '⥖': "&DownLeftVectorBar;", '⥗': "&DownRightVectorBar;", '⥘': "&LeftUpVectorBar;",
    '⥙': "&LeftDownVectorBar;", '⥚': "&LeftTeeVector;", '⥛': "&RightTeeVector;", '⥜': "&RightUpTeeVector;",
    '⥝': "&RightDownTeeVector;", '⥞': "&DownLeftTeeVector;", '⥟': "&DownRightTeeVector;", '⥠': "&LeftUpTeeVector;",
    '⥡': "&LeftDownTeeVector;", '⥢': "&lHar;", '⥣': "&uHar;", '⥤': "&rHar;", '⥥': "&dHar;", '⥦': "&luruhar;",
    '⥧': "&ldrdhar;", '⥨': "&ruluhar;", '⥩': "&rdldhar;", '⥪': "&lharul;", '⥫': "&llhard;", '⥬': "&rharul;",
    '⥭': "&lrhard;", '⥮': "&udhar;", '⥯': "&duhar;", '⥰': "&RoundImplies;", '⥱': "&erarr;", '⥲': "&simrarr;",
    '⥳': "&larrsim;", '⥴': "&rarrsim;", '⥵': "&rarrap;", '⥶': "&ltlarr;", '⥸': "&gtrarr;", '⥹': "&subrarr;",
    '⥻': "&suplarr;", '⥼': "&lfisht;", '⥽': "&rfisht;", '⥾': "&ufisht;", '⥿': "&dfisht;", '⦅': "&lopar;",
    '⦆': "&ropar;", '⦋': "&lbrke;", '⦌': "&rbrke;", '⦍': "&lbrkslu;", '⦎': "&rbrksld;", '⦏': "&lbrksld;",
    '⦐': "&rbrkslu;", '⦑': "&langd;", '⦒': "&rangd;", '⦓': "&lparlt;", '⦔': "&rpargt;", '⦕': "&gtlPar;",
    '⦖': "&ltrPar;", '⦚': "&vzigzag;", '⦜': "&vangrt;", '⦝': "&angrtvbd;", '⦤': "&ange;", '⦥': "&range;",
    '⦦': "&dwangle;", '⦧': "&uwangle;", '⦨': "&angmsdaa;", '⦩': "&angmsdab;", '⦪': "&angmsdac;", '⦫': "&angmsdad;",
    '⦬': "&angmsdae;", '⦭': "&angmsdaf;", '⦮': "&angmsdag;", '⦯': "&angmsdah;", '⦰': "&bemptyv;", '⦱': "&demptyv;",
    '⦲': "&cemptyv;", '⦳': "&raemptyv;", '⦴': "&laemptyv;", '⦵': "&ohbar;", '⦶': "&omid;", '⦷': "&opar;",
    '⦹': "&operp;", '⦻': "&olcross;", '⦼': "&odsold;", '⦾': "&olcir;", '⦿': "&ofcir;", '⧀': "&olt;", '⧁': "&ogt;",
    '⧂': "&cirscir;", '⧃': "&cirE;", '⧄': "&solb;", '⧅': "&bsolb;", '⧉': "&boxbox;", '⧍': "&trisb;", '⧎': "&rtriltri;",
    '⧏': "&LeftTriangleBar;", '⧐': "&RightTriangleBar;", '⧚': "&race;", '⧜': "&iinfin;", '⧝': "&infintie;",
    '⧞': "&nvinfin;", '⧣': "&eparsl;", '⧤': "&smeparsl;", '⧥': "&eqvparsl;", '⧫': "&lozf;", '⧴': "&RuleDelayed;",
    '⧶': "&dsol;", '⨀': "&xodot;", '⨁': "&xoplus;", '⨂': "&xotime;", '⨄': "&xuplus;", '⨆': "&xsqcup;", '⨌': "&qint;",
    '⨍': "&fpartint;", '⨐': "&cirfnint;", '⨑': "&awint;", '⨒': "&rppolint;", '⨓': "&scpolint;", '⨔': "&npolint;",
    '⨕': "&pointint;", '⨖': "&quatint;", '⨗': "&intlarhk;", '⨢': "&pluscir;", '⨣': "&plusacir;", '⨤': "&simplus;",
    '⨥': "&plusdu;", '⨦': "&plussim;", '⨧': "&plustwo;", '⨩': "&mcomma;", '⨪': "&minusdu;", '⨭': "&loplus;",
    '⨮': "&roplus;", '⨯': "&Cross;", '⨰': "&timesd;", '⨱': "&timesbar;", '⨳': "&smashp;", '⨴': "&lotimes;",
    '⨵': "&rotimes;", '⨶': "&otimesas;", '⨷': "&Otimes;", '⨸': "&odiv;", '⨹': "&triplus;", '⨺': "&triminus;",
    '⨻': "&tritime;", '⨼': "&iprod;", '⨿': "&amalg;", '⩀': "&capdot;", '⩂': "&ncup;", '⩃': "&ncap;", '⩄': "&capand;",
    '⩅': "&cupor;", '⩆': "&cupcap;", '⩇': "&capcup;", '⩈': "&cupbrcap;", '⩉': "&capbrcup;", '⩊': "&cupcup;",
    '⩋': "&capcap;", '⩌': "&ccups;", '⩍': "&ccaps;", '⩐': "&ccupssm;", '⩓': "&And;", '⩔': "&Or;", '⩕': "&andand;",
    '⩖': "&oror;", '⩗': "&orslope;", '⩘': "&andslope;", '⩚': "&andv;", '⩛': "&orv;", '⩜': "&andd;", '⩝': "&ord;",
    '⩟': "&wedbar;", '⩦': "&sdote;", '⩪': "&simdot;", '⩭': "&congdot;", '⩮': "&easter;", '⩯': "&apacir;", '⩰': "&apE;",
    '⩱': "&eplus;", '⩲': "&pluse;", '⩳': "&Esim;", '⩴': "&Colone;", '⩵': "&Equal;", '⩷': "&eDDot;", '⩸': "&equivDD;",
    '⩹': "&ltcir;", '⩺': "&gtcir;", '⩻': "&ltquest;", '⩼': "&gtquest;", '⩽': "&les;", '⩾': "&ges;", '⩿': "&lesdot;",
    '⪀': "&gesdot;", '⪁': "&lesdoto;", '⪂': "&gesdoto;", '⪃': "&lesdotor;", '⪄': "&gesdotol;", '⪅': "&lap;",
    '⪆': "&gap;", '⪇': "&lne;", '⪈': "&gne;", '⪉': "&lnap;", '⪊': "&gnap;", '⪋': "&lEg;", '⪌': "&gEl;", '⪍': "&lsime;",
    '⪎': "&gsime;", '⪏': "&lsimg;", '⪐': "&gsiml;", '⪑': "&lgE;", '⪒': "&glE;", '⪓': "&lesges;", '⪔': "&gesles;",
    '⪕': "&els;", '⪖': "&egs;", '⪗': "&elsdot;", '⪘': "&egsdot;", '⪙': "&el;", '⪚': "&eg;", '⪝': "&siml;",
    '⪞': "&simg;", '⪟': "&simlE;", '⪠': "&simgE;", '⪡': "&LessLess;", '⪢': "&GreaterGreater;", '⪤': "&glj;",
    '⪥': "&gla;", '⪦': "&ltcc;", '⪧': "&gtcc;", '⪨': "&lescc;", '⪩': "&gescc;", '⪪': "&smt;", '⪫': "&lat;",
    '⪬': "&smte;", '⪭': "&late;", '⪮': "&bumpE;", '⪯': "&pre;", '⪰': "&sce;", '⪳': "&prE;", '⪴': "&scE;",
    '⪵': "&prnE;", '⪶': "&scnE;", '⪷': "&prap;", '⪸': "&scap;", '⪹': "&prnap;", '⪺': "&scnap;", '⪻': "&Pr;",
    '⪼': "&Sc;", '⪽': "&subdot;", '⪾': "&supdot;", '⪿': "&subplus;", '⫀': "&supplus;", '⫁': "&submult;",
    '⫂': "&supmult;", '⫃': "&subedot;", '⫄': "&supedot;", '⫅': "&subE;", '⫆': "&supE;", '⫇': "&subsim;",
    '⫈': "&supsim;", '⫋': "&subnE;", '⫌': "&supnE;", '⫏': "&csub;", '⫐': "&csup;", '⫑': "&csube;", '⫒': "&csupe;",
    '⫓': "&subsup;", '⫔': "&supsub;", '⫕': "&subsub;", '⫖': "&supsup;", '⫗': "&suphsub;", '⫘': "&supdsub;",
    '⫙': "&forkv;", '⫚': "&topfork;", '⫛': "&mlcp;", '⫤': "&Dashv;", '⫦': "&Vdashl;", '⫧': "&Barv;", '⫨': "&vBar;",
    '⫩': "&vBarv;", '⫫': "&Vbar;", '⫬': "&Not;", '⫭': "&bNot;", '⫮': "&rnmid;", '⫯': "&cirmid;", '⫰': "&midcir;",
    '⫱': "&topcir;", '⫲': "&nhpar;", '⫳': "&parsim;", '⫽': "&parsl;", 'ﬀ': "&fflig;", 'ﬁ': "&filig;", 'ﬂ': "&fllig;",
    'ﬃ': "&ffilig;", 'ﬄ': "&ffllig;", '𝒜': "&Ascr;", '𝒞': "&Cscr;", '𝒟': "&Dscr;", '𝒢': "&Gscr;", '𝒥': "&Jscr;",
    '𝒦': "&Kscr;", '𝒩': "&Nscr;", '𝒪': "&Oscr;", '𝒫': "&Pscr;", '𝒬': "&Qscr;", '𝒮': "&Sscr;", '𝒯': "&Tscr;",
    '𝒰': "&Uscr;", '𝒱': "&Vscr;", '𝒲': "&Wscr;", '𝒳': "&Xscr;", '𝒴': "&Yscr;", '𝒵': "&Zscr;", '𝒶': "&ascr;",
    '𝒷': "&bscr;", '𝒸': "&cscr;", '𝒹': "&dscr;", '𝒻': "&fscr;", '𝒽': "&hscr;", '𝒾': "&iscr;", '𝒿': "&jscr;",
    '𝓀': "&kscr;", '𝓁': "&lscr;", '𝓂': "&mscr;", '𝓃': "&nscr;", '𝓅': "&pscr;", '𝓆': "&qscr;", '𝓇': "&rscr;",
    '𝓈': "&sscr;", '𝓉': "&tscr;", '𝓊': "&uscr;", '𝓋': "&vscr;", '𝓌': "&wscr;", '𝓍': "&xscr;", '𝓎': "&yscr;",
    '𝓏': "&zscr;", '𝔄': "&Afr;", '𝔅': "&Bfr;", '𝔇': "&Dfr;", '𝔈': "&Efr;", '𝔉': "&Ffr;", '𝔊': "&Gfr;", '𝔍': "&Jfr;",
    '𝔎': "&Kfr;", '𝔏': "&Lfr;", '𝔐': "&Mfr;", '𝔑': "&Nfr;", '𝔒': "&Ofr;", '𝔓': "&Pfr;", '𝔔': "&Qfr;", '𝔖': "&Sfr;",
    '𝔗': "&Tfr;", '𝔘': "&Ufr;", '𝔙': "&Vfr;", '𝔚': "&Wfr;", '𝔛': "&Xfr;", '𝔜': "&Yfr;", '𝔞': "&afr;", '𝔟': "&bfr;",
    '𝔠': "&cfr;", '𝔡': "&dfr;", '𝔢': "&efr;", '𝔣': "&ffr;", '𝔤': "&gfr;", '𝔥': "&hfr;", '𝔦': "&ifr;", '𝔧': "&jfr;",
    '𝔨': "&kfr;", '𝔩': "&lfr;", '𝔪': "&mfr;", '𝔫': "&nfr;", '𝔬': "&ofr;", '𝔭': "&pfr;", '𝔮': "&qfr;", '𝔯': "&rfr;",
    '𝔰': "&sfr;", '𝔱': "&tfr;", '𝔲': "&ufr;", '𝔳': "&vfr;", '𝔴': "&wfr;", '𝔵': "&xfr;", '𝔶': "&yfr;", '𝔷': "&zfr;",
    '𝔸': "&Aopf;", '𝔹': "&Bopf;", '𝔻': "&Dopf;", '𝔼': "&Eopf;", '𝔽': "&Fopf;", '𝔾': "&Gopf;", '𝕀': "&Iopf;",
    '𝕁': "&Jopf;", '𝕂': "&Kopf;", '𝕃': "&Lopf;", '𝕄': "&Mopf;", '𝕆': "&Oopf;", '𝕊': "&Sopf;", '𝕋': "&Topf;",
    '𝕌': "&Uopf;", '𝕍': "&Vopf;", '𝕎': "&Wopf;", '𝕏': "&Xopf;", '𝕐': "&Yopf;", '𝕒': "&aopf;", '𝕓': "&bopf;",
    '𝕔': "&copf;", '𝕕': "&dopf;", '𝕖': "&eopf;", '𝕗': "&fopf;", '𝕘': "&gopf;", '𝕙': "&hopf;", '𝕚': "&iopf;",
    '𝕛': "&jopf;", '𝕜': "&kopf;", '𝕝': "&lopf;", '𝕞': "&mopf;", '𝕟': "&nopf;", '𝕠': "&oopf;", '𝕡': "&popf;",
    '𝕢': "&qopf;", '𝕣': "&ropf;", '𝕤': "&sopf;", '𝕥': "&topf;", '𝕦': "&uopf;", '𝕧': "&vopf;", '𝕨': "&wopf;",
    '𝕩': "&xopf;", '𝕪': "&yopf;", '𝕫': "&zopf;",
}
DECMAP = {v: k for k, v in ENCMAP.items()}


class HtmlEntityDecodeError(ValueError):
    pass


def htmlentity_encode(text, errors="strict"):
    s = ""
    for c in text:
        try:
            s += ENCMAP[c]
        except KeyError:
            i = ord(c)
            s += "&" + hex(i)[2:].zfill(0) + ";" if i > 0xff else c
    return s, len(text)


def htmlentity_decode(text, errors="strict"):
    s = ""
    i = 0
    while i < len(text):
        m = re.match(r"&(?:(?:[A-Za-z][A-Za-z0-9]{1,6}){1,4}|[0-9]{4});", text[i:i+30])
        if m:
            entity = m.group()
            c = chr(int(entity[1:5], 16)) if entity[1:5].isdigit() and len(entity) == 6 else \
                " " if entity == "&nbsp;" else None
            if c:
                s += c
            else:
                try:
                    s += DECMAP[entity]
                except KeyError:
                    s += handle_error("html-entity", errors, HtmlEntityDecodeError, decode=True)(text[i], i)
            i += len(entity)
        else:
            s += text[i]
            i += 1
    return s, len(text)


add("html", htmlentity_encode, htmlentity_decode, r"^html(?:[-_]?entit(?:y|ies))?$",
    extra_exceptions=["HtmlEntityDecodeError"])

