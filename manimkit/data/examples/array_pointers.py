"""Array algorithm with index pointers: binary search narrowing lo / mid / hi over a row of cells.

tags: array, list, cells, index, pointers, lo hi mid, binary search, two pointers, sliding window, search, algorithm, range narrowing, eliminate, computer science, no latex
scene: ArrayPointers
source: original (manimkit, MIT)

The layout most array algorithms need: a row of (Square, Text) cells with their
indices underneath, and labelled pointer arrows that move: mid above the cells, lo and hi below the index row
with their names on opposite sides, so no two labels collide when pointers meet. Eliminated cells dim. Two rules this example follows:
build each pointer once and MOVE it (never re-create per step), and in one play
touch each mobject with at most one .animate — here the cell squares are dimmed
in one play and the numbers in the same play as separate mobjects, never the
group and its child at once (the later animation silently wins).
"""

from manim import *

VALUES = [3, 8, 12, 17, 21, 25, 30, 33, 37, 41, 46, 52, 58, 63, 70]
TARGET = 37
CELL = 0.75


def pointer(name, color, *, below=False, label_side=UP):
    """An arrow pointing at a cell from above (or from below), with its name beside it."""
    arrow = Arrow(DOWN * 0.6 if below else UP * 0.6, ORIGIN, buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.35)
    label = Text(name, font_size=22, color=color).next_to(arrow, label_side, buff=0.05)
    return VGroup(label, arrow)


class ArrayPointers(Scene):
    def construct(self):
        title = Text(f"Binary search for {TARGET}", font_size=36).to_edge(UP)
        squares = VGroup(*[Square(CELL, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.6) for _ in VALUES]).arrange(RIGHT, buff=0)
        squares.scale_to_fit_width(min(squares.width, config.frame_width - 1)).shift(DOWN * 0.3)
        numbers = VGroup(*[Text(str(v), font_size=22).move_to(sq) for v, sq in zip(VALUES, squares)])
        indices = VGroup(*[Text(str(i), font_size=16, color=GREY_B).next_to(sq, DOWN, buff=0.1) for i, sq in enumerate(squares)])
        self.play(Write(title), FadeIn(squares), FadeIn(numbers), FadeIn(indices), run_time=1.2)

        # mid points down from above; lo and hi point up from below the index row, with
        # their names on opposite sides, so they stay readable when they meet.
        lo_p = pointer("lo", GREEN, below=True, label_side=LEFT)
        hi_p = pointer("hi", RED, below=True, label_side=RIGHT)
        mid_p = pointer("mid", YELLOW)

        def under(p, i):  # place a below-pointer's arrow tip under cell i
            return p.animate.shift(squares[i].get_bottom() + DOWN * 0.45 - p[1].get_end())

        lo, hi = 0, len(VALUES) - 1
        lo_p.shift(squares[lo].get_bottom() + DOWN * 0.45 - lo_p[1].get_end())
        hi_p.shift(squares[hi].get_bottom() + DOWN * 0.45 - hi_p[1].get_end())
        self.play(FadeIn(lo_p), FadeIn(hi_p), run_time=0.6)
        status = Text("start: the whole array", font_size=26).to_edge(DOWN, buff=0.8)
        self.play(FadeIn(status), run_time=0.4)

        while lo <= hi:
            mid = (lo + hi) // 2
            target_mid = mid_p.copy().next_to(squares[mid], UP, buff=0.1)
            if mid_p not in self.mobjects:
                mid_p.move_to(target_mid)
                self.play(FadeIn(mid_p), run_time=0.5)
            else:
                self.play(mid_p.animate.move_to(target_mid), run_time=0.5)
            if VALUES[mid] == TARGET:
                self.play(squares[mid].animate.set_fill(GREEN, opacity=0.9), Transform(status, Text(f"found {TARGET} at index {mid}", font_size=26, color=GREEN).move_to(status)), run_time=0.8)
                break
            go_right = VALUES[mid] < TARGET
            drop = range(lo, mid + 1) if go_right else range(mid, hi + 1)
            msg = f"{VALUES[mid]} < {TARGET}: keep the right half" if go_right else f"{VALUES[mid]} > {TARGET}: keep the left half"
            lo, hi = (mid + 1, hi) if go_right else (lo, mid - 1)
            self.play(
                *[squares[i].animate.set_fill(GREY_E, opacity=0.3).set_stroke(GREY_D) for i in drop],
                *[numbers[i].animate.set_opacity(0.3) for i in drop],
                Transform(status, Text(msg, font_size=26).move_to(status)),
                run_time=0.7,
            )
            self.play(under(lo_p, lo), under(hi_p, hi), run_time=0.5)
        self.wait(1.2)
