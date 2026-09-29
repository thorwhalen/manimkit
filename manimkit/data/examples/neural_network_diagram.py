"""Neural network diagram: layers of neurons connected by edges, a forward pass pulses through.

tags: neural network, machine learning, deep learning, layers, neurons, diagram, forward pass, perceptron, AI, ShowPassingFlash, no latex
scene: NeuralNetworkDiagram
source: original (manimkit, MIT)

Each layer is a VGroup of Circles arranged DOWN; the layers are arranged RIGHT
with a wide buff. Edges are Lines between every pair of neurons in adjacent
layers, drawn *behind* the neurons (add edges first, or set_z_index). A forward
pass is ShowPassingFlash over copies of each layer's edges, followed by the next
layer lighting up. Layer captions sit under each column.
"""

from manim import *

SIZES = [3, 5, 5, 2]
NAMES = ["input", "hidden", "hidden", "output"]


class NeuralNetworkDiagram(Scene):
    def construct(self):
        layers = VGroup(*[
            VGroup(*[Circle(radius=0.25, color=WHITE, fill_color=BLACK, fill_opacity=1) for _ in range(n)]).arrange(DOWN, buff=0.35)
            for n in SIZES
        ]).arrange(RIGHT, buff=2.0).shift(UP * 0.2)
        edges = VGroup(*[
            VGroup(*[Line(a.get_center(), b.get_center(), stroke_width=1.5, color=GREY_C) for a in l1 for b in l2])
            for l1, l2 in zip(layers[:-1], layers[1:])
        ])
        captions = VGroup(*[Text(n, font_size=24, color=GREY_B).next_to(l, DOWN, buff=0.4) for n, l in zip(NAMES, layers)])
        captions.align_to(captions[0], UP)  # same baseline for all
        for c, l in zip(captions, layers):
            c.set_x(l.get_x())
        title = Text("A small neural network", font_size=40).to_edge(UP)

        self.play(Write(title))
        self.add(edges)  # added first so neurons stay on top
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in layers], lag_ratio=0.3), Create(edges), run_time=2)
        self.play(FadeIn(captions))

        self.play(layers[0].animate.set_fill(BLUE, opacity=1), run_time=0.5)
        for i, e in enumerate(edges):
            self.play(ShowPassingFlash(e.copy().set_color(YELLOW).set_stroke(width=3), time_width=0.5), run_time=1)
            self.play(layers[i + 1].animate.set_fill(BLUE, opacity=1), run_time=0.4)
        self.play(Indicate(layers[-1], color=YELLOW))
        self.wait(1)
