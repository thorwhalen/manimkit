"""Rotate the camera around a 3D scene (ambient camera rotation), then restore the orientation.

tags: 3D, camera rotation, ThreeDScene, orbit, special camera settings, ThreeDScene, ThreeDAxes, begin_ambient_camera_rotation, stop_ambient_camera_rotation
scene: ThreeDCameraRotation
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Special Camera Settings" section of the official ManimCE example gallery.
"""

from manim import *

class ThreeDCameraRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        circle=Circle()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(circle,axes)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait()
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
        self.wait()
