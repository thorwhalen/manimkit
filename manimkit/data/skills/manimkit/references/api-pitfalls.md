# ManimCE API pitfalls (what LLM-written Manim gets wrong)

`manimkit lint scene.py` checks most of the first table automatically, plus every capitalised name your file uses that the installed manim does not define (with close-match suggestions). When in doubt about any API, `manimkit search <ClassName>` shows it used correctly *in the installed version* (the docstring examples are harvested from it).

## ManimGL / old-Manim names that do not exist in ManimCE

| Wrong (ManimGL or pre-0.10) | ManimCE |
|---|---|
| `from manimlib import *`, `manimgl` command | `from manim import *`, `manim` command |
| `ShowCreation(m)` | `Create(m)` |
| `TextMobject("hi")` | `Text("hi")` (plain) or `Tex("hi")` (LaTeX text) |
| `TexMobject("x^2")`, `TexText` | `MathTex(r"x^2")`, `Tex(...)` |
| `CONFIG = {...}` class dict | constructor keyword arguments |
| `GraphScene`, `self.setup_axes()`, `self.get_graph(f)` | `axes = Axes(...)`, `axes.plot(f, x_range=[a, b])` |
| `axes.get_graph(f)` | `axes.plot(f)` |
| `FadeInFrom(m, DOWN)`, `FadeInFromDown(m)` | `FadeIn(m, shift=UP)` (shift is the motion direction) |
| `FadeOutAndShift(m, UP)` | `FadeOut(m, shift=UP)` |
| `ApplyMethod(m.shift, UP)` | `m.animate.shift(UP)` |
| `ShowCreationThenDestruction(m)` | `ShowPassingFlash(m.copy())` |
| `InteractiveScene`, `self.embed()` | not available — ManimGL only |
| `self.frame` (GL camera) | `MovingCameraScene` and `self.camera.frame` |
| `Code(code=...)`, `insert_line_no=`, `style=` | since 0.19: `Code(code_string=..., language="python", add_line_numbers=True, formatter_style="monokai", background="window")`; lines are `code.code_lines` |

## LaTeX

- Raw strings, always: `MathTex(r"\frac{1}{2}")`. In a normal string `\f` becomes a form-feed and `\t` a tab; the LaTeX error that follows is confusing.
- `MathTex` is math mode: no `$`. `Tex` is text mode: math inside needs `$...$`: `Tex(r"The area is $\pi r^2$")`.
- Split an equation into pieces to address/colour/morph them: `MathTex("a^2", "+", "b^2", "=", "c^2")` → `eq[0]` is `a^2`. `TransformMatchingTex` matches identical pieces between steps; `substrings_to_isolate=["x"]` or `{{ x }}` double braces isolate parts of a single string.
- Things that silently need LaTeX: `DecimalNumber`, `Integer`, `Variable`, `Matrix`, `BarChart` labels, `NumberLine(include_numbers=True)`, `Axes(axis_config={"include_numbers": True})`, `axes.get_axis_labels()`, `axes.get_graph_label()`, `Brace.get_tex`, `Title`, `Graph(labels=True)`. Without LaTeX: `Text` everywhere, `include_numbers=False` plus `Text` tick labels, `Graph(labels={v: Text(str(v))})`.
- A LaTeX error in the render report comes with the LaTeX log's `!` lines — they name the bad command (`Undefined control sequence`, `Missing $ inserted` = math in `Tex` text mode).
- Unicode in `Text` is fine (`Text("café → 25 °C")`); in `MathTex` it is not — use LaTeX commands (`\rightarrow`, `^\circ`).

## Mobjects and animations

- `Transform(a, b)`: afterwards the on-screen object is still `a` (now shaped like `b`); `b` was never added. Animate `a` next time. `ReplacementTransform(a, b)`: afterwards `b` is on screen and `a` is gone. Mixing them up produces "nothing happens" or duplicate objects.
- One `.animate` per mobject per `play`: `self.play(m.animate.shift(UP), m.animate.scale(2))` — only the last wins. Chain instead: `m.animate.shift(UP).scale(2)`.
- `.animate` interpolates start and end states, so rotating by `PI` with `.animate.rotate(PI)` may look like a flip; use `Rotate(m, PI)` for a real rotation.
- Updaters: a mobject with an updater keeps following it; `clear_updaters()` before transforming it, or the updater fights the animation. `always_redraw` rebuilds every frame — keep the lambda cheap.
- `self.add(m)` shows instantly (no time); `self.remove(m)` hides instantly. To hide with an animation: `FadeOut(m)`.
- Draw order = add order: add backgrounds and edges first, or `m.set_z_index(1)`.
- `VGroup` only holds VMobjects; an `ImageMobject` (or `SVGMobject` mixed with images) needs `Group`.
- `Arrow(start, end)` has `buff=0.25` by default (it stops short of the points); use `buff=0` for vectors that must touch their endpoints.
- `Line`/`Arrow` take points, not mobjects: `Arrow(a.get_right(), b.get_left(), buff=0.1)`.
- Angles are radians: `PI / 2`, or `90 * DEGREES`.
- `set_color` / `set_fill` on a group recolours every child; `family=False` to colour only the parent's own shape.
- `Graph` edges are keyed in the order you declared them: `g.edges[(1, 2)]`, not `(2, 1)`. Vertices: `g.vertices[v]`. Layouts: `"spring"`, `"circular"`, `"kamada_kawai"`, `"tree"` (needs `root_vertex=`), `"partite"`.
- `BarChart(values, bar_names=[...], y_range=[0, 10, 2])`; update with `chart.animate.change_bar_values(new)`. It uses LaTeX for labels. For full control or no LaTeX, build bars from `Rectangle`s (see the `bar_chart_story` example).
- Axes: `axes.c2p(x, y)` (coordinates → point), `axes.p2c(point)`, `axes.plot(f, x_range=[a, b], color=...)`, `axes.get_area(graph, x_range=[a, b])`, `axes.get_riemann_rectangles(graph, dx=0.25)`, `axes.plot_line_graph(x_values, y_values)`, `axes.get_vertical_line(point)`.
- `NumberPlane().apply_function(f)` / `LinearTransformationScene.apply_matrix(M)` for grid warps.
- `LinearTransformationScene`: `apply_matrix` transforms everything on screen that is not registered as foreground. Register every title, label and caption with `self.add_foreground_mobject(m)` before showing it — including each *new* caption you later `Transform` into — or the transform fails with `ValueError: zip() argument 3 is longer than arguments 1-2`. Vectors that should move: `self.add_vector([x, y])`; extra shapes that should warp with the grid: `self.add_transformable_mobject(m)`. See the `linear_transformation_eigenvectors` example.
- Points are 3D everywhere: `[x, y, 0]`, not `[x, y]` (a 2D list fails with "operands could not be broadcast together"). `axes.c2p(x, y)` returns a 3D point.

## Rendering

- CLI: `manim -ql file.py Scene` (480p15), `-qm` 720p30, `-qh` 1080p60, `-qk` 4K; `-s` saves only the last frame as PNG; `--format gif`; `-a` renders all scenes. Output lands in `media/videos/<file>/<quality>/Scene.mp4`.
- Never `-p` / `--preview` in an agent run — there is no display.
- The bare `manim` CLI (observed with manim 0.20.1) never exits if the scene raises inside a `play`: its movie-writer thread waits forever. Use `manimkit render`, which exits as soon as the error is recorded.
- A file with several Scene classes: always name the one to render.
- Slow renders: lots of `always_redraw` with LaTeX inside (every frame re-compiles unless cached), huge `Surface` resolutions, very long `wait`s at high quality. Iterate at `-ql`.
