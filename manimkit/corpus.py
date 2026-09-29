"""The example corpus: working ManimCE scenes an agent can retrieve and adapt.

Two sources feed it, both yielding :class:`Example` records:

- **curated** — scenes shipped in ``manimkit/data/examples/`` (original ones, plus
  the Manim Community example gallery, MIT, with attribution). Each file starts
  with a small header docstring::

      '''Bar chart that grows, then re-sorts.

      tags: data, bar chart, BarChart, story
      scene: BarChartStory
      source: original (manimkit, MIT)

      Free-text description, as long as useful.
      '''

- **api** — the ``.. manim::`` examples embedded in the docstrings of the
  *installed* manim package, harvested on demand. They are version-matched to the
  manim you actually have, which is the cheapest defence against an agent writing
  code for an API that has since moved.

>>> ex = next(iter(curated_examples()))
>>> isinstance(ex, Example) and ex.origin in {"curated", "gallery"}
True
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Iterable, Iterator

MANIM_IMPORT = "from manim import *"
HEADER_KEYS = ("tags", "scene", "source", "latex")

# Names whose use (in ManimCE) goes through LaTeX. A hint only: used to let an
# agent without a TeX install filter examples out, never to refuse anything.
LATEX_PATTERN = re.compile(
    r"\b(MathTex|Tex|SingleStringMathTex|DecimalNumber|Integer|Variable|Matrix"
    r"|IntegerMatrix|DecimalMatrix|MobjectMatrix|MathTable|IntegerTable"
    r"|DecimalTable|BarChart|BraceLabel|BraceText|get_tex|get_axis_labels"
    r"|get_graph_label|get_y_axis_label|get_x_axis_label|include_numbers"
    r"|add_coordinates|get_riemann_rectangles_label|Title)\b"
)
SCENE_CLASS_PATTERN = re.compile(r"^class\s+(\w+)\s*\(([^)]*)\)\s*:", re.M)
DIRECTIVE_PATTERN = re.compile(r"^(?P<indent>[ \t]*)\.\. manim::\s*(?P<name>\w+)\s*$")


def uses_latex(code: str) -> bool:
    """Whether code (docstrings and comments ignored) uses something that needs LaTeX.

    >>> uses_latex("'''Unlike BarChart, no LaTeX.'''\\nText('hi')  # not MathTex")
    False
    >>> uses_latex('MathTex(r"x^2")')
    True
    """
    try:
        tree = ast.parse(code)
        strip = {
            id(n.body[0].value)
            for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
            and n.body
            and isinstance(n.body[0], ast.Expr)
            and isinstance(n.body[0].value, ast.Constant)
            and isinstance(n.body[0].value.value, str)
        }
        lines = code.splitlines()
        for n in ast.walk(tree):
            if id(n) in strip:
                for i in range(n.lineno - 1, n.end_lineno):
                    lines[i] = ""
        code = "\n".join(re.sub(r"#.*$", "", line) for line in lines)
    except SyntaxError:
        pass
    return bool(LATEX_PATTERN.search(code))


@dataclass(frozen=True)
class Example:
    """One retrievable, renderable Manim scene."""

    id: str
    title: str
    code: str
    scene: str
    description: str = ""
    tags: tuple[str, ...] = ()
    source: str = ""
    origin: str = "curated"  # 'curated' | 'gallery' | 'api'
    needs_latex: bool = False
    extras: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def runnable_code(self) -> str:
        """The code with ``from manim import *`` guaranteed at the top."""
        if MANIM_IMPORT in self.code or "import manim" in self.code:
            return self.code
        return f"{MANIM_IMPORT}\n\n{self.code.lstrip()}"

    def summary(self) -> str:
        """One line: id, title, tags."""
        latex = " [latex]" if self.needs_latex else ""
        tags = ", ".join(self.tags[:8])
        return f"{self.id} — {self.title}{latex}  ({tags})"


# --------------------------------------------------------------------------- #
# curated examples (shipped files)
# --------------------------------------------------------------------------- #


def examples_dir() -> Path:
    """Where the shipped example files live."""
    return Path(str(files("manimkit") / "data" / "examples"))


def parse_example_file(
    path, *, origin: str = "curated", id_prefix: str = ""
) -> Example:
    """Parse one example file (header docstring + scene code) into an Example."""
    path = Path(path)
    code = path.read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(code)) or ""
    title, meta, description = _parse_header(doc)
    scenes = scene_names(code)
    scene = meta.get("scene") or (scenes[-1] if scenes else "")
    tags = tuple(t.strip() for t in meta.get("tags", "").split(",") if t.strip())
    latex = meta.get("latex")
    needs_latex = latex.lower() in {"yes", "true", "1"} if latex else uses_latex(code)
    return Example(
        id=f"{id_prefix}{path.stem}",
        title=title or path.stem.replace("_", " "),
        code=code,
        scene=scene,
        description=description,
        tags=tags,
        source=meta.get("source", ""),
        origin=origin,
        needs_latex=needs_latex,
    )


def _parse_header(doc: str) -> tuple[str, dict, str]:
    """Split a header docstring into (title, {key: value}, description)."""
    lines = doc.strip().splitlines()
    if not lines:
        return "", {}, ""
    title, rest = lines[0].strip(), lines[1:]
    meta, body_start = {}, len(rest)
    for i, line in enumerate(rest):
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() in HEADER_KEYS:
            meta[key.strip().lower()] = value.strip()
        elif line.strip() and meta:
            body_start = i
            break
    description = "\n".join(rest[body_start:]).strip()
    return title, meta, description


def curated_examples(root=None) -> Iterator[Example]:
    """Yield the shipped examples: originals, then the gallery subfolder."""
    root = Path(root) if root else examples_dir()
    for path in sorted(root.glob("*.py")):
        yield parse_example_file(path, origin="curated")
    for path in sorted((root / "gallery").glob("*.py")):
        yield parse_example_file(path, origin="gallery", id_prefix="gallery/")


def folder_examples(folder, *, origin: str = "user") -> Iterator[Example]:
    """Yield examples from any folder of scene files (header docstring optional)."""
    folder = Path(folder)
    for path in sorted(folder.rglob("*.py")):
        yield parse_example_file(path, origin=origin, id_prefix=f"{origin}/")


# --------------------------------------------------------------------------- #
# api examples (harvested from the installed manim's docstrings)
# --------------------------------------------------------------------------- #


def scene_names(code: str) -> list[str]:
    """Names of classes that look like Manim scenes, in file order.

    >>> scene_names("class A(Scene):\\n  pass\\nclass B(ThreeDScene):\\n  pass")
    ['A', 'B']
    """
    return [
        name for name, bases in SCENE_CLASS_PATTERN.findall(code) if "Scene" in bases
    ]


def parse_manim_directives(text: str) -> Iterator[dict]:
    """Yield ``{name, options, code, preamble}`` for each ``.. manim::`` block.

    ``preamble`` is the paragraph just above the directive, which in the manim
    docs is usually the one-sentence description of the example.

    >>> doc = '''A simple arc.
    ...
    ... .. manim:: ArcExample
    ...     :save_last_frame:
    ...
    ...     class ArcExample(Scene):
    ...         def construct(self):
    ...             self.add(Arc(angle=PI))
    ... '''
    >>> d = next(parse_manim_directives(doc))
    >>> d['name'], d['options'], d['preamble']
    ('ArcExample', {'save_last_frame': ''}, 'A simple arc.')
    >>> print(d['code'])
    class ArcExample(Scene):
        def construct(self):
            self.add(Arc(angle=PI))
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = DIRECTIVE_PATTERN.match(lines[i])
        if not m:
            i += 1
            continue
        indent = len(m.group("indent").expandtabs())
        name = m.group("name")
        preamble = _preceding_paragraph(lines, i)
        i += 1
        options = {}
        while i < len(lines) and lines[i].strip().startswith(":"):
            key, _, value = lines[i].strip()[1:].partition(":")
            options[key.strip()] = value.strip()
            i += 1
        body = []
        while i < len(lines):
            line = lines[i]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            body.append(line)
            i += 1
        code = _dedent(body)
        if code:
            yield {"name": name, "options": options, "code": code, "preamble": preamble}


def _preceding_paragraph(lines: list[str], i: int) -> str:
    j = i - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    para = []
    while (
        j >= 0
        and lines[j].strip()
        and not lines[j].strip().startswith(("..", ":", "---", "==="))
    ):
        para.append(lines[j].strip())
        j -= 1
    text = " ".join(reversed(para))
    return "" if text.lower() in {"examples", "example"} else text


def _dedent(body: list[str]) -> str:
    import textwrap

    return textwrap.dedent("\n".join(body)).strip("\n")


def _manim_root() -> Path | None:
    try:
        import importlib.util

        spec = importlib.util.find_spec("manim")
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.origin:
        return None
    return Path(spec.origin).parent


def manim_version() -> str | None:
    """Version of the installed manim, without importing it (importing is slow)."""
    try:
        from importlib.metadata import version

        return version("manim")
    except Exception:
        return None


@lru_cache(maxsize=4)
def api_examples(root=None) -> tuple[Example, ...]:
    """The ``.. manim::`` docstring examples of the installed manim (or ``root``)."""
    root = Path(root) if root else _manim_root()
    if root is None:
        return ()
    version = manim_version() or "?"
    out = []
    for path in sorted(root.rglob("*.py")):
        src = path.read_text(encoding="utf-8", errors="replace")
        if ".. manim::" not in src:
            continue
        module = ".".join(path.relative_to(root.parent).with_suffix("").parts)
        for owner, doc in _docstrings(src):
            for d in parse_manim_directives(doc):
                out.append(
                    _api_example(
                        d, owner=owner, module=module, doc=doc, version=version
                    )
                )
    return tuple(out)


def _docstrings(src: str) -> Iterator[tuple[str, str]]:
    """(qualified owner name, docstring) for the module, classes and functions."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                doc = ast.get_docstring(child, clean=True)
                if doc and ".. manim::" in doc:
                    yield name, doc
                yield from walk(child, f"{name}.")

    doc = ast.get_docstring(tree, clean=True)
    if doc and ".. manim::" in doc:
        yield "", doc
    yield from walk(tree, "")


def _api_example(
    d: dict, *, owner: str, module: str, doc: str, version: str
) -> Example:
    summary = (
        " ".join(doc.strip().split("\n\n")[0].split()) if doc.strip() else ""
    )  # first paragraph
    refs = " ".join(v for k, v in d["options"].items() if k.startswith("ref_")).split()
    owner_leaf = owner.split(".")[-1] if owner else module.split(".")[-1]
    tags = tuple(
        dict.fromkeys(
            [t for t in [owner, owner_leaf] if t]
            + refs
            + module.split(".")[1:]
            + (["still image"] if "save_last_frame" in d["options"] else [])
        )
    )
    where = owner or module
    title = f"{where}: {d['preamble'] or summary}".strip().rstrip(":")
    description = " ".join(x for x in [summary, d["preamble"]] if x)
    return Example(
        id=f"api/{where}/{d['name']}",
        title=title[:160],
        code=d["code"],
        scene=d["name"],
        description=description,
        tags=tags,
        source=f"manim {version} docstring of {module}.{owner}".rstrip("."),
        origin="api",
        needs_latex=uses_latex(d["code"]),
        extras={"options": d["options"]},
    )


# --------------------------------------------------------------------------- #
# the corpus
# --------------------------------------------------------------------------- #

DFLT_SOURCES = ("curated", "api")


def iter_examples(sources: Iterable = DFLT_SOURCES) -> Iterator[Example]:
    """Every example from ``sources``.

    Each source is ``'curated'``, ``'api'``, a folder path of your own scenes,
    or any iterable of :class:`Example` (the seam for other corpora).
    """
    for src in sources:
        if src == "curated":
            yield from curated_examples()
        elif src == "api":
            yield from api_examples()
        elif isinstance(src, (str, Path)):
            yield from folder_examples(src)
        else:
            yield from src


def get_example(example_id: str, *, sources: Iterable = DFLT_SOURCES) -> Example:
    """The example with this id (exact, else a unique case-insensitive suffix match)."""
    examples = list(iter_examples(sources))
    for ex in examples:
        if ex.id == example_id:
            return ex
    key = example_id.lower()
    matches = [
        ex for ex in examples if ex.id.lower().endswith(key) or ex.scene.lower() == key
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        ids = ", ".join(m.id for m in matches[:10])
        raise KeyError(f"{example_id!r} is ambiguous: {ids}")
    raise KeyError(f"No example {example_id!r}. Try `manimkit search <words>`.")
