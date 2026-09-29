"""A dot moves along a circle path, rotates about a point, and follows a line.

tags: move along path, dot, circle, rotate, motion, animations, Circle, Dot, Line, GrowFromCenter, Transform, MoveAlongPath, Rotating
scene: PointMovingOnShapes
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Animations" section of the official ManimCE example gallery.
"""

from manim import *

class PointMovingOnShapes(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        dot = Dot()
        dot2 = dot.copy().shift(RIGHT)
        self.add(dot)

        line = Line([3, 0, 0], [5, 0, 0])
        self.add(line)

        self.play(GrowFromCenter(circle))
        self.play(Transform(dot, dot2))
        self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
        self.play(Rotating(dot, about_point=[2, 0, 0]), run_time=1.5)
        self.wait()
