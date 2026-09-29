"""Code walkthrough: a syntax-highlighted listing with a highlight bar stepping through lines, plus notes.

tags: code, programming, source code, syntax highlighting, Code, line highlight, walkthrough, tutorial, explain code, python, no latex
scene: CodeWalkthrough
source: original (manimkit, MIT)

Manim >= 0.19 API: Code(code_string=..., language="python",
formatter_style="monokai", add_line_numbers=True, background="window"). The lines
of the listing are code.code_lines[i] (a VGroup per line) — use them to place a
translucent highlight Rectangle behind the current line and move it with
.animate.move_to. Notes on the right are Transform-ed per step.
"""

from manim import *

SOURCE = '''def mean(xs):
    total = 0
    for x in xs:
        total += x
    return total / len(xs)
'''
NOTES = {0: "Define the function", 1: "Start a running sum", 2: "Visit each value", 3: "Add it to the sum", 4: "Divide by the count"}


class CodeWalkthrough(Scene):
    def construct(self):
        code = Code(code_string=SOURCE, language="python", formatter_style="monokai", add_line_numbers=True, background="window")
        code.scale(0.9).to_edge(LEFT, buff=0.6)
        title = Text("Computing a mean", font_size=36).to_edge(UP)
        self.play(Write(title), FadeIn(code))

        lines = code.code_lines
        bar = Rectangle(width=code.width - 0.2, height=lines[0].height + 0.15, fill_color=YELLOW, fill_opacity=0.2, stroke_width=0)
        bar.move_to([code.get_x(), lines[0].get_y(), 0])
        note = Text(NOTES[0], font_size=30).next_to(code, RIGHT, buff=0.8)
        self.play(FadeIn(bar), FadeIn(note))
        self.wait(0.8)
        for i in range(1, len(lines)):
            new_note = Text(NOTES[i], font_size=30).next_to(code, RIGHT, buff=0.8)
            self.play(bar.animate.set_y(lines[i].get_y()), Transform(note, new_note), run_time=0.7)
            self.wait(0.8)
        self.wait(1)
