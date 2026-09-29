"""Build a raster image from a numpy array and frame it with a rectangle.

tags: image, numpy, raster, gradient, still image, basic concepts, ImageMobject
scene: GradientImageFromArray
source: Manim Community example gallery (docs/source/examples.rst), MIT, (c) the Manim Community Developers

From the "Basic Concepts" section of the official ManimCE example gallery.
"""

from manim import *

class GradientImageFromArray(Scene):
    def construct(self):
        n = 256
        imageArray = np.uint8(
            [[i * 256 / n for i in range(0, n)] for _ in range(0, n)]
        )
        image = ImageMobject(imageArray).scale(2)
        image.background_rectangle = SurroundingRectangle(image, color=GREEN)
        self.add(image, image.background_rectangle)
