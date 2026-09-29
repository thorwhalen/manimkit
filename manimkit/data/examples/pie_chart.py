"""Pie chart from data: sectors sweep in with percentages and a legend, one slice pops out.

tags: pie chart, donut chart, proportions, percentages, data, share, legend, chart, Sector, AnnularSector, statistics, no latex
scene: PieChart
source: original (manimkit, MIT)

Manim has no PieChart: build one from Sector (or AnnularSector for a donut) with
start_angle / angle computed from cumulative shares. Percent labels sit at the
sector's mid-angle, a bit outside the middle radius. A slice "pops" by shifting
along its mid-angle direction. The legend is a VGroup of (Square, Text) rows
arranged DOWN with aligned_edge=LEFT.
"""

from manim import *

DATA = [("Rent", 40, BLUE), ("Food", 25, GREEN), ("Transport", 15, ORANGE), ("Savings", 20, PURPLE)]
RADIUS = 2.4


class PieChart(Scene):
    def construct(self):
        title = Text("Monthly budget", font_size=40).to_edge(UP)
        total = sum(v for _, v, _ in DATA)
        center = LEFT * 2.5 + DOWN * 0.4
        start = PI / 2
        sectors, labels = VGroup(), VGroup()
        for name, v, color in DATA:
            angle = -TAU * v / total  # clockwise from 12 o'clock
            sec = Sector(radius=RADIUS, start_angle=start, angle=angle, color=color, fill_opacity=0.9, stroke_color=BLACK, stroke_width=3)
            sec.shift(center)
            mid = start + angle / 2
            sec.mid_dir = np.array([np.cos(mid), np.sin(mid), 0])
            labels.add(Text(f"{v * 100 // total}%", font_size=28).move_to(center + sec.mid_dir * RADIUS * 0.62))
            sectors.add(sec)
            start += angle

        legend = VGroup(*[
            VGroup(Square(0.35, fill_color=c, fill_opacity=1, stroke_width=0), Text(n, font_size=28)).arrange(RIGHT, buff=0.25)
            for n, _, c in DATA
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.35).to_edge(RIGHT, buff=1.5)

        self.play(Write(title))
        self.play(LaggedStart(*[Create(s) for s in sectors], lag_ratio=0.6), run_time=2.5)
        self.play(FadeIn(labels), FadeIn(legend, shift=LEFT * 0.3))
        self.wait(0.8)
        pop = sectors[3]
        self.play(VGroup(pop, labels[3]).animate.shift(pop.mid_dir * 0.4), Indicate(legend[3]))
        note = Text("Savings: one fifth", font_size=30, color=PURPLE_A).next_to(legend, DOWN, buff=0.8)
        self.play(Write(note))
        self.wait(1.5)
