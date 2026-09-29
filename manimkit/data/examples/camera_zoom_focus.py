"""Camera zoom: show a whole diagram, zoom into one detail, then pull back out (MovingCameraScene).

tags: camera, zoom, zoom in, focus, detail, MovingCameraScene, frame, pan, save_state, restore, no latex
scene: CameraZoomFocus
source: original (manimkit, MIT)

Subclass MovingCameraScene, then animate self.camera.frame like any mobject:
frame.animate.set(width=...).move_to(target) zooms and pans in one move.
frame.save_state() before and Restore(frame) after returns to the full view.
Text sized for the zoomed view looks tiny in the full view — size it for where it
is read.
"""

from manim import *


class CameraZoomFocus(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        cells = VGroup(*[Square(0.9, color=BLUE_D, fill_opacity=0.3) for _ in range(24)]).arrange_in_grid(4, 6, buff=0.15)
        target = cells[9]
        detail = VGroup(
            Text("cell 9", font_size=14),
            Text("value: 0.42", font_size=10, color=YELLOW),
        ).arrange(DOWN, buff=0.05).move_to(target)
        title = Text("A grid of cells", font_size=40).to_edge(UP)
        self.play(Write(title), LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.03), run_time=2)
        self.play(target.animate.set_fill(YELLOW, opacity=0.4))

        frame.save_state()
        self.play(frame.animate.set(width=target.width * 3).move_to(target), run_time=2)
        self.play(FadeIn(detail))
        self.wait(1.5)
        self.play(Restore(frame), run_time=2)
        self.wait(1)
