# manimkit

manimkit — make Manim (Community Edition) animations with an AI agent.

Three things an agent needs, as plain functions (and a `manimkit` CLI):

- **find a working example** close to what it has to draw:
  [`search_examples()`](#manimkit.search_examples) / [`get_example()`](#manimkit.get_example) over a curated corpus plus the
  > docstring examples of the installed manim;
- **catch the classic mistakes before rendering**: [`lint_scene()`](#manimkit.lint_scene) (ManimGL
  names, removed APIs, LaTeX-string traps, names manim does not define);
- **render and look**: [`render_check()`](#manimkit.render_check) renders at low quality, samples frames
  into one contact sheet, and reports duration, timeline, layout warnings
  (cut-off text, overlaps) and concise errors.

Plus [`check_requirements()`](#manimkit.check_requirements) for manim / LaTeX, and the agent skill shipped in
`manimkit/data/skills/manimkit/` (see [`skills_dir()`](#manimkit.skills_dir)).

```pycon
>>> hits = search_examples("bar chart", k=2, sources=["curated"])
>>> all(isinstance(h.example, Example) for h in hits)
True
```

### Functions

| [`api_examples`](#manimkit.api_examples)([root])                              | The <br/><br/>```<br/>``<br/>```<br/><br/>.                                                                          |
|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| [`check_requirements`](#manimkit.check_requirements)()                              | Check manim, LaTeX and dvisvgm; never installs anything.                                                             |
| [`curated_examples`](#manimkit.curated_examples)([root])                          | Yield the shipped examples: originals, then the gallery subfolder.                                                   |
| [`get_example`](#manimkit.get_example)(example_id, \*[, sources])            | The example with this id (exact, else a unique case-insensitive suffix match).                                       |
| [`iter_examples`](#manimkit.iter_examples)([sources])                          | Every example from `sources`.                                                                                        |
| [`lint_code`](#manimkit.lint_code)(code, \*[, check_names])                | Lint Manim source code.                                                                                              |
| [`lint_scene`](#manimkit.lint_scene)(path)                                  | Lint a scene file.                                                                                                   |
| [`render_check`](#manimkit.render_check)(file[, scene, quality, ...])         | Lint, render `scene` from `file`, sample frames, report.                                                             |
| [`requirements_report`](#manimkit.requirements_report)()                             | Human-readable [`check_requirements()`](#manimkit.check_requirements), plus what to do without LaTeX. |
| [`search_examples`](#manimkit.search_examples)(query[, k, sources, origin, ...]) | The `k` examples most relevant to `query`, best first.                                                               |
| [`skills_dir`](#manimkit.skills_dir)()                                      | The folder holding the agent skills this package ships.                                                              |

### Classes

| [`Example`](#manimkit.Example)(id, title, code, scene[, ...])      | One retrievable, renderable Manim scene.         |
|----------------------------------------------------------------------------------------------|--------------------------------------------------|
| [`Hit`](#manimkit.Hit)(example, score)                         | A search result: the example and its score.      |
| [`LintIssue`](#manimkit.LintIssue)(line, message[, kind])            | One finding: where, what, and (usually) the fix. |
| [`RenderReport`](#manimkit.RenderReport)(ok, file[, scene, video, ...]) | What happened when a scene was rendered.         |

### *class* manimkit.Example(id, title, code, scene, description='', tags=(), source='', origin='curated', needs_latex=False, extras=<factory>)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

One retrievable, renderable Manim scene.

#### *property* runnable_code *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

The code with `from manim import *` guaranteed at the top.

#### summary()

One line: id, title, tags.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### *class* manimkit.Hit(example, score)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A search result: the example and its score.

### *class* manimkit.LintIssue(line, message, kind='rule')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

One finding: where, what, and (usually) the fix.

### *class* manimkit.RenderReport(ok, file, scene=None, video=None, image=None, contact_sheet=None, frames=<factory>, duration=None, scene_time=None, timeline=<factory>, layout_warnings=<factory>, lint=<factory>, error=None, error_kind=None, user_frames=<factory>, raised_in=None, latex_log=None, hint=None, stderr_tail=None, source_hash=None, unchanged=False, reads=None)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

What happened when a scene was rendered.

#### reads *: [list](https://docs.python.org/3/builtins/stdtypes.html#list) | [None](https://docs.python.org/3/builtins/constants.html#None)* *= None*

every file the render opened for reading and
every folder it listed, outside the Python installation and `out_dir`
(`[{"path", "kind"}]`, `kind` `"file"` or `"dir"`); `None` when
not recorded, or when the render died before reporting.

* **Type:**
  With `record_reads=True`

### manimkit.api_examples(root=None)

The `.. manim::` docstring examples of the installed manim (or `root`).

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`Example`](manimkit.corpus.html.md#manimkit.corpus.Example), [`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis)]

### manimkit.check_requirements()

Check manim, LaTeX and dvisvgm; never installs anything.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`Requirement`](manimkit.requirements.html.md#manimkit.requirements.Requirement)]

### manimkit.curated_examples(root=None)

Yield the shipped examples: originals, then the gallery subfolder.

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`Example`](manimkit.corpus.html.md#manimkit.corpus.Example)]

### manimkit.get_example(example_id, , sources=('curated', 'api'))

The example with this id (exact, else a unique case-insensitive suffix match).

* **Return type:**
  [`Example`](manimkit.corpus.html.md#manimkit.corpus.Example)

### manimkit.iter_examples(sources=('curated', 'api'))

Every example from `sources`.

Each source is `'curated'`, `'api'`, a folder path of your own scenes,
or any iterable of [`Example`](#manimkit.Example) (the seam for other corpora).

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`Example`](manimkit.corpus.html.md#manimkit.corpus.Example)]

### manimkit.lint_code(code, , check_names=True)

Lint Manim source code. `check_names` imports manim (about a second).

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`LintIssue`](manimkit.lint.html.md#manimkit.lint.LintIssue)]

### manimkit.lint_scene(path)

Lint a scene file.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`LintIssue`](manimkit.lint.html.md#manimkit.lint.LintIssue)]

### manimkit.render_check(file, scene=None, , quality='l', n_frames=8, at=(), out_dir=None, probe=True, no_latex=False, lint=True, timeout=600, python=None, record_reads=False)

Lint, render `scene` from `file`, sample frames, report.

* **Parameters:**
  * **quality** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – `l` (480p15, the iteration default), `m`, `h`, `p`, `k`.
  * **n_frames** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – how many frames to sample: taken just before animations end
    (settled states), spread over the timeline; evenly spaced if the probe is
    off. The final frame is always added.
  * **at** ([`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)) – extra timestamps (seconds) to sample, e.g. where a warning points.
  * **out_dir** – where media, frames and the contact sheet go
    (default: `manimkit_renders/<file stem>/` next to the file).
  * **probe** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – record the timeline and check layout after every play/wait.
  * **no_latex** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – fail on the first use of LaTeX, for scenes that must run on a
    machine without a TeX install (this one may well have it).
  * **python** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – interpreter to render with (default: this one).
  * **record_reads** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – 

    record every file the render opens for reading and
    every folder it lists — whatever built the path — in
    [`RenderReport.reads`](#manimkit.RenderReport.reads) ([`manimkit.reads.ReadRecorder`](manimkit.reads.html.md#manimkit.reads.ReadRecorder)), so a
    > caller that caches renders can key the files a scene reads by a
    > computed path.
* **Return type:**
  [`RenderReport`](manimkit.render.html.md#manimkit.render.RenderReport)

### manimkit.requirements_report()

Human-readable [`check_requirements()`](#manimkit.check_requirements), plus what to do without LaTeX.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### manimkit.search_examples(query, k=5, \*, sources=('curated', 'api'), origin=None, latex=None, scorer=<function bm25_scores>, origin_weights=None)

The `k` examples most relevant to `query`, best first.

* **Parameters:**
  * **origin** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`None`](https://docs.python.org/3/builtins/constants.html#None)]) – keep only these origins (`'curated'`, `'gallery'`, `'api'`).
  * **latex** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – `False` drops examples that need a LaTeX install; `True`
    keeps only those; `None` keeps all.
  * **scorer** ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)[[[`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]], [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`float`](https://docs.python.org/3/builtins/functions.html#float)]]) – the ranking function (the seam for embedding retrieval).
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`Hit`](manimkit.search.html.md#manimkit.search.Hit)]

### manimkit.skills_dir()

The folder holding the agent skills this package ships.

* **Return type:**
  [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)

### Modules

| [`corpus`](manimkit.corpus.html.md#module-manimkit.corpus)             | The example corpus: working ManimCE scenes an agent can retrieve and adapt.   |
|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| [`lint`](manimkit.lint.html.md#module-manimkit.lint)                 | Static checks for the mistakes LLMs make most when writing ManimCE code.      |
| [`reads`](manimkit.reads.html.md#module-manimkit.reads)               | What a render read: the files and folders a scene opens, recorded as it runs. |
| [`render`](manimkit.render.html.md#module-manimkit.render)             | Render a scene, look at it, and say concisely what went wrong.                |
| [`requirements`](manimkit.requirements.html.md#module-manimkit.requirements) | What rendering needs, whether you have it, and how to get what is missing.    |
| [`search`](manimkit.search.html.md#module-manimkit.search)             | Retrieval over the example corpus.                                            |
| [`tools`](manimkit.tools.html.md#module-manimkit.tools)               | CLI-shaped wrappers: each returns the text an agent (or a human) reads.       |
