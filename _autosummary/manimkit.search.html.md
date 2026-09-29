# manimkit.search

Retrieval over the example corpus.

The default scorer is a small, dependency-free BM25 over each example’s title,
tags, description and the Manim identifiers its code uses (`BarChart`,
`ValueTracker`, `always_redraw` …). Fields are weighted by repetition, and
identifiers are split (`MoveAlongPath` -> `move along path movealongpath`) so a
plain-English query still reaches a class name.

`scorer=` is the seam: any `(query_tokens, docs_tokens) -> list[float]`
(an embedding scorer, say) drops in without touching the corpus.

```pycon
>>> hits = search_examples("bar chart", k=3, sources=["curated"])
>>> len(hits) <= 3 and all(h.score > 0 for h in hits)
True
```

### Functions

| [`bm25_scores`](#manimkit.search.bm25_scores)(query, docs)                          | Okapi BM25 of `query` against each tokenized doc.                  |
|----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| [`example_tokens`](#manimkit.search.example_tokens)(ex, \*[, field_weights])           | The weighted bag of tokens an example is indexed under.            |
| [`search_examples`](#manimkit.search.search_examples)(query[, k, sources, origin, ...]) | The `k` examples most relevant to `query`, best first.             |
| [`tokenize`](#manimkit.search.tokenize)(text)                                    | Lowercase word tokens, with identifiers split and also kept whole. |

### Classes

| [`Hit`](#manimkit.search.Hit)(example, score)   | A search result: the example and its score.   |
|------------------------------------------------------------------------|-----------------------------------------------|

### *class* manimkit.search.Hit(example, score)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A search result: the example and its score.

### manimkit.search.bm25_scores(query, docs)

Okapi BM25 of `query` against each tokenized doc.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`float`](https://docs.python.org/3/builtins/functions.html#float)]

### manimkit.search.example_tokens(ex, , field_weights=None)

The weighted bag of tokens an example is indexed under.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### manimkit.search.search_examples(query, k=5, \*, sources=('curated', 'api'), origin=None, latex=None, scorer=<function bm25_scores>, origin_weights=None)

The `k` examples most relevant to `query`, best first.

* **Parameters:**
  * **origin** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`None`](https://docs.python.org/3/builtins/constants.html#None)]) – keep only these origins (`'curated'`, `'gallery'`, `'api'`).
  * **latex** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – `False` drops examples that need a LaTeX install; `True`
    keeps only those; `None` keeps all.
  * **scorer** ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)[[[`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]], [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`float`](https://docs.python.org/3/builtins/functions.html#float)]]) – the ranking function (the seam for embedding retrieval).
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`Hit`](#manimkit.search.Hit)]

### manimkit.search.tokenize(text)

Lowercase word tokens, with identifiers split and also kept whole.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

```pycon
>>> tokenize("MoveAlongPath and always_redraw")
['mov', 'along', 'path', 'movealongpath', 'always', 'redraw', 'always_redraw']
```
