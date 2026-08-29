# wordtally-tools

Count and rank the words in a text file, from Python or from the command line.

This project exists to be built, inspected and installed. It is a teaching
package and is deliberately not published to any index.

## Install

```bash
pip install wordtally-tools
```

The distribution name is `wordtally-tools`; the import name is `wordtally`.

## Use it as a library

```python
from wordtally import count_words, top_words

count_words("the cat sat on the mat")          # 6
top_words("the cat sat on the cat mat", n=2)   # [('cat', 2), ('mat', 1)]
```

## Use it as a command

```bash
wordtally count sample.txt
wordtally top sample.txt -n 5
wordtally --version
```

`wordtally top` filters common words such as `the` and `and` using a stop-word
list shipped inside the package; pass `--keep-stopwords` to turn that off.

## Licence

MIT. See `LICENSE`.
