"""Horizontal timeline: dated events pop up alternately above and below an axis line, then a highlight.

tags: timeline, history, events, dates, chronology, milestones, roadmap, axis, labels, alternating, no latex
scene: TimelineEvents
source: original (manimkit, MIT)

Map a year to x with a small linear function, put a tick and a Dot at each
event, and alternate labels above/below so neighbours never overlap. Labels are
two-line VGroups (year + caption) built with arrange(DOWN). Everything is kept
inside the frame by construction (x range chosen from the frame width).
"""

from manim import *

EVENTS = [
    (1903, "First powered flight"),
    (1927, "Solo Atlantic crossing"),
    (1947, "Sound barrier broken"),
    (1969, "Moon landing"),
    (2004, "Private spaceflight"),
]
X_MIN, X_MAX = -6.0, 6.0


def year_to_x(y, y0=1895, y1=2012):
    return X_MIN + (y - y0) / (y1 - y0) * (X_MAX - X_MIN)


class TimelineEvents(Scene):
    def construct(self):
        title = Text("A century of flight", font_size=40).to_edge(UP)
        axis = Arrow([X_MIN - 0.4, 0, 0], [X_MAX + 0.4, 0, 0], buff=0, stroke_width=3)
        self.play(Write(title), GrowArrow(axis))

        cards = VGroup()
        for k, (year, text) in enumerate(EVENTS):
            x = year_to_x(year)
            dot = Dot([x, 0, 0], color=YELLOW)
            card = VGroup(
                Text(str(year), font_size=26, color=YELLOW),
                Text(text, font_size=20),
            ).arrange(DOWN, buff=0.1)
            side = UP if k % 2 == 0 else DOWN
            card.next_to(dot, side, buff=0.6)
            stem = Line(dot.get_center(), card.get_edge_center(-side), stroke_width=2, color=GREY_B)
            self.play(FadeIn(dot, scale=1.5), Create(stem), FadeIn(card, shift=side * 0.3), run_time=0.9)
            self.wait(0.4)
            cards.add(VGroup(dot, stem, card))

        self.play(Circumscribe(cards[3], color=YELLOW), cards[3][2][1].animate.set_color(YELLOW))
        self.wait(1.5)
