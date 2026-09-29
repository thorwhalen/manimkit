"""CLI-shaped wrappers: each returns the text an agent (or a human) reads.

The business logic lives in the other modules and returns data; these functions
only format it. ``manimkit/__main__.py`` dispatches this SSOT list with ``cw``.
"""

from __future__ import annotations

from manimkit.corpus import get_example, iter_examples
from manimkit.lint import lint_scene
from manimkit.render import render_check
from manimkit.requirements import requirements_report
from manimkit.search import search_examples


def search(query: str, *, k: int = 5, code: bool = False, no_latex: bool = False, origin: str = ""):
    """Find corpus examples for QUERY (plain words: 'bar chart race', 'move dot along curve').

    --code prints each hit's full source; --no-latex skips examples that need LaTeX;
    --origin curated|gallery|api restricts the source.
    """
    hits = search_examples(
        query, k, latex=False if no_latex else None, origin=origin or None
    )
    if not hits:
        return "No match. Try other words (a Manim class name also works: 'ValueTracker')."
    out = [str(h) for h in hits]
    if code:
        for h in hits:
            out += ["", f"# ===== {h.example.id} — scene {h.example.scene} =====", h.example.runnable_code]
    else:
        out.append("\n(show one with: manimkit show <id>)")
    return "\n".join(out)


def show(example_id: str):
    """Print an example's metadata and full, runnable source."""
    ex = get_example(example_id)
    head = [
        f"# id: {ex.id}",
        f"# title: {ex.title}",
        f"# scene: {ex.scene}   needs LaTeX: {'yes' if ex.needs_latex else 'no'}",
        f"# tags: {', '.join(ex.tags)}",
        f"# source: {ex.source}",
    ]
    return "\n".join(head) + "\n\n" + ex.runnable_code


def list_examples(*, origin: str = "curated"):
    """List example ids and titles (origin: curated, gallery, api, or all)."""
    exs = [e for e in iter_examples() if origin == "all" or e.origin == origin]
    return "\n".join(e.summary() for e in exs) + f"\n({len(exs)} examples)"


def lint(file: str):
    """Static checks for common ManimCE mistakes (ManimGL names, removed APIs, LaTeX traps)."""
    issues = lint_scene(file)
    return "\n".join(str(i) for i in issues) if issues else "lint: clean"


def render(file: str, scene: str = "", *, quality: str = "l", frames: int = 8, at: str = "", out_dir: str = "", no_latex: bool = False):
    """Render SCENE from FILE (low quality by default), sample frames into a contact sheet, report.

    --quality l|m|h|p|k (480p15, 720p30, 1080p60, 1440p60, 2160p60). --at 1.5,4 adds
    frames at those seconds. --no-latex fails on any use of LaTeX (for machines without
    TeX). Each run overwrites the previous frames and contact sheet.
    Exit code 1 if the render failed.
    """
    times = tuple(float(x) for x in at.split(",") if x.strip())
    report = render_check(
        file, scene or None, quality=quality, n_frames=frames, at=times,
        out_dir=out_dir or None, no_latex=no_latex,
    )
    print(report)
    if not report.ok:
        raise SystemExit(1)


def check():
    """Report whether manim, LaTeX and dvisvgm are available, and how to install what is missing."""
    return requirements_report()


def skill_path():
    """Print the folder of the agent skills shipped with manimkit (to link into ~/.claude/skills)."""
    from manimkit import skills_dir

    return str(skills_dir())


_dispatch_funcs = [search, show, list_examples, lint, render, check, skill_path]
