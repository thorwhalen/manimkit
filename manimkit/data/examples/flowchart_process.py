"""Process / pipeline diagram: labelled boxes joined by arrows, a token travelling through the steps.

tags: process, flowchart, pipeline, workflow, diagram, boxes, arrows, steps, flow, token, highlight, system design, no latex
scene: FlowchartProcess
source: original (manimkit, MIT)

Boxes are RoundedRectangle + Text grouped per step and laid out with
arrange(RIGHT, buff=...), so spacing is automatic and nothing overlaps. Arrows
connect box edges (get_right -> get_left) with buff so tips do not touch text. A
Dot moves along each arrow with MoveAlongPath while the current step is
highlighted; a caption at the bottom narrates each step (Transform the caption,
do not stack new Text on top of the old one).
"""

from manim import *

STEPS = ["Request", "Validate", "Process", "Respond"]
CAPTIONS = [
    "A request arrives",
    "Its input is checked",
    "The work is done",
    "The answer goes back",
]


def make_step(label):
    text = Text(label, font_size=28)
    box = RoundedRectangle(corner_radius=0.2, width=text.width + 0.6, height=1.0, color=BLUE)
    return VGroup(box, text)


class FlowchartProcess(Scene):
    def construct(self):
        title = Text("A request's journey", font_size=40).to_edge(UP)
        steps = VGroup(*[make_step(s) for s in STEPS]).arrange(RIGHT, buff=0.9)
        steps.scale_to_fit_width(min(steps.width, config.frame_width - 1.0))
        arrows = VGroup(*[
            Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.1, max_tip_length_to_length_ratio=0.3)
            for i in range(len(steps) - 1)
        ])
        self.play(Write(title))
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in steps], lag_ratio=0.25), run_time=1.5)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.25))

        caption = Text(CAPTIONS[0], font_size=30, color=GREY_A).to_edge(DOWN, buff=0.8)
        token = Dot(color=YELLOW, radius=0.12).move_to(steps[0].get_left() + LEFT * 0.4)
        self.play(FadeIn(token), steps[0][0].animate.set_fill(BLUE, opacity=0.35), FadeIn(caption))
        self.wait(0.6)
        for i, arrow in enumerate(arrows):
            new_caption = Text(CAPTIONS[i + 1], font_size=30, color=GREY_A).move_to(caption)
            self.play(
                MoveAlongPath(token, Line(arrow.get_start(), arrow.get_end())),
                steps[i][0].animate.set_fill(opacity=0),
                steps[i + 1][0].animate.set_fill(BLUE, opacity=0.35),
                Transform(caption, new_caption),
                run_time=1.0,
            )
            self.wait(0.6)
        self.play(Flash(steps[-1], color=YELLOW), FadeOut(token))
        self.wait(1)
