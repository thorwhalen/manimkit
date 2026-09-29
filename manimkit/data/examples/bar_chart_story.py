"""Data story with a bar chart: bars grow in, one is highlighted, values change, bars re-sort.

tags: data, bar chart, chart, story, comparison, ranking, sort, highlight, statistics, business, grow, no latex
scene: BarChartStory
source: original (manimkit, MIT)

Hand-built bars (Rectangle + Text) instead of BarChart, so it needs no LaTeX and
every piece is addressable. Shows: growing bars from the baseline
(GrowFromEdge), highlighting one bar with Indicate + colour, animating new values
with .animate.stretch_to_fit_height anchored at the bottom (keep the baseline!),
updating value labels, and re-sorting by animating bars to new x positions.
"""

from manim import *

DATA = {"Solar": 3.0, "Wind": 4.5, "Hydro": 2.0, "Gas": 5.0}
NEW = {"Solar": 6.0, "Wind": 5.0, "Hydro": 2.2, "Gas": 3.0}
UNIT = 0.7  # scene units per data unit
BAR_W, GAP = 1.2, 0.5
BASE_Y = -2.8


def x_of(i, n):
    return (i - (n - 1) / 2) * (BAR_W + GAP)


class BarChartStory(Scene):
    def construct(self):
        title = Text("Electricity by source (TWh)", font_size=36).to_edge(UP)
        baseline = Line(LEFT * 4.5, RIGHT * 4.5, color=GREY).set_y(BASE_Y)
        self.play(Write(title), Create(baseline))

        names = list(DATA)
        bars, labels, values = VGroup(), VGroup(), VGroup()
        for i, name in enumerate(names):
            h = DATA[name] * UNIT
            bar = Rectangle(width=BAR_W, height=h, fill_opacity=0.85, fill_color=BLUE, stroke_width=0)
            bar.move_to([x_of(i, len(names)), BASE_Y + h / 2, 0])
            label = Text(name, font_size=24).next_to(bar, DOWN, buff=0.25).set_y(BASE_Y - 0.35)
            value = Text(f"{DATA[name]:g}", font_size=24).next_to(bar, UP, buff=0.15)
            bars.add(bar), labels.add(label), values.add(value)

        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), FadeIn(labels))
        self.play(FadeIn(values))
        self.wait(0.5)

        # Highlight one bar.
        solar = bars[0]
        self.play(solar.animate.set_fill(YELLOW), Indicate(labels[0], color=YELLOW))
        self.wait(0.5)

        # New values: stretch each bar keeping its bottom on the baseline.
        anims = []
        for i, name in enumerate(names):
            h = NEW[name] * UNIT
            anims.append(bars[i].animate.stretch_to_fit_height(h).move_to([bars[i].get_x(), BASE_Y + h / 2, 0]))
            new_val = Text(f"{NEW[name]:g}", font_size=24).move_to([bars[i].get_x(), BASE_Y + h + 0.3, 0])
            anims.append(Transform(values[i], new_val))
        self.play(*anims, run_time=1.5)
        self.wait(0.5)

        # Re-sort, tallest first: move each (bar, label, value) column to its new slot.
        order = sorted(range(len(names)), key=lambda i: -NEW[names[i]])
        moves = []
        for slot, i in enumerate(order):
            dx = x_of(slot, len(names)) - bars[i].get_x()
            moves.append(VGroup(bars[i], labels[i], values[i]).animate.shift(RIGHT * dx))
        self.play(*moves, run_time=1.5)
        caption = Text("Solar is now the largest source", font_size=30, color=YELLOW).next_to(title, DOWN)
        self.play(FadeIn(caption, shift=DOWN * 0.2))
        self.wait(1.5)
