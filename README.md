# manimkit

Make [Manim](https://www.manim.community/) (Community Edition) animations with an AI agent: an agent skill, a searchable corpus of working scenes, a linter for the classic LLM mistakes, and a render-and-look loop.

```bash
pip install manimkit            # plus `pip install manim` (or manimkit[render]) to render
manimkit check                  # manim / LaTeX / dvisvgm present? how to install what isn't
manimkit search "bar chart that re-sorts"      # find a working example to adapt
manimkit show bar_chart_story                  # its full, runnable source
manimkit lint scene.py                         # ManimGL names, removed APIs, LaTeX traps
manimkit render scene.py MyScene               # render -ql, sample frames, report
```

Then tell your agent "make me a 10-second manim animation explaining X". The shipped skill (`manimkit/data/skills/manimkit/SKILL.md`) teaches it the loop: plan a storyboard, retrieve examples, write the scene, lint, render, **look at the contact sheet**, fix, final render.

## Why

LLMs write Manim well enough to be dangerous. The recurring failures are: ManimGL or pre-0.18 API names (`ShowCreation`, `TextMobject`, `GraphScene`, `Code(code=...)`), LaTeX strings that are not raw strings, text running off the frame, labels on top of each other, and videos of the wrong length. Published agent systems for this (TheoremExplainAgent, Manimator, PhysicsSolutionAgent) converge on the same remedies: plan first, retrieve working code, and feed rendered frames back to the model. manimkit packages those remedies as plain functions and a CLI, so any agent host can use them.

## What is in the box

- **A corpus** of retrievable scenes: 21 original, curated full scenes (data stories, line and bar and pie charts, flowcharts, cycle and sequence diagrams, array algorithms, equation derivations, linear transformations, calculus with trackers, visual proofs, graph traversal, sorting, timelines, code walkthroughs, neural-net diagrams, vectors, camera zooms), the 27 scenes of the official ManimCE example gallery (MIT, with attribution), and every `.. manim::` example in the docstrings of **your installed manim** (about 400 in manim 0.20), harvested on the fly so their API always matches the version you render with. Every shipped scene is rendered in the repo's verification run.
- **Search** (`search_examples`, `manimkit search`): dependency-free BM25 over titles, tags, descriptions and the Manim identifiers each scene uses, with `--no-latex` to keep only scenes that render without a TeX install. `scorer=` is the seam for embedding retrieval.
- **Lint** (`lint_scene`, `manimkit lint`): known wrong-API patterns with the right replacement, plus every capitalised name your file uses that the installed manim does not define, with close matches (`LIGHT_BLUE` -> did you mean `LIGHT_BROWN`, `BLUE`...).
- **Render and inspect** (`render_check`, `manimkit render`): renders in a child process, records a timeline of every `play`/`wait` with start and end seconds, checks the layout after each (text cut off at the frame edge, text overlapping text, text crossed by a shape's outline, shapes partly off-screen), samples frames into one contact-sheet PNG, and reports errors as the exception plus the lines of *your* file that led to it, a hint for known failure signatures, and the LaTeX log's error lines for LaTeX failures. `--no-latex` makes any use of LaTeX fail, for scenes that must run on a machine without TeX.

## Python API

```python
from manimkit import search_examples, get_example, lint_scene, render_check

for hit in search_examples("move a dot along a curve", k=3, latex=False):
    print(hit)
print(get_example("flowchart_process").runnable_code)

report = render_check("scene.py", "MyScene", quality="l", n_frames=6)
print(report)                 # duration, timeline, layout warnings, contact sheet path
report.ok, report.contact_sheet, report.layout_warnings
```

Your own scenes can join the corpus: `search_examples(query, sources=["curated", "api", "/path/to/my/scenes"])`. A header docstring (first line = title, then `tags:`, `scene:`, `source:` lines, then a description) makes them rank well; without one the file name and code identifiers are still indexed.

## Installing the agent skill

The skill ships inside the package (`manimkit skill-path` prints where). For Claude Code, link it into your skills folder:

```bash
ln -s "$(manimkit skill-path)/manimkit" ~/.claude/skills/manimkit
```

or, with the GitHub CLI, `gh skill install thorwhalen/manimkit manimkit`.

## System requirements

Rendering needs the `manim` package (Cairo and Pango come with its wheels on macOS and Windows; on Linux install `libcairo2-dev libpango1.0-dev` first) and, for `MathTex`/`Tex`/numbered axes, a LaTeX distribution with `dvisvgm`. `manimkit check` tells you what is missing and the command to install it on your platform. See the [Manim installation guide](https://docs.manim.community/en/stable/installation.html).

## Licence

MIT. The gallery scenes in `manimkit/data/examples/gallery/` are from the Manim Community documentation, MIT, (c) the Manim Community Developers; see the `NOTICE.md` there.
