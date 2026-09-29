"""Visual counting proof with a grid of squares: 1 + 2 + ... + n as a staircase, doubled into an n x (n+1) rectangle.

tags: visual proof, counting, grid, squares, staircase, triangular numbers, sum formula, arithmetic series, gauss, math concept, proof without words, arrange_in_grid, latex
scene: GridCountingProof
source: original (manimkit, MIT)

The pattern behind many proofs without words: build unit squares with a helper,
colour groups (one row = one term), bring terms in one at a time with LaggedStart,
then copy the whole figure, rotate it 180 degrees and slot it INTO the original's
empty half (target position computed, not guessed) to form a rectangle whose area is easy to read. Brace + label gives the side
lengths; the formula appears last. Figure on the left, algebra on the right.
"""

from manim import *

N = 4
SIDE = 0.55
COLORS = [BLUE, TEAL, GREEN, YELLOW, ORANGE, RED]


def cell(color):
    return Square(SIDE, fill_color=color, fill_opacity=0.85, stroke_color=WHITE, stroke_width=1.5)


class GridCountingProof(Scene):
    def construct(self):
        title = Text("1 + 2 + 3 + 4 = ?", font_size=40).to_edge(UP)
        self.play(Write(title))

        rows = VGroup()
        for k in range(1, N + 1):  # row k has k squares
            row = VGroup(*[cell(COLORS[k - 1]) for _ in range(k)]).arrange(RIGHT, buff=0)
            rows.add(row)
        rows.arrange(DOWN, buff=0, aligned_edge=LEFT).move_to(LEFT * 4)
        for row in rows:
            self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in row], lag_ratio=0.15), run_time=0.6)
        self.wait(0.4)

        # Copy, rotate 180 degrees, slot next to the staircase: an N x (N + 1) rectangle.
        # Its right edge must land N + 1 cells from the staircase's left edge — compute the
        # target explicitly; next_to(rows, RIGHT) would leave a gap, not a rectangle.
        twin = rows.copy().set_fill(opacity=0.35)
        target = rows.copy().rotate(PI).align_to(rows, UP)
        target.shift(RIGHT * (rows.get_left()[0] + SIDE - target.get_left()[0]))
        self.play(twin.animate.rotate(PI).move_to(target), run_time=1.5)
        rect = VGroup(rows, twin)
        b_w = Brace(rect, DOWN)
        b_h = Brace(rect, LEFT)
        w_label = b_w.get_text(f"{N + 1}")
        h_label = b_h.get_text(f"{N}")
        self.play(GrowFromCenter(b_w), GrowFromCenter(b_h), FadeIn(w_label), FadeIn(h_label))

        algebra = VGroup(
            MathTex(r"2 \times (1+2+3+4) = 4 \times 5"),
            MathTex(r"1+2+\dots+n = \frac{n(n+1)}{2}", color=YELLOW),
        ).arrange(DOWN, buff=0.6).move_to(RIGHT * 2.8)
        self.play(Write(algebra[0]), run_time=1.2)
        self.play(Write(algebra[1]), run_time=1.2)
        self.play(Circumscribe(algebra[1], color=YELLOW))
        self.wait(1)
