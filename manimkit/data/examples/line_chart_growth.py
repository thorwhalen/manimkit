"""Line chart that draws itself point by point over time, then calls out the peak with an arrow.

tags: line chart, time series, data, growth, trend, over time, monthly, animated chart, annotation, callout, peak, ValueTracker, story, no latex
scene: LineChartGrowth
source: original (manimkit, MIT)

Axes without numbers (include_numbers needs LaTeX), with Text tick labels placed
via axes.c2p. The line grows with a ValueTracker t (months elapsed) and
always_redraw: the polyline through the data points up to t, with the last
segment interpolated so the growth is smooth, and a leading dot. At the end the
growing line is swapped for a static copy (clear the redraw) before annotating.
The callout label sits in empty space, with an Arrow(buff=0.1) to the point.
"""

from manim import *

MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
VALUES = [12, 14, 13, 17, 21, 24, 30, 28, 26, 33, 41, 38]


class LineChartGrowth(Scene):
    def construct(self):
        title = Text("Visitors per month (thousands)", font_size=34).to_edge(UP)
        axes = Axes(
            x_range=[0, 11, 1], y_range=[0, 50, 10], x_length=10, y_length=4.8,
            axis_config={"include_tip": False}, y_axis_config={"include_ticks": True},
        ).to_edge(DOWN, buff=0.9)
        x_labels = VGroup(*[Text(m, font_size=20).next_to(axes.c2p(i, 0), DOWN, buff=0.2) for i, m in enumerate(MONTHS)])
        y_labels = VGroup(*[Text(str(v), font_size=20).next_to(axes.c2p(0, v), LEFT, buff=0.2) for v in range(10, 51, 10)])
        self.play(Write(title), Create(axes), FadeIn(x_labels), FadeIn(y_labels), run_time=1.5)

        points = [axes.c2p(i, v) for i, v in enumerate(VALUES)]
        t = ValueTracker(0)

        def head():
            k = int(t.get_value())
            frac = t.get_value() - k
            if k >= len(points) - 1:
                return points[-1]
            return points[k] + frac * (points[k + 1] - points[k])

        line = always_redraw(
            lambda: VMobject(color=BLUE, stroke_width=4).set_points_as_corners(
                points[: int(t.get_value()) + 1] + [head()]
            )
        )
        dot = always_redraw(lambda: Dot(head(), color=BLUE_A, radius=0.07))
        self.add(line, dot)
        self.play(t.animate.set_value(len(points) - 1), run_time=5, rate_func=linear)

        # Freeze: replace the redrawn line with a static copy before annotating.
        static = line.copy().clear_updaters()
        self.remove(line, dot)
        self.add(static)
        peak_i = max(range(len(VALUES)), key=VALUES.__getitem__)
        peak = Dot(points[peak_i], color=YELLOW, radius=0.1)
        label = Text(f"Peak: {VALUES[peak_i]}k in November", font_size=26, color=YELLOW)
        label.move_to(axes.c2p(peak_i - 3.5, VALUES[peak_i] + 6))
        arrow = Arrow(label.get_right(), peak.get_center(), buff=0.1, color=YELLOW, stroke_width=3)
        self.play(FadeIn(peak, scale=1.5), GrowArrow(arrow), Write(label), run_time=1.2)
        self.wait(1.5)
