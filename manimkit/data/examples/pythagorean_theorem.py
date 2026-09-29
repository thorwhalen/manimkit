"""Visual Pythagorean theorem: squares grow on the sides of a right triangle, areas labelled, a² + b² = c².

tags: geometry, pythagorean theorem, proof, right triangle, squares, area, math concept, visual proof, Polygon, labels, latex
scene: PythagoreanTheorem
source: original (manimkit, MIT)

Build the triangle from explicit vertices, then build each square from a side's two
endpoints and the side's outward normal (so it works for any side). Labels sit at
each square's centre. The equation is assembled from the three area labels with
TransformFromCopy so the viewer sees where each term comes from. The whole figure
is scaled and shifted left to leave room for the equation on the right.
"""

from manim import *

A, B, C = np.array([0, 0, 0]), np.array([3, 0, 0]), np.array([0, 4, 0])  # right angle at A


def square_on(p, q, outward, **style):
    side = q - p
    normal = np.array([-side[1], side[0], 0]) / np.linalg.norm(side)
    if np.dot(normal, outward) < 0:
        normal = -normal
    L = np.linalg.norm(side)
    return Polygon(p, q, q + normal * L, p + normal * L, **style)


class PythagoreanTheorem(Scene):
    def construct(self):
        centroid = (A + B + C) / 3
        tri = Polygon(A, B, C, color=WHITE, stroke_width=4)
        sq_a = square_on(A, B, A - C, color=BLUE, fill_opacity=0.5)       # below side AB (length 3)
        sq_b = square_on(A, C, A - B, color=GREEN, fill_opacity=0.5)      # left of side AC (length 4)
        sq_c = square_on(B, C, (B + C) / 2 - centroid, color=RED, fill_opacity=0.5)  # hypotenuse (length 5)
        right_angle = RightAngle(Line(A, B), Line(A, C), length=0.35)
        figure = VGroup(tri, right_angle, sq_a, sq_b, sq_c)
        figure.scale(0.5).move_to(LEFT * 3 + DOWN * 0.4)  # centre it: to_edge only moves one axis

        labels = VGroup(
            MathTex("a^2 = 9").move_to(sq_a),
            MathTex("b^2 = 16").move_to(sq_b),
            MathTex("c^2 = 25").move_to(sq_c),
        ).scale(0.8)

        title = Text("Pythagorean theorem", font_size=40).to_edge(UP)
        self.play(Write(title), Create(tri), Create(right_angle))
        for sq, lab in zip([sq_a, sq_b, sq_c], labels):
            self.play(DrawBorderThenFill(sq), run_time=1)
            self.play(Write(lab), run_time=0.6)

        eq = MathTex("a^2", "+", "b^2", "=", "c^2").scale(1.4).move_to(RIGHT * 3.5 + UP * 0.5)
        nums = MathTex("9", "+", "16", "=", "25").scale(1.2).next_to(eq, DOWN, buff=0.6)
        self.play(
            TransformFromCopy(labels[0], eq[0]), TransformFromCopy(labels[1], eq[2]),
            TransformFromCopy(labels[2], eq[4]), FadeIn(eq[1]), FadeIn(eq[3]), run_time=1.5,
        )
        self.play(Write(nums))
        self.play(Circumscribe(eq, color=YELLOW))
        self.wait(1.5)
