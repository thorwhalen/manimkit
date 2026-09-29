"""What rendering needs, whether you have it, and how to get what is missing.

``manimkit`` itself is pure Python. Rendering needs the ``manim`` package (which
brings Cairo, Pango and PyAV) and, for any ``MathTex``/``Tex``/numbered axis, a LaTeX
install with ``dvisvgm``. :func:`check_requirements` reports each one with the
command that fixes it on this platform.

>>> reqs = check_requirements()
>>> {r.name for r in reqs} >= {'manim', 'latex', 'dvisvgm'}
True
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass

LATEX_FIX = {
    "darwin": "brew install --cask basictex && sudo tlmgr update --self && sudo tlmgr install standalone preview doublestroke relsize fundus-calligra wasysym physics dvisvgm.x86_64-darwin dvisvgm rsfs wasy cm-super babel-english gnu-freefont mathastext cbfonts-fd xetex  (or the full `brew install --cask mactex-no-gui`)",
    "linux": "sudo apt-get install texlive texlive-latex-extra texlive-fonts-extra texlive-latex-recommended texlive-science dvisvgm",
    "win32": "Install MiKTeX (https://miktex.org/download); it fetches packages on first use",
}
MANIM_FIX = {
    "darwin": "brew install cairo pkg-config  &&  pip install manim",
    "linux": "sudo apt-get install build-essential python3-dev libcairo2-dev libpango1.0-dev  &&  pip install manim",
    "win32": "pip install manim",
}
DOCS = "https://docs.manim.community/en/stable/installation.html"


@dataclass(frozen=True)
class Requirement:
    """One dependency: present or not, what we found, how to fix."""

    name: str
    ok: bool
    detail: str = ""
    fix: str = ""
    needed_for: str = ""

    def __str__(self) -> str:
        mark = "ok     " if self.ok else "MISSING"
        s = f"[{mark}] {self.name}: {self.detail}"
        if self.needed_for:
            s += f"  (needed for {self.needed_for})"
        if not self.ok and self.fix:
            s += f"\n          fix: {self.fix}"
        return s


def _platform() -> str:
    return "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")


def check_requirements() -> list[Requirement]:
    """Check manim, LaTeX and dvisvgm; never installs anything."""
    plat = _platform()
    out = []
    try:
        from importlib.metadata import version

        v = version("manim")
        out.append(Requirement("manim", True, f"manim {v} ({sys.executable})", needed_for="rendering"))
    except Exception:
        out.append(
            Requirement(
                "manim", False, f"not importable from {sys.executable}",
                fix=f"{MANIM_FIX[plat]}   (see {DOCS})", needed_for="rendering",
            )
        )
    for tool, why in (("latex", "MathTex, Tex, numbered axes, DecimalNumber, BarChart labels"), ("dvisvgm", "the same (LaTeX -> SVG)")):
        path = shutil.which(tool)
        out.append(
            Requirement(
                tool, bool(path), path or "not on PATH",
                fix=f"{LATEX_FIX[plat]}   (or avoid LaTeX: use Text, `search_examples(..., latex=False)`)",
                needed_for=why,
            )
        )
    return out


def requirements_report() -> str:
    """Human-readable :func:`check_requirements`, plus what to do without LaTeX."""
    reqs = check_requirements()
    lines = [str(r) for r in reqs]
    latex_ok = all(r.ok for r in reqs if r.name in {"latex", "dvisvgm"})
    if not latex_ok:
        lines.append(
            "No LaTeX: write text with Text(...), avoid MathTex/Tex/DecimalNumber/Integer, "
            "use Axes(..., axis_config={'include_numbers': False}), and search with --no-latex."
        )
    return "\n".join(lines)
