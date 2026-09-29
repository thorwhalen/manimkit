# Layout and timing in ManimCE

## Positioning — relative, not absolute

| Want | Use |
|---|---|
| Put B next to A | `b.next_to(a, RIGHT, buff=0.3)` (directions: UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR) |
| A row / column of things | `VGroup(a, b, c).arrange(RIGHT, buff=0.5)`; left-aligned column: `.arrange(DOWN, aligned_edge=LEFT)` |
| A grid | `VGroup(*items).arrange_in_grid(rows, cols, buff=0.2)` |
| Pin to an edge / corner | `m.to_edge(UP)`, `m.to_corner(UL, buff=0.5)` — `to_edge` moves ONE axis only |
| Centre something anywhere | `m.move_to(ORIGIN)` / `m.move_to(LEFT * 3 + DOWN)` |
| Align edges | `b.align_to(a, LEFT)` / `b.align_to(a, UP)` |
| Shift | `m.shift(RIGHT * 2)` |
| Same x or y as another | `b.set_x(a.get_x())`, `b.set_y(a.get_y())` |
| Label an object's part | `label.next_to(obj.get_top(), UP)`, `obj.get_center()`, `get_left()`, `get_corner(UR)`, `get_start()`/`get_end()` for lines |

Keep it inside the frame:

```python
MAX_W = config.frame_width - 1.0
group = VGroup(...).arrange(DOWN)
if group.width > MAX_W:
    group.scale_to_fit_width(MAX_W)
if group.height > config.frame_height - 2.0:  # leave room for title + caption
    group.scale_to_fit_height(config.frame_height - 2.0)
```

Long sentences: split with `\n` inside `Text("line one\nline two")`, or use `Paragraph("line one", "line two", alignment="left")`. Text does not wrap itself.

Sizes: `Text(..., font_size=48)` title, 32–36 body, 24–28 labels. `Text` default is 48 — usually too big for body text. `MathTex(...).scale(1.2)` to enlarge equations.

Build figures from raw coordinates (e.g. `Polygon([0,0,0],[3,0,0],[0,4,0])`)? Group them and `move_to` the zone you planned — the raw coordinates are rarely centred.

## Colour and emphasis

- Colour constants: `BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, PINK, TEAL, GOLD, MAROON, WHITE, GREY/GRAY, BLACK`, shades `BLUE_A` (light) … `BLUE_E` (dark), `GREY_A`…`GREY_E`, `DARK_BLUE`, `LIGHT_GREY`. Hex strings work: `"#E07A5F"`. There is no `LIGHT_BLUE` — `manimkit lint` catches invented names.
- `set_color(c)` sets stroke and fill; `set_fill(c, opacity=0.5)`, `set_stroke(c, width=4)`. They apply to the whole family (children too) unless `family=False`.
- Colour parts of text: `Text("x and y", t2c={"x": YELLOW})`; `MathTex("a", "+", "b").set_color_by_tex("a", RED)`; or index a MathTex part `eq[0].set_color(RED)`.
- Emphasis animations: `Indicate(m)`, `Circumscribe(m)`, `Flash(m)`, `Wiggle(m)`, `FocusOn(m)`, `ShowPassingFlash(m.copy())`; boxes: `SurroundingRectangle(m, buff=0.1)`, `BackgroundRectangle(m)`, `Underline(m)`, `Cross(m)`.
- Background colour: `self.camera.background_color = "#1e1e1e"` (or `WHITE` — then make text `BLACK`).

## Animations you will use most

| Purpose | Animation |
|---|---|
| Draw a shape | `Create(shape)`; filled: `DrawBorderThenFill(shape)` |
| Write text / equations | `Write(text)`; quick: `FadeIn(text, shift=UP * 0.3)` |
| Appear / disappear | `FadeIn(m)`, `FadeOut(m)`, `GrowFromCenter(m)`, `GrowFromEdge(m, DOWN)`, `GrowArrow(arrow)`, `SpinInFromNothing(m)` |
| Change a property | `m.animate.shift(RIGHT).scale(0.5).set_color(RED)` (chain methods on ONE `.animate`) |
| Morph A into B | `Transform(a, b)` (keep using `a`), `ReplacementTransform(a, b)` (use `b`), `TransformFromCopy(a, b)` (a stays) |
| Equation steps | `TransformMatchingTex(eq1, eq2)` — build each step from separate string pieces so pieces can match |
| Text changes | `TransformMatchingShapes(t1, t2)` or `Transform(caption, new_caption)` |
| Move along a path | `MoveAlongPath(dot, path)`; rotate: `Rotate(m, angle=PI/2, about_point=ORIGIN)` |
| Several at once, staggered | `LaggedStart(*[FadeIn(x) for x in xs], lag_ratio=0.2)` |
| In sequence within one play | `Succession(a, b, c)` |
| Continuous change | `t = ValueTracker(0)`, `m = always_redraw(lambda: ...)`, `self.play(t.animate.set_value(5))` |
| Remove updaters | `m.clear_updaters()` before transforming an updated mobject |

`rate_func=linear` for constant speed (sweeps, tracers); `smooth` is the default; `there_and_back`, `rush_into`, `rush_from` exist.

## Timing

- Default `run_time=1`; set it per `play`. `self.wait(t)` for pauses.
- Total length = sum of plays and waits; `manimkit render` prints it and a per-step timeline.
- Updaters run during `wait` too; a `wait` with active updaters animates.
- For a target length, adjust waits first, run_times second.

## Scene types

- `Scene` — 2D default.
- `MovingCameraScene` — `self.camera.frame.animate.set(width=4).move_to(target)` to zoom/pan; `frame.save_state()` + `Restore(frame)`.
- `ThreeDScene` — `self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)`, `ThreeDAxes`, `Surface`; 2D overlays via `self.add_fixed_in_frame_mobjects(title)`; `self.begin_ambient_camera_rotation(rate=0.2)`.
- `ZoomedScene` — magnifier inset.
- `LinearTransformationScene` — grids and `apply_matrix` for linear algebra. It transforms everything on screen that is not foreground: register every title/label/caption with `self.add_foreground_mobject(m)` (see the `linear_transformation_eigenvectors` example). With many changing overlays, a plain `Scene` is simpler and robust: `self.play(ApplyMatrix(M, VGroup(plane, v1, v2)))`, with labels added separately.
