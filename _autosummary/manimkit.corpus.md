# manimkit.corpus

The example corpus: working ManimCE scenes an agent can retrieve and adapt.

Two sources feed it, both yielding [`Example`](#manimkit.corpus.Example) records:

- **curated** — scenes shipped in `manimkit/data/examples/` (original ones, plus
  the Manim Community example gallery, MIT, with attribution). Each file starts
  with a small header docstring:
  ```default
  '''Bar chart that grows, then re-sorts.

  tags: data, bar chart, BarChart, story
  scene: BarChartStory
  source: original (manimkit, MIT)

  Free-text description, as long as useful.
  '''
  ```
- **api** — the `.. manim::` examples embedded in the docstrings of the
  *installed* manim package, harvested on demand. They are version-matched to the
  manim you actually have, which is the cheapest defence against an agent writing
  code for an API that has since moved.

```pycon
>>> ex = next(iter(curated_examples()))
>>> isinstance(ex, Example) and ex.origin in {"curated", "gallery"}
True
```

### Functions

| [`api_examples`](#manimkit.corpus.api_examples)([root])                              | The <br/><br/>```<br/>``<br/>```<br/><br/>.                                              |
|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| [`curated_examples`](#manimkit.corpus.curated_examples)([root])                          | Yield the shipped examples: originals, then the gallery subfolder.                       |
| [`examples_dir`](#manimkit.corpus.examples_dir)()                                    | Where the shipped example files live.                                                    |
| [`folder_examples`](#manimkit.corpus.folder_examples)(folder, \*[, origin])             | Yield examples from any folder of scene files (header docstring optional).               |
| [`get_example`](#manimkit.corpus.get_example)(example_id, \*[, sources])            | The example with this id (exact, else a unique case-insensitive suffix match).           |
| [`iter_examples`](#manimkit.corpus.iter_examples)([sources])                          | Every example from `sources`.                                                            |
| [`manim_version`](#manimkit.corpus.manim_version)()                                   | Version of the installed manim, without importing it (importing is slow).                |
| [`parse_example_file`](#manimkit.corpus.parse_example_file)(path, \*[, origin, id_prefix]) | Parse one example file (header docstring + scene code) into an Example.                  |
| [`parse_manim_directives`](#manimkit.corpus.parse_manim_directives)(text)                      | Yield `{name, options, code, preamble}` for each <br/><br/>```<br/>``<br/>```<br/><br/>. |
| [`scene_names`](#manimkit.corpus.scene_names)(code)                                 | Names of classes that look like Manim scenes, in file order.                             |
| [`uses_latex`](#manimkit.corpus.uses_latex)(code)                                  | Whether code (docstrings and comments ignored) uses something that needs LaTeX.          |

### Classes

| [`Example`](#manimkit.corpus.Example)(id, title, code, scene[, ...])   | One retrievable, renderable Manim scene.   |
|-------------------------------------------------------------------------------------------|--------------------------------------------|

### *class* manimkit.corpus.Example(id, title, code, scene, description='', tags=(), source='', origin='curated', needs_latex=False, extras=<factory>)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

One retrievable, renderable Manim scene.

#### *property* runnable_code *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

The code with `from manim import *` guaranteed at the top.

#### summary()

One line: id, title, tags.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### manimkit.corpus.api_examples(root=None)

The `.. manim::` docstring examples of the installed manim (or `root`).

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`Example`](#manimkit.corpus.Example), [`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis)]

### manimkit.corpus.curated_examples(root=None)

Yield the shipped examples: originals, then the gallery subfolder.

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`Example`](#manimkit.corpus.Example)]

### manimkit.corpus.examples_dir()

Where the shipped example files live.

* **Return type:**
  [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)

### manimkit.corpus.folder_examples(folder, , origin='user')

Yield examples from any folder of scene files (header docstring optional).

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`Example`](#manimkit.corpus.Example)]

### manimkit.corpus.get_example(example_id, , sources=('curated', 'api'))

The example with this id (exact, else a unique case-insensitive suffix match).

* **Return type:**
  [`Example`](#manimkit.corpus.Example)

### manimkit.corpus.iter_examples(sources=('curated', 'api'))

Every example from `sources`.

Each source is `'curated'`, `'api'`, a folder path of your own scenes,
or any iterable of [`Example`](#manimkit.corpus.Example) (the seam for other corpora).

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`Example`](#manimkit.corpus.Example)]

### manimkit.corpus.manim_version()

Version of the installed manim, without importing it (importing is slow).

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### manimkit.corpus.parse_example_file(path, , origin='curated', id_prefix='')

Parse one example file (header docstring + scene code) into an Example.

* **Return type:**
  [`Example`](#manimkit.corpus.Example)

### manimkit.corpus.parse_manim_directives(text)

Yield `{name, options, code, preamble}` for each `.. manim::` block.

`preamble` is the paragraph just above the directive, which in the manim
docs is usually the one-sentence description of the example.

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/typing.html#typing.Iterator)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]

```pycon
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
```

### manimkit.corpus.scene_names(code)

Names of classes that look like Manim scenes, in file order.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

```pycon
>>> scene_names("class A(Scene):\n  pass\nclass B(ThreeDScene):\n  pass")
['A', 'B']
```

### manimkit.corpus.uses_latex(code)

Whether code (docstrings and comments ignored) uses something that needs LaTeX.

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

```pycon
>>> uses_latex("'''Unlike BarChart, no LaTeX.'''\nText('hi')  # not MathTex")
False
>>> uses_latex('MathTex(r"x^2")')
True
```
