"""Linear transformation of the plane: a matrix warps the grid; eigenvectors stay on their span.

tags: linear algebra, matrix, linear transformation, eigenvector, eigenvalue, span, grid warp, LinearTransformationScene, apply_matrix, vectors, 3blue1brown, no latex
scene: LinearTransformationEigenvectors
source: original (manimkit, MIT)

LinearTransformationScene gives you the grid, basis vectors and apply_matrix. Its
one trap: apply_matrix transforms EVERY mobject in the scene unless you register
it as foreground — a title or label added with self.add/self.play and not
registered makes apply_matrix fail with "zip() argument 3 is longer than
arguments 1-2". Register overlays with self.add_foreground_mobject(m) before
showing them; vectors that should move go through self.add_vector(...). Dashed
span lines are added with add_transformable_mobject so they warp with the grid.
"""

from manim import *

MATRIX = [[3, 1], [0, 2]]  # eigenvectors (1, 0) with eigenvalue 3 and (1, -1) with eigenvalue 2


class LinearTransformationEigenvectors(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(show_coordinates=False, show_basis_vectors=False, leave_ghost_vectors=True, **kwargs)

    def construct(self):
        title = Text("Eigenvectors stay on their line", font_size=34).to_edge(UP)
        self.add_foreground_mobject(title)  # overlays must be foreground, or apply_matrix fails
        self.play(FadeIn(title), run_time=0.8)

        spans = VGroup(
            DashedLine([-8, 0, 0], [8, 0, 0], color=YELLOW, stroke_opacity=0.6),
            DashedLine([-5, 5, 0], [5, -5, 0], color=GREEN, stroke_opacity=0.6),
        )
        self.add_transformable_mobject(spans)
        self.play(Create(spans), run_time=0.8)
        e1 = self.add_vector([1, 0], color=YELLOW)
        e2 = self.add_vector([1, -1], color=GREEN)
        other = self.add_vector([1, 1], color=RED)
        self.wait(0.6)

        self.apply_matrix(MATRIX, run_time=3)
        self.wait(0.6)

        note = VGroup(
            Text("yellow: stretched x3, same line", font_size=26, color=YELLOW),
            Text("green: stretched x2, same line", font_size=26, color=GREEN),
            Text("red: knocked off its line", font_size=26, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DL).add_background_rectangle()
        self.add_foreground_mobject(note)
        self.play(FadeIn(note), run_time=0.8)
        self.wait(1.6)
