"""An arrow vector from the origin on a coordinate grid, with coordinate labels at its ends.

tags: vector, arrow, NumberPlane, grid, coordinates, label, still image, basic concepts, Dot, Arrow, NumberPlane, Text
scene: VectorArrow
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Basic Concepts" section of the official ManimCE example gallery.
"""

from manim import *

class VectorArrow(Scene):
    def construct(self):
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        numberplane = NumberPlane()
        origin_text = Text('(0, 0)').next_to(dot, DOWN)
        tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
        self.add(numberplane, dot, arrow, origin_text, tip_text)
