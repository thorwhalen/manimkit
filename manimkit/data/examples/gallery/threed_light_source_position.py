"""A 3D parametric surface (sphere) lit from a chosen light source position.

tags: 3D, surface, light, sphere, ThreeDScene, still image, special camera settings, ThreeDScene, ThreeDAxes, Surface, set_camera_orientation
scene: ThreeDLightSourcePosition
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Special Camera Settings" section of the official ManimCE example gallery.
"""

from manim import *

class ThreeDLightSourcePosition(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        sphere = Surface(
            lambda u, v: np.array([
                1.5 * np.cos(u) * np.cos(v),
                1.5 * np.cos(u) * np.sin(v),
                1.5 * np.sin(u)
            ]), v_range=[0, TAU], u_range=[-PI / 2, PI / 2],
            checkerboard_colors=[RED_D, RED_E], resolution=(15, 32)
        )
        self.renderer.camera.light_source.move_to(3*IN) # changes the source of the light
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(axes, sphere)
