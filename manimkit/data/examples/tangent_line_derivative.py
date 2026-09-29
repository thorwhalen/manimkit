"""Derivative as slope: a tangent line slides along a curve while a live readout shows the slope.

tags: calculus, derivative, slope, tangent line, function plot, axes, ValueTracker, always_redraw, DecimalNumber, live value, math education, latex
scene: TangentLineDerivative
source: original (manimkit, MIT)

The canonical ValueTracker pattern: one tracker holds x; the dot, the tangent line
and the numeric readout are all rebuilt from it every frame with always_redraw
(or an updater), and the animation is just tracker.animate.set_value(...).
axes.c2p converts graph coordinates to scene points; axes.plot draws f; the slope
comes from a numeric derivative. Axis numbers and DecimalNumber need LaTeX.
"""

from manim import *


def f(x):
    return 0.25 * x**3 - x


def df(x, h=1e-4):
    return (f(x + h) - f(x - h)) / (2 * h)


class TangentLineDerivative(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1], y_range=[-4, 4, 1], x_length=8, y_length=5.5,
            axis_config={"include_numbers": True, "font_size": 24},
        ).to_edge(DOWN, buff=0.4)
        graph = axes.plot(f, x_range=[-2.8, 2.8], color=BLUE)
        # Place the formula in empty space; get_graph_label next to a steep curve lands on it.
        label = MathTex(r"f(x)=\tfrac14 x^3 - x", color=BLUE).move_to(axes.c2p(1.3, 3.2))
        self.play(Create(axes), run_time=1.2)
        self.play(Create(graph), FadeIn(label))

        x = ValueTracker(-1.8)
        dot = always_redraw(lambda: Dot(axes.c2p(x.get_value(), f(x.get_value())), color=YELLOW))
        tangent = always_redraw(
            lambda: axes.plot(
                lambda t: f(x.get_value()) + df(x.get_value()) * (t - x.get_value()),
                x_range=[x.get_value() - 0.6, x.get_value() + 0.6], color=YELLOW,  # short: steep tangents leave the axes
            )
        )
        readout = always_redraw(
            lambda: VGroup(
                Text("slope =", font_size=30),
                DecimalNumber(df(x.get_value()), num_decimal_places=2, font_size=36),
            ).arrange(RIGHT).to_corner(UL, buff=0.5)
        )
        self.play(FadeIn(dot), Create(tangent), FadeIn(readout))
        self.play(x.animate.set_value(2.2), run_time=5, rate_func=linear)
        self.play(x.animate.set_value(2 / 3**0.5), run_time=1.5)  # where the slope is 0
        flat = Text("slope 0: a local minimum", font_size=28, color=YELLOW).next_to(readout, DOWN, aligned_edge=LEFT)
        self.play(FadeIn(flat))
        self.wait(1)
