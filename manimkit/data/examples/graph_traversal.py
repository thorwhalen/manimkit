"""Network graph with a breadth-first traversal: nodes light up in visiting order, edges highlighted.

tags: graph, network, nodes, edges, BFS, breadth first search, traversal, algorithm, Graph, layout, highlight, computer science, no latex
scene: GraphTraversal
source: original (manimkit, MIT)

Manim's Graph mobject lays nodes out for you (layout="kamada_kawai", "circular",
"tree" ...; tree needs root_vertex). Access a node as g.vertices[v] and an edge as
g.edges[(u, v)] — edge keys are in the order you declared them. Node labels here
are passed as labels={v: Text(...)} so they belong to the vertex and move with
it (labels=True would use LaTeX). Recolour a labelled vertex with
set_fill(..., family=False), or its label is recoloured too and disappears. An
order counter below narrates the visit.
"""

from manim import *
from collections import deque

VERTICES = [1, 2, 3, 4, 5, 6, 7]
EDGES = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]


class GraphTraversal(Scene):
    def construct(self):
        title = Text("Breadth-first search", font_size=40).to_edge(UP)
        g = Graph(
            VERTICES, EDGES, layout="tree", root_vertex=1, layout_scale=3,
            labels={v: Text(str(v), font_size=26) for v in VERTICES},
            vertex_config={"radius": 0.3, "fill_color": GREY_D, "stroke_color": WHITE, "stroke_width": 2, "fill_opacity": 1},
            edge_config={"stroke_color": GREY_B},
        ).shift(DOWN * 0.3)
        self.play(Write(title), Create(g), run_time=2)

        adj = {v: [] for v in VERTICES}
        for u, v in EDGES:
            adj[u].append(v)
            adj[v].append(u)

        order_text = Text("visited:", font_size=28).to_corner(DL, buff=0.6)
        self.play(FadeIn(order_text))
        seen, queue, visited = {1}, deque([1]), VGroup()
        while queue:
            u = queue.popleft()
            # family=False: colour the dot only; the default would also fill its label and hide it.
            self.play(g.vertices[u].animate.set_fill(BLUE, family=False), run_time=0.5)
            tag = Text(str(u), font_size=28, color=BLUE_B)
            tag.next_to(visited[-1] if len(visited) else order_text, RIGHT, buff=0.3)
            visited.add(tag)
            self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.3)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
                    key = (u, w) if (u, w) in g.edges else (w, u)
                    self.play(g.edges[key].animate.set_color(YELLOW), run_time=0.3)
        self.wait(1.5)
