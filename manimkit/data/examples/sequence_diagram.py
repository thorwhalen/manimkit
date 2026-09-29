"""Sequence diagram: two parties with lifelines exchange numbered messages as arrows, step by step.

tags: sequence diagram, protocol, client server, messages, request response, handshake, networking, lifelines, arrows, message passing, computer science, UML, no latex
scene: SequenceDiagram
source: original (manimkit, MIT)

The standard layout for protocols and APIs: a header box per party at the top,
dashed vertical lifelines (DashedLine), then one horizontal Arrow per message at
successive y positions, with its label just above it. Direction alternates by
choosing start/end x. Messages are data (sender, text), so the scene adapts to
any protocol; the vertical step is computed from the space left so the last
message stays above the bottom margin.
"""

from manim import *

PARTIES = {"client": ("Client", LEFT * 4), "server": ("Server", RIGHT * 4)}
MESSAGES = [
    ("client", "server", "1. GET /page"),
    ("server", "client", "2. 301 redirect to /new"),
    ("client", "server", "3. GET /new"),
    ("server", "client", "4. 200 OK + HTML"),
]
TOP_Y, BOTTOM_Y = 2.2, -3.2


class SequenceDiagram(Scene):
    def construct(self):
        title = Text("Following a redirect", font_size=36).to_edge(UP, buff=0.3)
        heads, lines = {}, VGroup()
        for key, (name, pos) in PARTIES.items():
            label = Text(name, font_size=28)
            box = RoundedRectangle(corner_radius=0.15, width=label.width + 0.6, height=0.7, color=BLUE)
            head = VGroup(box, label).move_to(pos + UP * TOP_Y)
            heads[key] = head
            lines.add(DashedLine(head.get_bottom(), [head.get_x(), BOTTOM_Y, 0], color=GREY_B))
        self.play(Write(title), *[FadeIn(h) for h in heads.values()], run_time=1)
        self.play(Create(lines), run_time=0.8)

        step = (heads["client"].get_bottom()[1] - BOTTOM_Y) / (len(MESSAGES) + 0.5)
        y = heads["client"].get_bottom()[1] - step * 0.75
        for src, dst, text in MESSAGES:
            color = BLUE if src == "client" else ORANGE
            start = [heads[src].get_x(), y, 0]
            end = [heads[dst].get_x(), y, 0]
            arrow = Arrow(start, end, buff=0.05, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.04)
            label = Text(text, font_size=24, color=color).next_to(arrow, UP, buff=0.1)
            self.play(GrowArrow(arrow), FadeIn(label, shift=UP * 0.1), run_time=1.0)
            self.wait(0.5)
            y -= step
        self.wait(1)
