"""Child-process side of :func:`manimkit.render.render_check`.

Runs in its own interpreter (``python -m manimkit._runner args.json``) so a
crashing or hanging scene cannot take the caller down, and so the layout probe can
monkeypatch ``Scene.play`` without touching anyone else's manim. It:

1. imports the scene file and renders one scene through manim's own API
   (``tempconfig`` + ``Scene().render()``, what ``manim -ql file.py Scene`` does);
2. after every ``play``/``wait``, records the timeline and checks the layout —
   text cut off at the frame edge, shapes partly off-screen, text overlapping text;
3. samples frames from the resulting video and tiles them into a contact sheet;
4. writes everything, including a concise error, as JSON for the parent.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import traceback
from pathlib import Path

QUALITY = {
    "l": "low_quality",
    "m": "medium_quality",
    "h": "high_quality",
    "p": "production_quality",
    "k": "fourk_quality",
}
EDGE_TOLERANCE = 0.1  # scene units a mobject may poke past the frame edge
OVERLAP_FRACTION = 0.2  # of the smaller text's box area
MIN_TEXT_GAP = 0.1  # scene units between texts from different groups before 'cramped'
MIN_VISIBLE_OPACITY = 0.05
MIN_TEXT_SIZE = 1e-3  # an empty Text('') has no extent: ignore it
TEXT_BOX_SHRINK = 0.15  # x the box's smaller side, per side: glyph boxes are generous
SOLID_FILL_OPACITY = 0.5  # stroke-less shapes more transparent than this are highlights
MAX_WARNINGS = 12
SHEET_COLUMNS = 3
LABEL_HEIGHT = 30


# --------------------------------------------------------------------------- #
# layout probe
# --------------------------------------------------------------------------- #


class _Probe:
    def __init__(self, capture_dir=None):
        import manim as m

        self.capture_dir = Path(capture_dir) if capture_dir else None
        self.beats: list[dict] = []  # settled frame captured after each play

        self.m = m
        self.text_types = tuple(
            getattr(m, n)
            for n in ("Text", "MarkupText", "SingleStringMathTex", "DecimalNumber", "Code")
            if hasattr(m, n)
        )
        self.warnings: dict[tuple, dict] = {}
        self.timeline: list[dict] = []

    # -- helpers ----------------------------------------------------------- #
    def _label(self, mob) -> str:
        for attr in ("original_text", "tex_string", "text"):
            s = getattr(mob, attr, None)
            if isinstance(s, str) and s.strip():
                s = " ".join(s.split())
                return f"{type(mob).__name__}({s[:40]!r}{'…' if len(s) > 40 else ''})"
        if hasattr(mob, "get_value") and type(mob).__name__ in {"DecimalNumber", "Integer"}:
            return f"{type(mob).__name__}({mob.get_value():g})"
        return type(mob).__name__

    def _visible(self, mob) -> bool:
        members = mob.family_members_with_points()
        if not members:
            return False
        for sm in members:
            try:
                if sm.get_fill_opacity() > MIN_VISIBLE_OPACITY:
                    return True
                if sm.get_stroke_opacity() > MIN_VISIBLE_OPACITY and sm.get_stroke_width() > 0:
                    return True
            except Exception:
                return True  # images and the like: assume visible
        return False

    def _box(self, mob):
        return (mob.get_left()[0], mob.get_right()[0], mob.get_bottom()[1], mob.get_top()[1])

    def _frame(self, scene):
        frame = getattr(scene.camera, "frame", None)
        if frame is not None:
            c = frame.get_center()
            return c[0] - frame.width / 2, c[0] + frame.width / 2, c[1] - frame.height / 2, c[1] + frame.height / 2
        cfg = self.m.config
        return -cfg.frame_width / 2, cfg.frame_width / 2, -cfg.frame_height / 2, cfg.frame_height / 2

    def _text_units(self, mob):
        if isinstance(mob, self.text_types):
            yield mob
            return
        for sub in mob.submobjects:
            yield from self._text_units(sub)

    def _warn(self, t, kind, key, message):
        k = (kind, key)
        if k not in self.warnings and len(self.warnings) < MAX_WARNINGS:
            self.warnings[k] = {"t": round(t, 2), "kind": kind, "message": message}

    # -- the check --------------------------------------------------------- #
    def check(self, scene):
        m = self.m
        if isinstance(scene, getattr(m, "ThreeDScene", ())):
            return  # projected 3D boxes are not what the viewer sees
        t = scene.renderer.time
        fl, fr, fb, ft = self._frame(scene)
        fw, fh = fr - fl, ft - fb
        tol = EDGE_TOLERANCE
        texts, shapes = [], []  # shapes: (top, non-text bbox)
        zoomed = fw < m.config.frame_width * 0.98  # a zoomed camera crops on purpose
        highlight_types = tuple(getattr(m, n) for n in ("SurroundingRectangle", "BackgroundRectangle", "Underline", "Cross", "Brace") if hasattr(m, n))
        coord_types = tuple(getattr(m, n) for n in ("CoordinateSystem", "NumberLine") if hasattr(m, n))
        for top in scene.mobjects:
            if not self._visible(top):
                continue
            units = [u for u in self._text_units(top) if self._visible(u) and min(u.width, u.height) > MIN_TEXT_SIZE]
            texts += [(u, top) for u in units]
            l, r, b, tp = self._box(top)
            partly_out = (l < fl - tol or r > fr + tol or b < fb - tol or tp > ft + tol)
            fully_out = r < fl or l > fr or tp < fb or b > ft
            if not units and not zoomed and partly_out and not fully_out and (r - l) < fw and (tp - b) < fh:
                self._warn(t, "offscreen", self._label(top), f"{self._label(top)} is partly outside the frame ({self._edges(l, r, b, tp, fl, fr, fb, ft)}).")
            if not isinstance(top, coord_types) and not isinstance(top, highlight_types):
                segs = self._shape_segments(top, units)
                if segs is not None:
                    shapes.append((top, segs))
        for u, top in texts:
            if self._backed(u, top):
                continue  # the author put an opaque backing behind it: overlap is intended
            l, r, b, tp = self._box(u)
            d = TEXT_BOX_SHRINK * min(r - l, tp - b)
            box = (l + d, r - d, b + d, tp - d)
            for other, segs in shapes:
                if other is top:
                    continue
                if _segments_hit_box(segs, box):
                    self._warn(t, "text-on-shape", (self._label(u), self._label(other)), f"{self._label(u)} is crossed by the outline of {self._label(other)} — move one (next_to/to_edge/shift), shrink the figure, or add_background_rectangle() to the text if the overlap is intended.")
        tops = {id(u): top for u, top in texts}
        texts = [u for u, _ in texts]
        for u in texts:
            l, r, b, tp = self._box(u)
            fully_out = r < fl or l > fr or tp < fb or b > ft
            if fully_out:
                continue
            edges = self._edges(l, r, b, tp, fl, fr, fb, ft)
            if edges:
                self._warn(t, "cut-off", self._label(u), f"{self._label(u)} is cut off at the frame edge ({edges}); scale it down or move it in.")
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                a, c = texts[i], texts[j]
                if a is c:
                    continue
                ba, bc = self._box(a), self._box(c)
                la, lc = self._label(a), self._label(c)
                frac = self._overlap(ba, bc)
                if frac > OVERLAP_FRACTION:
                    self._warn(t, "overlap", tuple(sorted([la, lc])), f"{la} overlaps {lc} ({frac:.0%} of the smaller one); use next_to/arrange with buff, or FadeOut the old one first.")
                elif frac == 0 and tops[id(a)] is not tops[id(c)]:
                    gap = self._gap(ba, bc)
                    if gap is not None and gap < MIN_TEXT_GAP:
                        self._warn(t, "cramped", tuple(sorted([la, lc])), f"{la} and {lc} are only {max(gap, 0):.2f} units apart (hint: buff >= {MIN_TEXT_GAP}); give them room unless they belong together.")

    @staticmethod
    def _gap(a, c):
        """Clear distance between two boxes that face each other, else None."""
        x_overlap = min(a[1], c[1]) - max(a[0], c[0])
        y_overlap = min(a[3], c[3]) - max(a[2], c[2])
        if x_overlap > 0:  # stacked vertically
            return max(a[2], c[2]) - min(a[3], c[3])
        if y_overlap > 0:  # side by side
            return max(a[0], c[0]) - min(a[1], c[1])
        return None

    def _backed(self, u, top) -> bool:
        """Does the text sit on an opaque backing (add_background_rectangle or a filled box)?"""
        if getattr(u, "background_rectangle", None) is not None:
            return True
        l, r, b, tp = self._box(u)
        text_ids = {id(x) for x in u.get_family()}
        for x in top.family_members_with_points():
            if id(x) in text_ids:
                continue
            try:
                solid = x.get_fill_opacity() >= SOLID_FILL_OPACITY
            except Exception:
                continue
            if solid:
                xl, xr, xb, xt = self._box(x)
                if xl <= l and xr >= r and xb <= b and xt >= tp:
                    return True
        return False

    def _shape_segments(self, top, units):
        """Polyline segments of ``top``'s visible, stroked, non-text outline parts."""
        import numpy as np

        text_ids = {id(x) for u in units for x in u.get_family()}
        pts = []
        for x in top.family_members_with_points():
            if id(x) in text_ids:
                continue
            try:
                stroked = x.get_stroke_width() > 0 and x.get_stroke_opacity() > MIN_VISIBLE_OPACITY
                solid = x.get_fill_opacity() >= SOLID_FILL_OPACITY
            except Exception:
                continue  # images etc.
            if not (stroked or solid):
                continue  # translucent, stroke-less highlight: intended to sit on text
            p = np.asarray(x.points)[:, :2]
            if len(p) >= 2:
                pts.append(p)
        if not pts:
            return None
        return pts

    @staticmethod
    def _edges(l, r, b, tp, fl, fr, fb, ft):
        tol = EDGE_TOLERANCE
        out = []
        if l < fl - tol:
            out.append(f"left by {fl - l:.2f}")
        if r > fr + tol:
            out.append(f"right by {r - fr:.2f}")
        if b < fb - tol:
            out.append(f"bottom by {fb - b:.2f}")
        if tp > ft + tol:
            out.append(f"top by {tp - ft:.2f}")
        return ", ".join(out)

    @staticmethod
    def _overlap(a, c):
        w = min(a[1], c[1]) - max(a[0], c[0])
        h = min(a[3], c[3]) - max(a[2], c[2])
        if w <= 0 or h <= 0:
            return 0.0
        smaller = min((a[1] - a[0]) * (a[3] - a[2]), (c[1] - c[0]) * (c[3] - c[2]))
        return (w * h) / smaller if smaller > 0 else 0.0

    def capture(self, scene):
        """Save the settled frame after a play (exact: no video-timing guesswork)."""
        if self.capture_dir is None:
            return
        from PIL import Image

        scene.renderer.update_frame(scene, ignore_skipping=True)
        arr = scene.renderer.get_frame()
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        p = self.capture_dir / f"beat_{len(self.beats):03d}.png"
        Image.fromarray(arr).convert("RGB").save(p)
        self.beats.append({"t": round(scene.renderer.time, 2), "path": str(p)})

    # -- patching ---------------------------------------------------------- #
    def install(self):
        Scene = self.m.Scene
        probe = self
        orig_play, orig_wait = Scene.play, Scene.wait
        state = {"depth": 0}

        def record(scene, t0, what):
            try:
                probe.timeline.append({"t0": round(t0, 2), "t1": round(scene.renderer.time, 2), "what": what})
                probe.check(scene)
                if what != "wait":
                    probe.capture(scene)
            except Exception as e:  # the probe must never break a render
                probe.timeline.append({"t0": round(t0, 2), "t1": round(t0, 2), "what": f"(probe error: {e})"})

        def play(scene, *args, **kwargs):
            t0 = scene.renderer.time
            state["depth"] += 1
            try:
                out = orig_play(scene, *args, **kwargs)
            finally:
                state["depth"] -= 1
            if state["depth"] == 0:
                record(scene, t0, _compact([_anim_name(a) for a in args]))
            return out

        def wait(scene, *args, **kwargs):
            t0 = scene.renderer.time
            state["depth"] += 1
            try:
                out = orig_wait(scene, *args, **kwargs)
            finally:
                state["depth"] -= 1
            if state["depth"] == 0:
                record(scene, t0, "wait")
            return out

        Scene.play, Scene.wait = play, wait


class LatexBlockedError(RuntimeError):
    """Raised when a scene rendered with ``no_latex`` needs LaTeX."""


def _block_latex():
    """Make any LaTeX compilation fail loudly (the target machine has no TeX)."""
    import manim.mobject.text.tex_mobject as tex_mobject
    import manim.utils.tex_file_writing as tex_file_writing

    def blocked(expression, *args, **kwargs):
        raise LatexBlockedError(
            f"this needs LaTeX (expression {str(expression)[:60]!r}) but the render ran with no_latex: "
            "use Text instead of MathTex/Tex, Text tick labels instead of include_numbers, "
            "and avoid DecimalNumber/Integer/BarChart/get_tex/get_axis_labels."
        )

    tex_file_writing.tex_to_svg_file = blocked
    tex_mobject.tex_to_svg_file = blocked


def _compact(names: list[str]) -> str:
    counts = {}
    for n in names:
        counts[n] = counts.get(n, 0) + 1
    return ", ".join(n if c == 1 else f"{n} x{c}" for n, c in counts.items())


def _anim_name(a) -> str:
    try:
        name = type(a).__name__
        mob = getattr(a, "mobject", None)
        if name == "_AnimationBuilder":
            methods = []
            for m in getattr(a, "methods", []) or []:
                fn = getattr(m, "method", None) or (m[0] if isinstance(m, (tuple, list)) else None)
                methods.append(getattr(fn, "__name__", "?"))
            return f"{type(mob).__name__}.animate" + "".join(f".{n}" for n in methods)
        return f"{name}({type(mob).__name__})" if mob is not None else name
    except Exception:
        return type(a).__name__


def _segments_hit_box(polylines, box) -> bool:
    """Does any segment of any polyline pass through the (x0, x1, y0, y1) box?"""
    x0, x1, y0, y1 = box
    if x1 <= x0 or y1 <= y0:
        return False
    for p in polylines:
        for (ax, ay), (bx, by) in zip(p[:-1], p[1:]):
            if max(ax, bx) < x0 or min(ax, bx) > x1 or max(ay, by) < y0 or min(ay, by) > y1:
                continue
            if _clip(ax, ay, bx, by, x0, x1, y0, y1):
                return True
    return False


def _clip(ax, ay, bx, by, x0, x1, y0, y1) -> bool:
    """Liang-Barsky: does segment a-b intersect the box?"""
    dx, dy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, ax - x0), (dx, x1 - ax), (-dy, ay - y0), (dy, y1 - ay)):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


# --------------------------------------------------------------------------- #
# errors
# --------------------------------------------------------------------------- #


def _concise_error(exc: BaseException, file: Path) -> dict:
    tb = traceback.extract_tb(exc.__traceback__)
    user = [f for f in tb if Path(f.filename).resolve() == file.resolve()]
    lines = [f"line {f.lineno}: {(f.line or '').strip()}" for f in user[-3:]]
    last = tb[-1] if tb else None
    where = f"{Path(last.filename).name}:{last.lineno} in {last.name}" if last else ""
    msg = f"{type(exc).__name__}: {exc}"
    out = {"error": msg, "user_frames": lines, "raised_in": where, "kind": "python"}
    if isinstance(exc, LatexBlockedError):
        out["kind"] = "latex-blocked"
    elif "latex" in str(exc).lower():
        out["kind"] = "latex"
        out["latex_log"] = _latex_log_excerpt(str(exc))
    return out


def _latex_log_excerpt(message: str, *, context: int = 2) -> str:
    m = re.search(r"(\S+\.log)", message)
    if not m or not Path(m.group(1)).exists():
        return ""
    lines = Path(m.group(1)).read_text(encoding="utf-8", errors="replace").splitlines()
    keep = []
    for i, line in enumerate(lines):
        if line.startswith("!"):
            keep += lines[i : i + context + 1]
    return "\n".join(keep[:20])


# --------------------------------------------------------------------------- #
# frames
# --------------------------------------------------------------------------- #


def _sample_times(duration: float, n: int, at: list[float]) -> list[float]:
    """Evenly spaced frame times plus ``at`` plus the final frame (fallback sampling).

    >>> _sample_times(4, 2, [1.5])
    [1.0, 1.5, 3.0, 3.999]
    """
    if duration <= 0:
        return [0.0]
    times = [duration * (i + 0.5) / n for i in range(n)] if n > 0 else []
    times += [t for t in at if 0 <= t <= duration]
    times.append(max(duration - 1e-3, 0.0))  # the end state always
    return sorted(set(round(t, 3) for t in times))


def _choose_evenly(items: list, n: int) -> list:
    """At most ``n`` items spread over the list, first and last included.

    >>> _choose_evenly(list(range(10)), 4)
    [0, 3, 6, 9]
    """
    if n <= 0:
        return []
    if len(items) <= n:
        return list(items)
    return [items[round(i * (len(items) - 1) / max(n - 1, 1))] for i in range(n)]


def _video_duration(video: Path) -> float:
    import av

    with av.open(str(video)) as c:
        stream = c.streams.video[0]
        if stream.frames and stream.average_rate:
            return float(stream.frames / stream.average_rate)
        return float(c.duration or 0) / 1_000_000


def _extract_frames(video: Path, times: list[float], out_dir: Path) -> list[dict]:
    import av

    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = list(times)
    got, last = [], None
    with av.open(str(video)) as container:
        for frame in container.decode(video=0):
            ft = float(frame.time or 0.0)
            while wanted and ft + 1e-6 >= wanted[0]:
                got.append((wanted.pop(0), frame.to_image()))
            last = (ft, frame)
            if not wanted:
                break
    if wanted and last is not None:
        img = last[1].to_image()
        got += [(t, img) for t in wanted]
    out = []
    for t, img in got:
        p = out_dir / f"frame_{t:07.2f}s.png"
        img.save(p)
        out.append({"t": t, "path": str(p)})
    return out


def _contact_sheet(frames: list[dict], path: Path) -> str | None:
    from PIL import Image, ImageDraw, ImageFont

    if not frames:
        return None
    imgs = [Image.open(f["path"]).convert("RGB") for f in frames]
    w, h = imgs[0].size
    cols = min(SHEET_COLUMNS, len(imgs))
    rows = -(-len(imgs) // cols)
    sheet = Image.new("RGB", (cols * w, rows * (h + LABEL_HEIGHT)), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=LABEL_HEIGHT - 6)
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    for k, (img, f) in enumerate(zip(imgs, frames)):
        x, y = (k % cols) * w, (k // cols) * (h + LABEL_HEIGHT)
        sheet.paste(img.resize((w, h)), (x, y + LABEL_HEIGHT))
        draw.text((x + 6, y + 2), f"t = {f['t']:.2f}s", fill="black", font=font)
    sheet.save(path)
    return str(path)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def run(args: dict) -> dict:
    file = Path(args["file"]).resolve()
    out_dir = Path(args["out_dir"]).resolve()
    result = {"ok": False, "file": str(file), "scene": args.get("scene"), "source_hash": args.get("source_hash")}
    probe = None
    try:
        import manim  # noqa: F401
        from manim import config, tempconfig

        frames_dir = out_dir / "frames"
        if frames_dir.exists():
            for old in frames_dir.glob("*.png"):
                old.unlink()
        if args.get("probe", True):
            probe = _Probe(capture_dir=frames_dir)
            probe.install()
        if args.get("no_latex"):
            _block_latex()
        sys.path.insert(0, str(file.parent))
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[file.stem] = module
        spec.loader.exec_module(module)
        scene_cls = getattr(module, args["scene"])
        overrides = {
            "quality": QUALITY.get(args.get("quality", "l"), "low_quality"),
            "media_dir": str(out_dir / "media"),
            "progress_bar": "none",
            "verbosity": "WARNING",
            "input_file": str(file),
            "preview": False,
            "format": "mp4",
        }
        with tempconfig(overrides):
            scene = scene_cls()
            scene.render()
            fw = scene.renderer.file_writer
            duration = float(scene.renderer.time)
            video = Path(fw.movie_file_path) if getattr(fw, "movie_file_path", None) else None
            image = Path(fw.image_file_path) if getattr(fw, "image_file_path", None) else None
            result["pixel_size"] = [config.pixel_width, config.pixel_height]
            result["fps"] = config.frame_rate
        result["scene_time"] = round(duration, 2)
        result["duration"] = round(duration, 2)
        if video and video.exists() and duration > 0:
            result["video"] = str(video)
            video_duration = _video_duration(video) or duration
            result["duration"] = round(video_duration, 2)
            n = args.get("n_frames", 8)
            at = [t for t in args.get("at", []) if 0 <= t <= video_duration]
            beats = probe.beats if probe else []
            if beats:  # exact settled states, captured during the render
                chosen = _choose_evenly(beats, n)
                for b in beats:
                    if b not in chosen:
                        Path(b["path"]).unlink(missing_ok=True)
                times = sorted(set(at + [max(video_duration - 1e-3, 0.0)]))
                frames = chosen + _extract_frames(video, times, frames_dir)
            else:
                frames = _extract_frames(video, _sample_times(video_duration, n, at), frames_dir)
            frames.sort(key=lambda f: f["t"])
            result["frames"] = frames
            result["contact_sheet"] = _contact_sheet(frames, out_dir / f"{args['scene']}_sheet.png")
        elif image and image.exists():
            result["image"] = str(image)
            result["frames"] = [{"t": 0.0, "path": str(image)}]
            result["contact_sheet"] = str(image)
        result["ok"] = True
    except BaseException as exc:  # noqa: BLE001 - we report everything
        result.update(_concise_error(exc, file))
    if probe is not None:
        result["timeline"] = probe.timeline
        result["layout_warnings"] = sorted(probe.warnings.values(), key=lambda w: w["t"])
    return result


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    result = run(args)
    Path(args["result_path"]).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["ok"] else 1


def _exit_now(code: int):
    """Exit without waiting for threads.

    When a scene raises mid-``play``, manim's movie-writer thread (non-daemon)
    never receives its stop signal, and a normal interpreter exit waits for it
    forever — the parent would then sit until its timeout.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


if __name__ == "__main__":
    _exit_now(main())
