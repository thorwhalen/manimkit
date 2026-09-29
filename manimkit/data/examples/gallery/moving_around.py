"""Shift, recolour, scale and rotate a square with .animate.

tags: animate, move, scale, rotate, color, basic transforms, animations, shift, set_fill, scale, rotate
scene: MovingAround
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Animations" section of the official ManimCE example gallery.
"""

from manim import *

class MovingAround(Scene):
    def construct(self):
        square = Square(color=BLUE, fill_opacity=1)

        self.play(square.animate.shift(LEFT))
        self.play(square.animate.set_fill(ORANGE))
        self.play(square.animate.scale(0.3))
        self.play(square.animate.rotate(0.4))
