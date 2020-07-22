With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings).

Unless explicitely specified, each codec supports writing to and reading from a file.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

