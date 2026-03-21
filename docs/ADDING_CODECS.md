# Adding a Codec

1. Categorize accordingly ; categories are the folder names in `src/codext` (further folder references are relative to this). When a category cannot be put in one of these folders, it shall be put by default in `others`.

2. Add the `.py` file in the relevant category folder, named with the short name of the new codec.

3. Respect the typical structure of a codec's `.py` file according to the following template (double-bracketed enclosures indicate codec parameters, double-arrowed enclosures indicate instructions that may refer to further steps of this guideline):

    ```python
    # -*- coding: UTF-8 -*-
    """{{codec_long_name}} Codec - {{codec_short_name}} content encoding.

    {{codec_description}}

    This codec:
    - en/decodes strings from str to str
    - en/decodes strings from bytes to bytes
    - decodes file content to str (read)
    - encodes file content from str to bytes (write)

    Reference: {{codec_source_hyperlink}}
    """
    from ..__common__ import *


    __examples__ = {<<dictionary of examples with, as keys, a special format detailed hereafter and, as values, a dictionary mapping source to destination values (see 7.)>>}
    <<optional list of valid codec names to be used with the guessing mode (see 8.), in format "__guess__ = [...]">>]


    <<constants here, including ENCMAP if the codec is a simple mapping (see 6.)>>
    <<functions here, if the codec requires some additional logic, i.e. when it is not a mapping (see 6.)>>


    <<put the right add function (see 4.) here with its relevant parameters (see 5.)>>
    ```

4. Choose the right add function

    If the codec is a simple mapping, use the `add_map` function.
    
    Examples: `languages/braille`, `languages/morse`, `languages/southpark`

    In some cases, an algorithm can even be equivalent to one or a number of mappings and can then be defined as a dynamic generation of `ENCMAP`.
    
    Examples: `stegano/resistor`, `crypto/barbie`
    
    When the codec is more complex than a mapping, use the `add` function.

5. Configure the add function

    Refer to the relevant function signature in `__common__.py`.

6. Write the codec logic

    If the codec is a mapping, at least `ENC_MAP` should be defined and refered in the parameters of the `add_map` function.
    
    Examples: `stegano/rick`, `stegano/klopf`
    
    If the codec is not a mapping, the logic can be written in the following order: the encoding function first, then the decoding function.
    
    Examples: `stegano/whitespace`, `crypto/railfence`

7. Write some examples

    Examples are used during the automated test generation. They should then be carefully written to also cover some edge cases. A set of 3-8 examples is generally a must.

8. Specify the names to be used with the guessing mode

    The `__guess__` list of codec names is used to limit the possibilities in the tree search from the guessing mode. Especially when the codec is dynamic and may have a large (or even infinite) number of dynamic names, it is necessary to set a limited number, generally maximum 16 as a best practice. This list, when relevant, shall be used with due care.
