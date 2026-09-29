"""Tests for the corpus, retrieval, lint, requirements and (when manim is installed) rendering."""

import importlib.util
import textwrap

import pytest

from manimkit import (
    check_requirements,
    curated_examples,
    get_example,
    lint_code,
    search_examples,
)
from manimkit.corpus import api_examples, scene_names
from manimkit.render import resolve_scene

HAS_MANIM = importlib.util.find_spec("manim") is not None
needs_manim = pytest.mark.skipif(not HAS_MANIM, reason="manim not installed")


# --- corpus ---------------------------------------------------------------- #


def test_curated_examples_are_complete_and_unique():
    exs = list(curated_examples())
    assert len(exs) >= 40
    ids = [e.id for e in exs]
    assert len(ids) == len(set(ids))
    for e in exs:
        assert e.title and e.tags and e.source, e.id
        assert e.scene in scene_names(e.code), e.id
        assert "from manim import *" in e.code, e.id


def test_latex_hint_ignores_docstrings():
    ex = get_example("bar_chart_story")
    assert "BarChart" in ex.code  # mentioned in its docstring...
    assert not ex.needs_latex  # ...but not used
    assert get_example("equation_derivation").needs_latex


def test_api_examples_harvested_from_a_package_tree(tmp_path):
    pkg = tmp_path / "fakemanim"
    pkg.mkdir()
    (pkg / "shapes.py").write_text(
        textwrap.dedent(
            '''
            class Blob:
                """A blob.

                A small blob.

                .. manim:: BlobExample
                    :save_last_frame:

                    class BlobExample(Scene):
                        def construct(self):
                            self.add(Circle())
                """
            '''
        )
    )
    exs = api_examples(pkg)
    assert [e.id for e in exs] == ["api/Blob/BlobExample"]
    assert exs[0].scene == "BlobExample"
    assert "still image" in exs[0].tags
    assert exs[0].runnable_code.startswith("from manim import *")


def test_get_example_suffix_and_errors():
    assert get_example("pie_chart").id == "pie_chart"
    assert get_example("moving_angle").id == "gallery/moving_angle"
    with pytest.raises(KeyError):
        get_example("no_such_example_xyz")


# --- search ---------------------------------------------------------------- #


@pytest.mark.parametrize(
    "query, expected",
    [
        ("bar chart story", "bar_chart_story"),
        ("flowchart of a process with arrows", "flowchart_process"),
        ("pie chart with percentages", "pie_chart"),
        ("sorting algorithm", "bubble_sort_bars"),
        ("derivative slope tangent", "tangent_line_derivative"),
        ("timeline of historical events", "timeline_events"),
        ("breadth first search on a graph", "graph_traversal"),
    ],
)
def test_search_finds_the_obvious_example(query, expected):
    hits = search_examples(query, k=3, sources=["curated"])
    assert hits and hits[0].example.id == expected


def test_search_latex_filter():
    hits = search_examples("chart", k=20, sources=["curated"], latex=False)
    assert hits and all(not h.example.needs_latex for h in hits)


def test_search_scorer_seam():
    hits = search_examples("anything", k=2, sources=["curated"], scorer=lambda q, docs: [1.0] * len(docs))
    assert len(hits) == 2


# --- lint ------------------------------------------------------------------ #

SCENE = "from manim import *\nclass S(Scene):\n    def construct(self):\n{body}\n"


@pytest.mark.parametrize(
    "body, needle",
    [
        ("        self.play(ShowCreation(Circle()))", "Create"),
        ('        self.add(MathTex("\\frac{a}{b}"))', "raw string"),
        ('        self.add(Tex(r"\\frac{a}{b}"))', "MathTex"),
        ('        self.add(Code(code="x = 1"))', "code_string"),
        ("        self.play(FadeInFromDown(Circle()))", "shift"),
    ],
)
def test_lint_rules(body, needle):
    issues = lint_code(SCENE.format(body=body), check_names=False)
    assert any(needle in i.message for i in issues), issues


def test_lint_clean_and_structure():
    assert lint_code(SCENE.format(body="        self.play(Create(Circle()))"), check_names=False) == []
    issues = lint_code("from manimlib import *\n", check_names=False)
    msgs = " ".join(i.message for i in issues)
    assert "ManimGL" in msgs and "No Scene subclass" in msgs


@needs_manim
def test_lint_undefined_manim_names():
    issues = lint_code(SCENE.format(body="        self.add(Circle(color=LIGHT_BLU))"))
    assert any("LIGHT_BLU" in i.message and i.kind == "name" for i in issues)


# --- requirements & render --------------------------------------------------- #


def test_check_requirements_shape():
    reqs = {r.name: r for r in check_requirements()}
    assert {"manim", "latex", "dvisvgm"} <= set(reqs)
    assert all(r.fix for r in reqs.values() if not r.ok)


def test_resolve_scene(tmp_path):
    f = tmp_path / "two.py"
    f.write_text(SCENE.format(body="        pass") + "class T(Scene):\n    pass\n")
    with pytest.raises(ValueError, match="several scenes"):
        resolve_scene(f)
    assert resolve_scene(f, "T") == "T"


@needs_manim
def test_render_check_reports_layout_and_errors(tmp_path):
    from manimkit import render_check

    f = tmp_path / "probe_me.py"
    f.write_text(
        SCENE.format(
            body=textwrap.indent(
                textwrap.dedent(
                    """
                    t = Text("far too far right", font_size=36).move_to(RIGHT * 6.5)
                    a = Text("overlap A", font_size=36)
                    b = Text("overlap B", font_size=36).shift(RIGHT * 0.3)
                    c = Text("cramped C", font_size=30).next_to(a, DOWN, buff=0.02)
                    self.play(FadeIn(t), FadeIn(a), FadeIn(b), FadeIn(c), run_time=0.5)
                    self.wait(0.5)
                    """
                ),
                " " * 8,
            )
        )
    )
    r = render_check(f, n_frames=2, out_dir=tmp_path / "out")
    assert r.ok, str(r)
    assert abs(r.duration - 1.0) < 0.1
    kinds = {w["kind"] for w in r.layout_warnings}
    assert {"cut-off", "overlap", "cramped"} <= kinds, r.layout_warnings
    assert r.contact_sheet and r.frames

    bad = tmp_path / "broken.py"
    bad.write_text(SCENE.format(body="        self.play(Create(Circle(radius=undefined_name)))"))
    r = render_check(bad, out_dir=tmp_path / "out2")
    assert not r.ok
    assert "NameError" in r.error
    assert any("undefined_name" in u for u in r.user_frames)
