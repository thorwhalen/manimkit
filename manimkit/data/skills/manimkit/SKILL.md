---
name: manimkit
description: >-
  Make animations and explainer videos with Manim (Community Edition, "ManimCE") —
  plan the scene, find a working example to adapt, write the code, render at low
  quality, LOOK at sampled frames, fix, then render the final video. Use whenever
  the user asks for a manim animation, a 3Blue1Brown-style video, an animated
  explanation of a math/science/CS concept, an animated chart or data story, a
  process/flow diagram animation, an algorithm visualisation, or "make a short
  video/animation showing X". Ships a searchable corpus of working scenes
  (`manimkit search`), a linter for ManimGL/outdated API mistakes
  (`manimkit lint`), and a render-and-inspect tool that reports duration,
  timeline, cut-off/overlapping text and concise errors (`manimkit render`).
license: MIT
metadata:
  audience: consumers
---

# Making Manim animations with manimkit

You write **ManimCE** code (`from manim import *`), never ManimGL (`manimlib`). Most
failures are not exotic: an API name from the wrong Manim, text running off the
frame, labels on top of each other, a video the wrong length. This workflow catches
each of those before the user sees it.

```bash
manimkit --help            # if "command not found":  python -m manimkit --help  (same commands)
```

If neither works: `pip install manimkit`, and `pip install manim` if `manimkit check`
says manim is missing. Everything below writes `manimkit ...`; substitute
`python -m manimkit ...` when needed.

## The loop

**0. Check the machine once.** `manimkit check`. If LaTeX is missing — or the user
says the scene must run without it — you can still do a lot: use `Text` (not
`MathTex`/`Tex`), no `DecimalNumber`/`Integer`, axes with `include_numbers=False`
plus `Text` tick labels; add `--no-latex` to every search, and render with
`manimkit render ... --no-latex`, which fails on the first thing that needs LaTeX.

**1. Plan before code.** Write a storyboard table: beats, seconds per beat, what is on
screen, which animation. The seconds must add up to the requested duration (a
"10-second animation" is 9–11 s). 10 s holds 3–5 beats, not 10. Decide the layout
zones: title band at the top, main area, caption band at the bottom. See
`references/storyboard.md` for the template and duration arithmetic.

**2. Retrieve working examples — every time, before writing.**

```bash
manimkit search "bar chart grows then re-sorts" -k 5      # plain words
manimkit search "ValueTracker tangent line" --no-latex    # class names work too
manimkit show bar_chart_story                              # full runnable source
manimkit search "move dot along path" --code -k 2          # hits + code in one go
```

Search once per distinctive visual idea in your storyboard. The full scenes
(`curated`, `gallery`) are the best starting points; if the top hits are only
`api/...` snippets, also try `--origin curated` with more general words ("array
algorithm", "cycle diagram", "line chart"). The corpus has curated
full scenes (data stories, flowcharts, equation derivations, graphs, algorithms,
timelines, code walkthroughs, pie charts, camera zooms...), the official ManimCE
gallery, and ~400 snippets from the docstrings of *the manim version installed here*
— so their API is current by construction. Copy the **patterns** (how the layout is
built, which animation, how the tracker drives things), not the content.

**3. Write one file, one `Scene`.** `from manim import *` at the top, data and sizes
as constants, a `construct(self)` that follows the storyboard beat by beat. Put the
file where the user wants the output (or a working folder), never inside a package.

**4. Lint, then render and look.**

```bash
manimkit lint scene.py                 # seconds; catches ManimGL / removed APIs
manimkit render scene.py MyScene       # -ql render + frames + contact sheet + report
```

The report gives: OK/FAILED, the **duration**, a **timeline** (every play/wait with
start–end seconds), **layout warnings** (`cut-off` text at the frame edge,
`overlap` text on text, `cramped` texts from different groups almost touching,
`text-on-shape` text crossed by a shape's outline, `offscreen` shapes), and the path
to a **contact sheet** PNG: tiles showing the *settled state after each `play`*
(captured during the render, spread over the timeline when there are many), plus
the final video frame and any `--at` times, each labelled with its time.

- **FAILED** → the report shows the exception and the lines of *your* file that led
  to it (and the LaTeX log lines for a LaTeX error). Fix and re-render. If the error
  names an API you are unsure of, `manimkit search <ClassName>` shows it used
  correctly in the installed version.
- **OK** → **open the contact sheet image and look at it** (with your file/image
  reading tool). Warnings are a floor, not a ceiling: they cannot see colour
  contrast, invisible labels, a wrong diagram, or clutter. Go through the checklist
  below. Need to see a specific moment? `manimkit render scene.py MyScene --at 3.5,7`.
- Fix every layout warning unless you can say why it is intended.
- A fix that "did nothing" (the tile looks the same as last time) usually means two
  animations on the same mobject in one `play` — only the last one runs. Compare
  with the previous sheet before trying something else.
- The duration line is the real video length. Each `play` is rounded up to whole
  frames, so use `run_time`s and `wait`s in multiples of 0.2 s (0.4, 0.6, 1.2 — not
  0.5 or 0.7); then the 15 fps draft and the 30/60 fps final have the same length.
  Within ±0.3 s of the requested length is fine; otherwise adjust the waits.

**5. Iterate** until clean (usually 1–3 renders). Each run overwrites the previous
frames and contact sheet of that file (`--out-dir` to keep both). Then the final
render at the quality the user wants: `manimkit render scene.py MyScene --quality m`
(`l` 480p15, `m` 720p30, `h` 1080p60, `k` 4K). The report's `video:` line is the
file to deliver; quote its duration. Do not pass `-p`
(preview) anywhere: there is no display.

## Look at the frames: the checklist

1. Every piece of text fully inside the frame, with margin (≥ 0.5 units from edges).
2. Nothing overlapping that should not: titles vs figures, labels vs curves, old
   captions under new ones (FadeOut/Transform the old one).
3. Every label readable: contrast against what is behind it, size ≥ ~20 px at 480p
   (`font_size` ≥ 24 for body text, 36–48 for titles).
4. The final frame is the message — it is what people remember. It must be clean.
5. The duration matches the request; nothing important happens in under ~0.5 s;
   text stays up long enough to read it (roughly 1 s plus 0.3 s per word).
6. The diagram is *correct*: right numbers, arrows the right way, right order of
   steps, shapes that should tile actually tiling (compute target positions;
   `next_to` puts things side by side, it does not fit them together), facts right
   (a protocol's real messages). Rendering without error proves nothing about that,
   and no warning will catch it — only you, reading the sheet.

## The rules that prevent most failures (details in references/)

- ManimCE only: `Create` not `ShowCreation`; `Text`/`MathTex`/`Tex`, never
  `TextMobject`/`TexMobject`; `Axes` + `axes.plot(f)` not `GraphScene`/`get_graph`;
  `FadeIn(m, shift=UP)` not `FadeInFrom`; `m.animate.shift(...)` not `ApplyMethod`;
  no `CONFIG = {}`. `manimkit lint` flags all of these and any name manim does not
  define, with suggestions. → `references/api-pitfalls.md`
- LaTeX strings are raw strings: `MathTex(r"\frac{a}{b}")`. `MathTex` is already math
  mode (no `$`); `Tex` is text mode (math needs `$...$`).
- Lay out with `arrange`, `next_to(..., buff=)`, `to_edge`, `move_to` — never with
  guessed absolute coordinates for text. After building a group, cap its size:
  `if g.width > config.frame_width - 1: g.scale_to_fit_width(config.frame_width - 1)`.
  → `references/layout-and-timing.md`
- `to_edge(LEFT)` moves only horizontally; the object keeps its y. Centre what you
  build from raw coordinates (`move_to(...)`) before placing it.
- Recolouring a group recolours its children (a label inside a dot vanishes when the
  dot turns the label's colour): `set_fill(c, family=False)` or target the shape.
- `Transform(a, b)` leaves `a` on screen looking like `b` (keep using `a`);
  `ReplacementTransform(a, b)` swaps them (use `b` afterwards). Captions: build the new
  Text at the old one's position and `Transform(caption, new)`.
- Everything that should move together goes in one `VGroup`; images need `Group`.
- In one `play`, touch each mobject once: two `.animate`s on it (or one on a group
  and another on its child) — only the last one runs, silently. Chain instead:
  `m.animate.set_fill(GREY).set_opacity(0.3)`, or animate the parts separately.
- Continuous change = `ValueTracker` + `always_redraw(lambda: ...)` or `add_updater`,
  animated with `tracker.animate.set_value(v)`.
- Duration = sum of `run_time`s (default 1 s each) + `wait`s (default 1 s). Set
  `run_time` explicitly; check the report's duration line.

## Python API (same functions the CLI wraps)

```python
from manimkit import search_examples, get_example, lint_scene, render_check, check_requirements
hits = search_examples("pie chart with legend", k=3, latex=False)
print(get_example(hits[0].example.id).runnable_code)
report = render_check("scene.py", "MyScene", n_frames=6)   # report.ok, .contact_sheet, .layout_warnings
print(report)
```

Outputs go to `manimkit_renders/<file stem>/` next to the scene file (media, frames,
contact sheet); `--out-dir` changes that.
