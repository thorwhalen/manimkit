"""Cyclic process diagram: stages placed around a circle, curved arrows between them, a token going round.

tags: cycle, cyclic process, loop, circular diagram, life cycle, feedback loop, stages, curved arrows, path_arc, round, iteration, water cycle, no latex
scene: CycleDiagram
source: original (manimkit, MIT)

Stages sit at equal angles on a circle (clockwise from 12 o'clock: angle =
PI/2 - k*TAU/n). Curved arrows between neighbours use Arrow(..., path_arc=a):
a NEGATIVE arc bends clockwise-outward for a clockwise cycle; start/end are
pulled in toward each box with buff so tips never touch the text. The token
follows an ArcBetweenPoints with the same angle, so it rides the arrow. The
active stage is highlighted and a caption in the centre, width-capped to the free
space between the boxes, is Transform-ed each step.
"""

from manim import *

STAGES = ["Plan", "Build", "Measure", "Learn"]
CAPTIONS = ["decide what to try", "make the smallest version", "collect real data", "adjust the plan"]
RADIUS = 2.7
CAPTION_MAX_W = 3.2  # the empty centre between the side boxes
ARC = -PI / 3  # negative: clockwise bend for a clockwise cycle


def stage_box(name):
    text = Text(name, font_size=30)
    box = RoundedRectangle(corner_radius=0.2, width=text.width + 0.6, height=0.9, color=TEAL, fill_color=BLACK, fill_opacity=1)
    return VGroup(box, text)


class CycleDiagram(Scene):
    def construct(self):
        n = len(STAGES)
        center = DOWN * 0.3
        nodes = VGroup()
        for k, name in enumerate(STAGES):
            angle = PI / 2 - k * TAU / n
            nodes.add(stage_box(name).move_to(center + RADIUS * np.array([np.cos(angle), np.sin(angle), 0])))
        arrows = VGroup(*[
            Arrow(nodes[k].get_center(), nodes[(k + 1) % n].get_center(), path_arc=ARC, buff=0.9, color=GREY_B, stroke_width=4)
            for k in range(n)
        ])
        title = Text("The build-measure-learn loop", font_size=36).to_edge(UP, buff=0.3)
        self.add(arrows)  # arrows first so boxes (opaque fill) sit on top
        self.play(Write(title), LaggedStart(*[FadeIn(nd, scale=0.8) for nd in nodes], lag_ratio=0.2), run_time=1.5)
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.2), run_time=1.2)

        def make_caption(text):  # capped to the free centre, so it never runs into the side boxes
            c = Text(text, font_size=26, color=YELLOW)
            return c.scale_to_fit_width(min(c.width, CAPTION_MAX_W)).move_to(center)

        caption = make_caption(CAPTIONS[0])
        token = Dot(color=YELLOW, radius=0.12).move_to(arrows[0].get_start())
        self.play(nodes[0][0].animate.set_stroke(YELLOW, width=6), FadeIn(caption), FadeIn(token), run_time=0.6)
        for k in range(n):
            nxt = (k + 1) % n
            path = ArcBetweenPoints(arrows[k].get_start(), arrows[k].get_end(), angle=ARC)
            new_caption = make_caption(CAPTIONS[nxt])
            self.play(
                MoveAlongPath(token, path),
                nodes[k][0].animate.set_stroke(TEAL, width=4),
                nodes[nxt][0].animate.set_stroke(YELLOW, width=6),
                Transform(caption, new_caption),
                run_time=1.2,
            )
            self.wait(0.3)
        self.play(FadeOut(token), Indicate(nodes[0]))
        self.wait(0.8)
