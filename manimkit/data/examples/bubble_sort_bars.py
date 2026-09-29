"""Sorting algorithm visualised: bubble sort on bars, compared pairs highlighted, swaps animated.

tags: sorting, bubble sort, algorithm, bars, swap, array, comparison, computer science, step by step, no latex
scene: BubbleSortBars
source: original (manimkit, MIT)

Keep a Python list of the bar mobjects in their *current* order and swap entries
in it whenever you swap on screen; position is then always slot_x(i). A swap is
two .animate.move_to calls in one play. Compared pairs flash colour and return.
Values are drawn as Text inside each bar's group so they travel with it. For long
arrays, shorten run_time per step (the total is roughly comparisons x run_time).
"""

from manim import *

VALUES = [5, 2, 8, 1, 6, 3]
UNIT, BAR_W, GAP, BASE_Y = 0.55, 0.9, 0.3, -2.5


def slot_x(i, n):
    return (i - (n - 1) / 2) * (BAR_W + GAP)


class BubbleSortBars(Scene):
    def construct(self):
        title = Text("Bubble sort", font_size=40).to_edge(UP)
        n = len(VALUES)
        bars = []
        for i, v in enumerate(VALUES):
            rect = Rectangle(width=BAR_W, height=v * UNIT, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
            num = Text(str(v), font_size=26).next_to(rect, UP, buff=0.1)
            col = VGroup(rect, num)
            col.move_to([slot_x(i, n), 0, 0]).align_to([0, BASE_Y, 0], DOWN)
            col.value = v
            bars.append(col)
        self.play(Write(title), LaggedStart(*[FadeIn(b, shift=UP * 0.3) for b in bars], lag_ratio=0.1))

        for end in range(n - 1, 0, -1):
            for i in range(end):
                a, b = bars[i], bars[i + 1]
                self.play(a[0].animate.set_fill(YELLOW), b[0].animate.set_fill(YELLOW), run_time=0.25)
                if a.value > b.value:
                    self.play(a.animate.set_x(slot_x(i + 1, n)), b.animate.set_x(slot_x(i, n)), run_time=0.4)
                    bars[i], bars[i + 1] = b, a
                self.play(bars[i][0].animate.set_fill(BLUE), bars[i + 1][0].animate.set_fill(BLUE), run_time=0.15)
            self.play(bars[end][0].animate.set_fill(GREEN), run_time=0.2)
        self.play(bars[0][0].animate.set_fill(GREEN))
        self.wait(1)
