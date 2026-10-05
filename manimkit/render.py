"""Render a scene, look at it, and say concisely what went wrong.

:func:`render_check` is the loop an agent runs after every edit: lint, render at
low quality in a child process, sample frames into one contact-sheet PNG (which
the agent then *looks at*), and return a :class:`RenderReport` whose ``str()`` is
a short, readable summary: duration, timeline, layout warnings, and — on failure —
the error with the offending lines of *your* file, not forty frames of manim.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from manimkit.corpus import scene_names
from manimkit.lint import LintIssue, lint_scene

DFLT_QUALITY = "l"
DFLT_N_FRAMES = 8
DFLT_TIMEOUT = 600
DFLT_OUT_DIRNAME = "manimkit_renders"


@dataclass
class RenderReport:
    """What happened when a scene was rendered."""

    ok: bool
    file: str
    scene: str | None = None
    video: str | None = None
    image: str | None = None
    contact_sheet: str | None = None
    frames: list = field(default_factory=list)
    duration: float | None = None
    scene_time: float | None = None
    timeline: list = field(default_factory=list)
    layout_warnings: list = field(default_factory=list)
    lint: list = field(default_factory=list)
    error: str | None = None
    error_kind: str | None = None
    user_frames: list = field(default_factory=list)
    raised_in: str | None = None
    latex_log: str | None = None
    hint: str | None = None
    stderr_tail: str | None = None
    source_hash: str | None = None
    unchanged: bool = False  # same source as the previous render of this file
    #: With ``record_reads=True``: every file the render opened for reading and
    #: every folder it listed, outside the Python installation and ``out_dir``
    #: (``[{"path", "kind"}]``, ``kind`` ``"file"`` or ``"dir"``); ``None`` when
    #: not recorded, or when the render died before reporting.
    reads: list | None = None

    def __str__(self) -> str:
        lines = []
        head = "OK" if self.ok else "FAILED"
        src = (
            f"  [source {self.source_hash}{', UNCHANGED since the last render' if self.unchanged else ''}]"
            if self.source_hash
            else ""
        )
        lines.append(f"{head}: {Path(self.file).name} :: {self.scene}{src}")
        if self.lint:
            lines.append("lint:")
            lines += [f"  - {i}" for i in self.lint]
        if self.ok:
            if self.duration is not None:
                clock = ""
                if (
                    self.scene_time is not None
                    and abs(self.scene_time - self.duration) >= 0.05
                ):
                    clock = (
                        f"  (scene clock {self.scene_time:.2f}s: each play is rounded up to whole frames; "
                        "run_times and waits in multiples of 0.2 s make draft and final lengths match)"
                    )
                lines.append(f"duration: {self.duration:.2f}s{clock}")
            if self.video:
                lines.append(f"video: {self.video}")
            if self.image:
                lines.append(f"image: {self.image}")
            if self.contact_sheet:
                lines.append(f"contact sheet (LOOK AT THIS): {self.contact_sheet}")
            if self.frames:
                lines.append(
                    "frames (settled state after each play, + --at, + final video frame): "
                    + ", ".join(f"{f['t']:.2f}s" for f in self.frames)
                    + f"  in {Path(self.frames[0]['path']).parent}"
                )
        else:
            lines.append(f"error ({self.error_kind}): {self.error}")
            if self.user_frames:
                lines.append("in your file:")
                lines += [f"  {u}" for u in self.user_frames]
            if self.raised_in:
                lines.append(f"raised in: {self.raised_in}")
            if self.hint:
                lines.append(f"hint: {self.hint}")
            if self.latex_log:
                lines.append("latex log:")
                lines += [f"  {x}" for x in self.latex_log.splitlines()]
            if self.stderr_tail and not self.error:
                lines.append("stderr (tail):")
                lines += [f"  {x}" for x in self.stderr_tail.splitlines()]
        if self.timeline:
            lines.append("timeline:")
            lines += [
                f"  {s['t0']:6.2f}–{s['t1']:6.2f}s  {s['what']}" for s in self.timeline
            ]
        if self.layout_warnings:
            lines.append("layout warnings:")
            lines += [
                f"  - t={w['t']:.2f}s [{w['kind']}] {w['message']}"
                for w in self.layout_warnings
            ]
        elif self.ok:
            lines.append("layout warnings: none (still look at the contact sheet)")
        return "\n".join(lines)


def resolve_scene(file, scene: str | None = None) -> str:
    """The scene to render: ``scene`` if given, else the file's only Scene class."""
    if scene:
        return scene
    code = Path(file).read_text(encoding="utf-8")
    names = scene_names(code)
    if len(names) == 1:
        return names[0]
    if not names:
        raise ValueError(f"No Scene subclass found in {file}.")
    raise ValueError(
        f"{file} defines several scenes ({', '.join(names)}); pass scene=<name>."
    )


def render_check(
    file,
    scene: str | None = None,
    *,
    quality: str = DFLT_QUALITY,
    n_frames: int = DFLT_N_FRAMES,
    at: tuple = (),
    out_dir=None,
    probe: bool = True,
    no_latex: bool = False,
    lint: bool = True,
    timeout: float = DFLT_TIMEOUT,
    python: str | None = None,
    record_reads: bool = False,
) -> RenderReport:
    """Lint, render ``scene`` from ``file``, sample frames, report.

    :param quality: ``l`` (480p15, the iteration default), ``m``, ``h``, ``p``, ``k``.
    :param n_frames: how many frames to sample: taken just before animations end
        (settled states), spread over the timeline; evenly spaced if the probe is
        off. The final frame is always added.
    :param at: extra timestamps (seconds) to sample, e.g. where a warning points.
    :param out_dir: where media, frames and the contact sheet go
        (default: ``manimkit_renders/<file stem>/`` next to the file).
    :param probe: record the timeline and check layout after every play/wait.
    :param no_latex: fail on the first use of LaTeX, for scenes that must run on a
        machine without a TeX install (this one may well have it).
    :param python: interpreter to render with (default: this one).
    :param record_reads: record every file the render opens for reading and
        every folder it lists — whatever built the path — in
        :attr:`RenderReport.reads` (:class:`manimkit.reads.ReadRecorder`), so a
        caller that caches renders can key the files a scene reads by a
        computed path.
    """
    file = Path(file).resolve()
    if not file.exists():
        raise FileNotFoundError(file)
    scene = resolve_scene(file, scene)
    out_dir = Path(out_dir) if out_dir else file.parent / DFLT_OUT_DIRNAME / file.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    issues: list[LintIssue] = lint_scene(file) if lint else []
    blocking = [
        i
        for i in issues
        if i.kind == "structure" and i.message.startswith("SyntaxError")
    ]
    if blocking:
        return RenderReport(
            ok=False,
            file=str(file),
            scene=scene,
            lint=[str(i) for i in issues],
            error=blocking[0].message,
            error_kind="syntax",
        )
    args = {
        "file": str(file),
        "scene": scene,
        "quality": quality,
        "n_frames": n_frames,
        "at": list(at),
        "out_dir": str(out_dir),
        "probe": probe,
        "no_latex": no_latex,
        "result_path": str(out_dir / "result.json"),
        "record_reads": record_reads,
    }
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(args, f)
        args_path = f.name
    result_path = Path(args["result_path"])
    source_hash = hashlib.sha1(file.read_bytes()).hexdigest()[:8]
    previous_hash = None
    if result_path.exists():
        try:
            previous_hash = json.loads(result_path.read_text(encoding="utf-8")).get(
                "source_hash"
            )
        except (ValueError, OSError):
            pass
        result_path.unlink()
    args["source_hash"] = source_hash
    with open(args_path, "w", encoding="utf-8") as f:
        json.dump(args, f)
    # no __pycache__ next to the user's scene file
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        proc = subprocess.run(
            [python or sys.executable, "-m", "manimkit._runner", args_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            cwd=str(file.parent),
            env=env,
        )
        stderr = proc.stderr
    except subprocess.TimeoutExpired as e:
        return RenderReport(
            ok=False,
            file=str(file),
            scene=scene,
            lint=[str(i) for i in issues],
            error=f"render timed out after {timeout}s (an infinite updater? a huge run_time?)",
            error_kind="timeout",
            stderr_tail=_tail(e.stderr),
        )
    finally:
        Path(args_path).unlink(missing_ok=True)
    if not result_path.exists():
        return RenderReport(
            ok=False,
            file=str(file),
            scene=scene,
            lint=[str(i) for i in issues],
            error=_last_error_line(stderr) or "the renderer died without a result",
            error_kind="crash",
            stderr_tail=_tail(stderr),
        )
    r = json.loads(result_path.read_text(encoding="utf-8"))
    return RenderReport(
        ok=r.get("ok", False),
        file=str(file),
        scene=scene,
        video=r.get("video"),
        image=r.get("image"),
        contact_sheet=r.get("contact_sheet"),
        frames=r.get("frames", []),
        duration=r.get("duration"),
        scene_time=r.get("scene_time"),
        timeline=r.get("timeline", []),
        layout_warnings=r.get("layout_warnings", []),
        lint=[str(i) for i in issues],
        error=r.get("error"),
        error_kind=r.get("kind"),
        user_frames=r.get("user_frames", []),
        raised_in=r.get("raised_in"),
        latex_log=r.get("latex_log") or None,
        hint=r.get("hint") or None,
        stderr_tail=None if r.get("ok") else _tail(stderr),
        source_hash=source_hash,
        unchanged=previous_hash == source_hash,
        reads=r.get("reads"),
    )


def _tail(text, n: int = 15) -> str:
    if not text:
        return ""
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return "\n".join(text.strip().splitlines()[-n:])


def _last_error_line(text: str) -> str:
    for line in reversed((text or "").strip().splitlines()):
        if "Error" in line or "error" in line:
            return line.strip()
    return ""
