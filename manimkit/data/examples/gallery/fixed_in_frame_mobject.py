"""3D axes with a 2D text label fixed in the frame (stays readable while the camera is 3D).

tags: 3D, ThreeDScene, fixed in frame, title, overlay, still image, special camera settings, ThreeDScene, set_camera_orientation, add_fixed_in_frame_mobjects
scene: FixedInFrameMObjectTest
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Special Camera Settings" section of the official ManimCE example gallery.
"""

from manim import *

class FixedInFrameMObjectTest(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        text3d = Text("This is a 3D text")
        self.add_fixed_in_frame_mobjects(text3d)
        text3d.to_corner(UL)
        self.add(axes)
        self.wait()
