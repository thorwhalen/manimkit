"""Step-by-step equation derivation: solve for x, terms morphing between steps, final answer boxed.

tags: equation, algebra, derivation, solve, MathTex, TransformMatchingTex, substrings, color terms, highlight, box answer, math, latex
scene: EquationDerivation
source: original (manimkit, MIT)

Each step is a MathTex built from separate string pieces, so TransformMatchingTex
can match identical pieces between steps and move them instead of redrawing.
Steps replace each other in place (ReplacementTransform keeps variables honest:
after it, the old mobject is gone from the scene). Colour one symbol everywhere
with set_color_by_tex, box the result with SurroundingRectangle, and keep a small
explanatory Text under the equation, transformed per step. Needs LaTeX.
"""

from manim import *


class EquationDerivation(Scene):
    def construct(self):
        title = Text("Solve for x", font_size=40).to_edge(UP)
        self.play(Write(title))

        steps = [
            MathTex("3", "x", "+", "5", "=", "20"),
            MathTex("3", "x", "=", "20", "-", "5"),
            MathTex("3", "x", "=", "15"),
            MathTex("x", "=", r"\frac{15}{3}"),
            MathTex("x", "=", "5"),
        ]
        notes = [
            "Start",
            "Subtract 5 from both sides",
            "Simplify",
            "Divide both sides by 3",
            "Done",
        ]
        for s in steps:
            s.scale(1.4).set_color_by_tex("x", YELLOW)

        eq = steps[0]
        note = Text(notes[0], font_size=28, color=GREY_B).next_to(eq, DOWN, buff=0.8)
        self.play(Write(eq), FadeIn(note))
        self.wait(0.8)
        for nxt, text in zip(steps[1:], notes[1:]):
            new_note = Text(text, font_size=28, color=GREY_B).next_to(nxt, DOWN, buff=0.8)
            self.play(TransformMatchingTex(eq, nxt), Transform(note, new_note), run_time=1.2)
            eq = nxt
            self.wait(0.8)

        box = SurroundingRectangle(eq, color=GREEN, buff=0.2)
        self.play(Create(box), Indicate(eq, color=GREEN))
        self.wait(1.5)
