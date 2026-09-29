"""3D camera 'illusion' rotation (precession) around axes and a circle.

tags: 3D, camera, illusion rotation, ThreeDScene, special camera settings, ThreeDScene, ThreeDAxes, begin_3dillusion_camera_rotation, stop_3dillusion_camera_rotation
scene: ThreeDCameraIllusionRotation
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Special Camera Settings" section of the official ManimCE example gallery.
"""

from manim import *

class ThreeDCameraIllusionRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        circle=Circle()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(circle,axes)
        self.begin_3dillusion_camera_rotation(rate=2)
        self.wait(PI/2)
        self.stop_3dillusion_camera_rotation()
