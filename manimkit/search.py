"""Retrieval over the example corpus.

The default scorer is a small, dependency-free BM25 over each example's title,
tags, description and the Manim identifiers its code uses (``BarChart``,
``ValueTracker``, ``always_redraw`` ...). Fields are weighted by repetition, and
identifiers are split (``MoveAlongPath`` -> ``move along path movealongpath``) so a
plain-English query still reaches a class name.

``scorer=`` is the seam: any ``(query_tokens, docs_tokens) -> list[float]``
(an embedding scorer, say) drops in without touching the corpus.

>>> hits = search_examples("bar chart", k=3, sources=["curated"])
>>> len(hits) <= 3 and all(h.score > 0 for h in hits)
True
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from manimkit.corpus import DFLT_SOURCES, Example, iter_examples

# Field weights (how many times a field's tokens are counted).
FIELD_WEIGHTS = {"title": 3, "tags": 3, "description": 2, "identifiers": 1}
# Prior per origin: full curated scenes beat API snippets at equal relevance.
ORIGIN_WEIGHTS = {"curated": 1.6, "gallery": 1.3, "user": 1.6, "api": 1.0}
BM25_K1, BM25_B = 1.4, 0.75
DFLT_K = 5

STOPWORDS = frozenset(
    "a an the and or of to in on for with from by is are be as at it this that "
    "how make me show using use into over under my i want some self def class "
    "construct scene return none true false import".split()
)
_IDENTIFIER = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")
_WORD = re.compile(r"[A-Za-z][a-z]+|[A-Z]+(?![a-z])|\d+")


@dataclass(frozen=True)
class Hit:
    """A search result: the example and its score."""

    example: Example
    score: float

    def __str__(self) -> str:
        return f"{self.score:6.2f}  {self.example.summary()}"


def _stem(word: str) -> str:
    """Crude suffix folding so 'sorted', 'sorting', 'sorts' meet at 'sort'.

    >>> [_stem(w) for w in ["curves", "sorted", "sorting", "axes", "always", "moving", "move", "labelled"]]
    ['curv', 'sort', 'sort', 'axes', 'always', 'mov', 'mov', 'label']
    """
    if len(word) > 5 and word.endswith("ing"):
        word = word[:-3]
    elif len(word) > 4 and word.endswith("ed"):
        word = word[:-2]
    elif (
        len(word) > 3
        and word.endswith("s")
        and not word.endswith(("ss", "us", "is", "ys", "axes"))
    ):
        word = word[:-1]
    if len(word) > 4 and word[-1] == word[-2] and word[-1] not in "aeiousl":
        word = word[:-1]  # 'mapp(ing)' -> 'map'
    elif len(word) > 4 and word.endswith("ll"):
        word = word[:-1]
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]  # 'move' and 'moving' both -> 'mov'
    return word


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, with identifiers split and also kept whole.

    >>> tokenize("MoveAlongPath and always_redraw")
    ['mov', 'along', 'path', 'movealongpath', 'always', 'redraw', 'always_redraw']
    """
    out = []
    for raw in re.findall(r"[A-Za-z0-9_]+", text):
        parts = [
            _stem(p.lower()) for piece in raw.split("_") for p in _WORD.findall(piece)
        ]
        out.extend(p for p in parts if p not in STOPWORDS)
        whole = raw.lower()
        if (len(parts) > 1 or "_" in raw) and whole not in STOPWORDS:
            out.append(whole)
    return out


def example_tokens(ex: Example, *, field_weights=None) -> list[str]:
    """The weighted bag of tokens an example is indexed under."""
    w = field_weights or FIELD_WEIGHTS
    identifiers = " ".join(sorted(set(_IDENTIFIER.findall(ex.code))))
    fields = {
        "title": ex.title,
        "tags": " ".join(ex.tags),
        "description": ex.description,
        "identifiers": identifiers,
    }
    tokens = []
    for name, text in fields.items():
        tokens.extend(tokenize(text) * w.get(name, 1))
    return tokens


def bm25_scores(query: Sequence[str], docs: Sequence[Sequence[str]]) -> list[float]:
    """Okapi BM25 of ``query`` against each tokenized doc."""
    n = len(docs)
    if not n:
        return []
    avgdl = sum(len(d) for d in docs) / n or 1.0
    df = Counter(t for d in docs for t in set(d))
    counts = [Counter(d) for d in docs]
    scores = []
    for d, tf in zip(docs, counts):
        s = 0.0
        for t in set(query):
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            f = tf[t]
            s += (
                idf
                * f
                * (BM25_K1 + 1)
                / (f + BM25_K1 * (1 - BM25_B + BM25_B * len(d) / avgdl))
            )
        scores.append(s)
    return scores


def search_examples(
    query: str,
    k: int = DFLT_K,
    *,
    sources: Iterable = DFLT_SOURCES,
    origin: str | Sequence[str] | None = None,
    latex: bool | None = None,
    scorer: Callable[
        [Sequence[str], Sequence[Sequence[str]]], list[float]
    ] = bm25_scores,
    origin_weights: dict | None = None,
) -> list[Hit]:
    """The ``k`` examples most relevant to ``query``, best first.

    :param origin: keep only these origins (``'curated'``, ``'gallery'``, ``'api'``).
    :param latex: ``False`` drops examples that need a LaTeX install; ``True``
        keeps only those; ``None`` keeps all.
    :param scorer: the ranking function (the seam for embedding retrieval).
    """
    examples = list(iter_examples(sources))
    if origin is not None:
        wanted = {origin} if isinstance(origin, str) else set(origin)
        examples = [e for e in examples if e.origin in wanted]
    if latex is not None:
        examples = [e for e in examples if e.needs_latex == latex]
    q = tokenize(query)
    if not q or not examples:
        return []
    raw = scorer(q, [example_tokens(e) for e in examples])
    ow = ORIGIN_WEIGHTS if origin_weights is None else origin_weights
    hits = [
        Hit(e, round(s * ow.get(e.origin, 1.0), 3))
        for e, s in zip(examples, raw)
        if s > 0
    ]
    hits.sort(key=lambda h: -h.score)
    return hits[:k]
