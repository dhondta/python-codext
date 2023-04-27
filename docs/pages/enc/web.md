`codext` implements some common Web-related encodings.

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

