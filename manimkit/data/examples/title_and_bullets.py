"""Title, subtitle and bullet points revealed one at a time, then a clean section change.

tags: title, subtitle, bullet points, slides, presentation, text, layout, arrange, section transition, intro
scene: TitleAndBullets
source: original (manimkit, MIT)

The layout pattern most explainers need: a title pinned to the top edge, a body
column built with VGroup(...).arrange(DOWN, aligned_edge=LEFT), width-capped so it
can never run off-screen, and a FadeOut of the whole section before the next one.
No LaTeX needed (Text only).
"""

from manim import *

MAX_WIDTH = config.frame_width - 1.5  # keep a margin on both sides


class TitleAndBullets(Scene):
    def construct(self):
        title = Text("How a rainbow forms", font_size=48).to_edge(UP)
        subtitle = Text("three steps", font_size=28, color=GREY_B).next_to(title, DOWN)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(0.5)

        bullets = VGroup(
            Text("1. Sunlight enters a raindrop and bends", font_size=32),
            Text("2. It reflects off the back of the drop", font_size=32),
            Text("3. It bends again on the way out, split by colour", font_size=32),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        if bullets.width > MAX_WIDTH:
            bullets.scale_to_fit_width(MAX_WIDTH)
        bullets.next_to(subtitle, DOWN, buff=0.8)

        for b in bullets:  # one beat per bullet, with time to read it
            self.play(FadeIn(b, shift=RIGHT * 0.3), run_time=0.8)
            self.wait(0.7)

        # Section change: clear everything but the title, then show the next idea.
        self.play(FadeOut(subtitle), FadeOut(bullets))
        takeaway = Text("Every colour leaves at its own angle", font_size=36, color=YELLOW)
        self.play(Write(takeaway))
        self.wait(1.5)
