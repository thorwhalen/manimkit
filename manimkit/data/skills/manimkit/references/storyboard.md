# Planning a Manim scene: the storyboard

Write this before any code. It takes two minutes and prevents the two most common
complaints: "it's too long / too short" and "too much happens at once".

## Template

| # | Seconds | On screen after this beat | Animation(s) | Notes |
|---|---------|---------------------------|--------------|-------|
| 1 | 0.0–1.5 | Title at top | `Write(title)` 1.5 s | |
| 2 | 1.5–4.5 | Title + figure | `Create(fig)` 2 s, wait 1 s | |
| 3 | 4.5–8.0 | Figure changes, caption at bottom | `tracker.animate.set_value` 2.5 s, `FadeIn(caption)` 1 s | |
| 4 | 8.0–10.0 | Final state (the takeaway) | `Indicate(key)` 1 s, wait 1 s | Final frame = the message |

Rules of thumb:

- A 10 s animation holds 3–5 beats. A 30 s one, 8–12. More beats than that is a slideshow at double speed.
- End on a hold: `self.wait(1)`–`self.wait(2)` so the viewer sees the final state.
- One new idea per beat. If a beat has two, split it or drop one.
- Text on screen at once: a title, a caption, and at most ~5 labels. More goes into a second section (FadeOut the first).
- Budget reading time: about 1 s plus 0.3 s per word for any sentence that appears.

## Duration arithmetic

- `self.play(...)` lasts `run_time` (default **1 s**); several animations in one `play` run in parallel and last as long as the longest one.
- `self.wait()` is 1 s; `self.wait(0.5)` half a second.
- `LaggedStart(*anims, lag_ratio=r)` lasts roughly `run_time` of the whole group (set `run_time=` on the LaggedStart).
- `Succession(a, b)` is sequential: sum of the parts.
- `self.add(...)` takes zero time (no animation).
- Loops multiply: a loop of 6 steps with `run_time=0.6` plus `wait(0.4)` is 6 s.
- Every `play`/`wait` is rounded UP to whole frames: at 15 fps (the `-ql` draft) a `run_time=0.5` lasts 0.533 s. Use multiples of 0.2 s so the draft and the 30/60 fps final have the same length. `manimkit render` prints the real video length, and the scene clock when they differ.

After rendering, `manimkit render` prints the real duration and a timeline of every play/wait. Compare with the storyboard, then adjust `run_time`s and `wait`s — do not cut beats to hit a length if the content needs them; ask instead.

## Layout zones (default 16:9 frame, 14.2 x 8 units, origin at centre)

- Title band: `title.to_edge(UP)` (y ≈ 3.2–3.6). Keep the figure below y ≈ 2.6.
- Caption band: `caption.to_edge(DOWN, buff=0.6)` (y ≈ −3.2). Keep the figure above y ≈ −2.6.
- Main area: roughly x ∈ [−6.5, 6.5], y ∈ [−2.6, 2.6]. Two-column layouts: figure at `LEFT * 3`, text or equation at `RIGHT * 3.5`.
- `config.frame_width` / `config.frame_height` give the exact numbers; use them instead of literals when capping sizes.
