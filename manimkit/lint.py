"""Static checks for the mistakes LLMs make most when writing ManimCE code.

Two kinds of check, both before any render:

- **rules**: a list of known wrong-API patterns (ManimGL names, pre-0.18 names,
  LaTeX-in-a-Python-string traps), each with the right replacement;
- **names**: every capitalised name the file uses but does not define is looked up
  in the *installed* manim; a miss is reported with close matches. This catches
  hallucinated classes and colour constants that no rule list anticipates.

>>> issues = lint_code("from manim import *\\nclass S(Scene):\\n"
...                    "    def construct(self):\\n"
...                    "        self.play(ShowCreation(Circle()))\\n", check_names=False)
>>> issues[0].message
'`ShowCreation` is ManimGL / pre-0.10 — ManimCE uses `Create(mob)`.'
"""

from __future__ import annotations

import ast
import builtins
import difflib
import re
from dataclasses import dataclass
from pathlib import Path

# (pattern, message). Order matters only for readability.
RULES: list[tuple[str, str]] = [
    (r"^\s*(from|import)\s+manimlib\b", "`manimlib` is ManimGL (3b1b). ManimCE is `from manim import *`."),
    (r"\bShowCreation\b", "`ShowCreation` is ManimGL / pre-0.10 — ManimCE uses `Create(mob)`."),
    (r"\bTextMobject\b", "`TextMobject` is gone — use `Text(...)` (plain) or `Tex(...)` (LaTeX text)."),
    (r"\bTexMobject\b", "`TexMobject` is gone — use `MathTex(r'...')`."),
    (r"\bTexText\b", "`TexText` is ManimGL — use `Tex(...)` in ManimCE."),
    (r"^\s*CONFIG\s*=\s*\{", "`CONFIG = {...}` class dicts are ManimGL/old style — pass keyword arguments to `__init__` / constructors."),
    (r"\bGraphScene\b", "`GraphScene` was removed — use `Axes(...)` and `axes.plot(f)` in a plain `Scene`."),
    (r"\.get_graph\(", "`get_graph` is the old GraphScene API — use `axes.plot(lambda x: ..., x_range=[a, b])`."),
    (r"\bFadeInFrom(Down|Large|Point)?\b", "`FadeInFrom*` is gone — use `FadeIn(mob, shift=DOWN)` / `FadeIn(mob, scale=1.5)`."),
    (r"\bFadeOutAndShift\w*\b", "`FadeOutAndShift` is gone — use `FadeOut(mob, shift=UP)`."),
    (r"\bApplyMethod\b", "`ApplyMethod` is deprecated — use `mob.animate.method(...)`."),
    (r"\bShowCreationThenDestruction\b", "Use `ShowPassingFlash(mob.copy())` or `Create` then `Uncreate` in ManimCE."),
    (r"\bInteractiveScene\b|\bself\.embed\(\)", "`InteractiveScene` / `self.embed()` are ManimGL-only."),
    (r"\bCode\(\s*code\s*=", "Since manim 0.19, `Code` takes `code_string=` (or `code_file=`), not `code=`."),
    (r"\binsert_line_no\s*=", "`insert_line_no` was renamed `add_line_numbers` (manim 0.19)."),
    (r"\bget_x_axis_label\(\s*['\"]", "Axis labels are LaTeX by default; pass `MathTex`/`Text` or a raw string: `axes.get_x_axis_label(Text('t'))`."),
    (r"\b(MathTex|Tex)\(\s*(?![rR])[\"'][^\"'\n]*\\(?![\\n])[a-zA-Z]",
     "LaTeX in a non-raw string: `\\f`, `\\t`, `\\b` ... become control characters. Use a raw string `r'...'`."),
    (r"\bTex\(\s*r?[\"'][^\"'\n]*\\(frac|sqrt|sum|int|cdot|alpha|beta|theta|pi|lim|infty)\b(?![^\"'\n]*\$)",
     "`Tex` is LaTeX *text* mode: math commands like `\\frac` need `MathTex(...)` (or `$...$` inside `Tex`)."),
    (r"\bMathTex\(\s*r?[\"']\$", "`MathTex` is already in math mode — drop the `$...$`."),
    (r"\.to_corner\(\s*\)", "`to_corner()` with no argument goes to DL (bottom-left); pass UL/UR/DL/DR explicitly."),
]

TEXT_NAMES = frozenset({"Text", "MarkupText", "Paragraph"})


@dataclass(frozen=True)
class LintIssue:
    """One finding: where, what, and (usually) the fix."""

    line: int
    message: str
    kind: str = "rule"  # 'rule' | 'name' | 'structure'

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}" if self.line else self.message


def lint_code(code: str, *, check_names: bool = True) -> list[LintIssue]:
    """Lint Manim source code. ``check_names`` imports manim (about a second)."""
    issues = []
    lines = code.splitlines()
    for pattern, message in RULES:
        rx = re.compile(pattern)
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                continue
            if rx.search(line):
                issues.append(LintIssue(i, message))
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [LintIssue(e.lineno or 0, f"SyntaxError: {e.msg}", "structure")] + issues
    issues += _structure_issues(code, tree)
    if check_names:
        issues += _undefined_manim_names(tree)
    return sorted(set(issues), key=lambda x: (x.line, x.message))


def lint_scene(path) -> list[LintIssue]:
    """Lint a scene file."""
    return lint_code(Path(path).read_text(encoding="utf-8"))


def _structure_issues(code: str, tree: ast.Module) -> list[LintIssue]:
    out = []
    uses_star = any(
        isinstance(n, ast.ImportFrom) and n.module == "manim" and any(a.name == "*" for a in n.names)
        for n in tree.body
    )
    imports_manim = uses_star or any(
        isinstance(n, (ast.Import, ast.ImportFrom))
        and ("manim" == getattr(n, "module", None) or any(a.name == "manim" for a in getattr(n, "names", [])))
        for n in ast.walk(tree)
    )
    if not imports_manim:
        out.append(LintIssue(1, "No `from manim import *` — every ManimCE scene file needs it.", "structure"))
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    scenes = [c for c in classes if any("Scene" in ast.unparse(b) for b in c.bases)]
    if not scenes:
        out.append(LintIssue(1, "No Scene subclass found (class X(Scene): def construct(self): ...).", "structure"))
    for c in scenes:
        if not any(isinstance(f, ast.FunctionDef) and f.name == "construct" for f in c.body):
            if not any(isinstance(b, ast.Name) and b.id in {c2.name for c2 in scenes} for b in c.bases):
                out.append(LintIssue(c.lineno, f"Scene `{c.name}` has no `construct(self)` method.", "structure"))
    return out


def _undefined_manim_names(tree: ast.Module) -> list[LintIssue]:
    """Capitalised names used but defined neither here, in builtins, nor in manim."""
    try:
        import manim
    except Exception:
        return []
    defined = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            defined.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                defined.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
    manim_names = set(dir(manim))
    seen, out = set(), []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)):
            continue
        name = node.id
        if name in seen or name in defined or name in manim_names or not name[:1].isupper():
            continue
        seen.add(name)
        close = difflib.get_close_matches(name, manim_names, n=3, cutoff=0.6)
        hint = f" Did you mean: {', '.join(close)}?" if close else ""
        out.append(
            LintIssue(
                node.lineno,
                f"`{name}` is not defined by manim {getattr(manim, '__version__', '')} "
                f"(nor in this file).{hint}",
                "name",
            )
        )
    return out
