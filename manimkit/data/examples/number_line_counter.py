"""A pointer moves along a number line while a live counter shows its value (ValueTracker basics).

tags: number line, pointer, counter, ValueTracker, add_updater, DecimalNumber, live value, basics, arithmetic, latex
scene: NumberLineCounter
source: original (manimkit, MIT)

The smallest complete ValueTracker example: the pointer's position and the
number's value both follow tracker.get_value() through add_updater, and the
animation itself is tracker.animate.set_value(v). NumberLine(include_numbers=True)
and DecimalNumber use LaTeX; for a LaTeX-free version use Text labels with an
updater that rebuilds the Text (become).
"""

from manim import *


class NumberLineCounter(Scene):
    def construct(self):
        line = NumberLine(x_range=[0, 10, 1], length=11, include_numbers=True)
        t = ValueTracker(0)
        pointer = Triangle(fill_opacity=1, color=YELLOW).scale(0.15).rotate(PI)
        pointer.add_updater(lambda m: m.next_to(line.n2p(t.get_value()), UP, buff=0.1))
        value = DecimalNumber(0, num_decimal_places=1, font_size=48)
        value.add_updater(lambda m: m.set_value(t.get_value()).next_to(pointer, UP))
        self.play(Create(line))
        self.play(FadeIn(pointer), FadeIn(value))
        for target in [3, 7.5, 2, 9]:
            self.play(t.animate.set_value(target), run_time=1.5)
            self.wait(0.4)
        self.wait(1)
