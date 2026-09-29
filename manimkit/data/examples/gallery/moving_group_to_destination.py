"""Move a group so that one specific member lands on a target point.

tags: group, move, align, destination, VGroup, animations
scene: MovingGroupToDestination
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Animations" section of the official ManimCE example gallery.
"""

from manim import *

class MovingGroupToDestination(Scene):
    def construct(self):
        group = VGroup(Dot(LEFT), Dot(ORIGIN), Dot(RIGHT, color=RED), Dot(2 * RIGHT)).scale(1.4)
        dest = Dot([4, 3, 0], color=YELLOW)
        self.add(group, dest)
        self.play(group.animate.shift(dest.get_center() - group[2].get_center()))
        self.wait(0.5)
