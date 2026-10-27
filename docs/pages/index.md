Codext, contraction of "*codecs*" and "*extension*", is a library that gathers many additional encodings for use with [`codecs`](https://docs.python.org/3/library/codecs.html). When imported, it registers new encodings to an extended codecs registry for making the encodings available from the `codecs.(decode|encode|open)` API. It also features [CLI tools](cli.md) and a [guess mode](guessing.md) for decoding multiple layers of codecs.

### Setup

This library requires Python 3.10 or later. It is available on [PyPi](https://pypi.python.org/pypi/codext/) and can be simply installed using Pip:

```sh
pip install codext
```
