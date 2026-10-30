`codext` implements some common Web-related encodings.

-----

### AAEncode

[AAEncode](https://utf-8.jp/public/aaencode.html), by Yosuke Hasegawa, turns JavaScript code into a JavaScript program made of Japanese-style emoticons (e.g. `ﾟωﾟﾉ` or `(ﾟДﾟ)`) that runs the code. The program builds the characters it needs from the string representations of JavaScript values (e.g. `false` or `undefined`), gets the `Function` constructor and calls it on a string literal holding the code, each character being written as an octal or Unicode escape sequence of its UTF-16 code unit. Encoding gives the same program as the reference encoder, while decoding parses the program (without running it), whatever its whitespaces, and returns the code.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`aaencode` | JavaScript code <-> AAEncoded program | `aa-encode`, `aa_encode` | malformed programs reported whatever the errors handling

```python
>>> js = codext.encode("alert(1)", "aaencode")
>>> js[:46]
"ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  ="
>>> codext.decode(js, "aaencode")
'alert(1)'
```

-----

### HTML Entities

This implements the full list of characters available at [this reference](https://dev.w3.org/html5/html-author/charref).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`html` | text <-> HTML entities | `html-entity`, `html_entities` | implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)

```python
>>> codext.encode("Тħĩş Їś ą Ţêšŧ", "html")
'&Tcy;&hstrok;&itilde;&scedil; &YIcy;&sacute; &aogon; &Tcedil;&ecirc;&scaron;&tstrok;'
>>> codext.decode("&Tcy;&hstrok;&itilde;&scedil; &YIcy;&sacute; &aogon; &Tcedil;&ecirc;&scaron;&tstrok;", "html-entities")
'Тħĩş Їś ą Ţêšŧ'
```

-----

### JJEncode

[JJEncode](https://utf-8.jp/public/jjencode.html), by Yosuke Hasegawa, turns JavaScript code into a JavaScript program only made of symbols (`$`, `_`, `+`, `!`, ...) and of the name of a global variable (`$` by default), that runs the code. The program fills the variable with an object whose properties hold the hexadecimal digits and some letters taken from the string representations of JavaScript values (e.g. `false` or `[object Object]`), gets the `Function` constructor and calls it on a string literal holding the code. Some punctuation characters are kept as is, the hexadecimal digits and the letters `l`, `o`, `t` and `u` are taken from the properties and the other characters are written as octal or Unicode escape sequences of their UTF-16 code units. Decoding parses the program (without running it), whatever the name of the variable, and returns the code.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`jjencode` | JavaScript code <-> JJEncoded program | `jj-encode`, `jj_encode` | malformed programs reported whatever the errors handling
`jjencode-[var]` | JavaScript code <-> JJEncoded program using the given global variable | `jjencode-_`, `jj_encode-$x` | the variable name is a JavaScript identifier ; decoding reads it from the program

!!! note "Differences with the reference encoder"

    The reference encoder gives a wrong program in two cases, where this codec pads the escape sequences instead: a character above U+007F and below U+1000 gets less than four hexadecimal digits (e.g. `\ue9` for `é`, a syntax error), and an octal escape sequence followed by a digit absorbs it (e.g. `\1` followed by `2` gives `\12`, a newline). Otherwise, encoding gives the same program as the reference encoder.

```python
>>> js = codext.encode("alert(1)", "jjencode-x")
>>> js[:17]
'x=~[];x={___:++x,'
>>> js[432:]
'x.$(x.$(x.$$+"\\""+x.$_$_+(![]+"")[x._$_]+x.$$$_+"\\\\"+x.__$+x.$$_+x._$_+x.__+"("+x.__$+")"+"\\"")())();'
>>> codext.decode(js, "jjencode")
'alert(1)'
```

-----

### URL

This handles URL encoding, regardless of the case when decoding and with no error.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`url` | text <-> URL encoded text | `url`, `urlencode` | 

```python
>>> codecs.encode("?=this/is-a_test/../", "url")
'%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F'
>>> codext.decode("%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F", "urlencode")
'?=this/is-a_test/../'
>>> codext.decode("%3f%3dthis%2fis-a_test%2f%2e%2e%2f", "urlencode")
'?=this/is-a_test/../'
```

