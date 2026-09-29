"""Vector addition on a grid: two vectors, tip-to-tail, and their resultant, with Text labels.

tags: vectors, vector addition, linear algebra, physics, forces, NumberPlane, Arrow, tip to tail, resultant, grid, coordinates, no latex
scene: VectorAddition
source: original (manimkit, MIT)

On a NumberPlane, plane.c2p(x, y) gives scene points. Arrows use buff=0 so they
start and end exactly on the points. The tip-to-tail step moves a copy of b so its
tail sits on a's tip (b.copy().shift(a.get_end() - b.get_start())). Labels are
placed with next_to on the arrow's midpoint, offset perpendicular-ish.
"""

from manim import *


class VectorAddition(Scene):
    def construct(self):
        plane = NumberPlane(x_range=[-7, 7, 1], y_range=[-4, 4, 1], background_line_style={"stroke_opacity": 0.4})
        o = plane.c2p(0, 0)
        a = Arrow(o, plane.c2p(3, 1), buff=0, color=BLUE)
        b = Arrow(o, plane.c2p(1, 2), buff=0, color=GREEN)
        la = Text("a", font_size=34, color=BLUE).next_to(a.get_center(), DOWN)
        lb = Text("b", font_size=34, color=GREEN).next_to(b.get_center(), LEFT)
        self.play(Create(plane), run_time=1.5)
        self.play(GrowArrow(a), Write(la))
        self.play(GrowArrow(b), Write(lb))
        self.wait(0.5)

        b_moved = b.copy()
        self.play(b_moved.animate.shift(a.get_end() - b.get_start()), run_time=1.5)
        s = Arrow(o, plane.c2p(4, 3), buff=0, color=YELLOW)
        ls = Text("a + b", font_size=34, color=YELLOW).next_to(s.get_end(), UR, buff=0.15)
        self.play(GrowArrow(s), Write(ls))
        coords = Text("(3, 1) + (1, 2) = (4, 3)", font_size=32).to_corner(UL).add_background_rectangle()
        self.play(FadeIn(coords))
        self.wait(1.5)
