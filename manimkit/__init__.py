"""manimkit — make Manim (Community Edition) animations with an AI agent.

Three things an agent needs, as plain functions (and a ``manimkit`` CLI):

- **find a working example** close to what it has to draw:
  :func:`search_examples` / :func:`get_example` over a curated corpus plus the
  docstring examples of the installed manim;
- **catch the classic mistakes before rendering**: :func:`lint_scene` (ManimGL
  names, removed APIs, LaTeX-string traps, names manim does not define);
- **render and look**: :func:`render_check` renders at low quality, samples frames
  into one contact sheet, and reports duration, timeline, layout warnings
  (cut-off text, overlaps) and concise errors.

Plus :func:`check_requirements` for manim / LaTeX, and the agent skill shipped in
``manimkit/data/skills/manimkit/`` (see :func:`skills_dir`).

>>> hits = search_examples("bar chart", k=2, sources=["curated"])
>>> all(isinstance(h.example, Example) for h in hits)
True
"""

from importlib.resources import files as _files
from pathlib import Path as _Path

from manimkit.corpus import (
    Example,
    api_examples,
    curated_examples,
    get_example,
    iter_examples,
)
from manimkit.lint import LintIssue, lint_code, lint_scene
from manimkit.render import RenderReport, render_check
from manimkit.requirements import check_requirements, requirements_report
from manimkit.search import Hit, search_examples


def skills_dir() -> _Path:
    """The folder holding the agent skills this package ships."""
    return _Path(str(_files("manimkit") / "data" / "skills"))


__all__ = [
    "Example",
    "Hit",
    "LintIssue",
    "RenderReport",
    "api_examples",
    "check_requirements",
    "curated_examples",
    "get_example",
    "iter_examples",
    "lint_code",
    "lint_scene",
    "render_check",
    "requirements_report",
    "search_examples",
    "skills_dir",
]
