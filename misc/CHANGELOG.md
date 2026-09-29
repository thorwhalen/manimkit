# Changelog (AI-made changes)

## 2026-09-29

- Initial release: corpus (21 curated scenes, the 27-scene ManimCE gallery, harvested docstring examples of the installed manim), BM25 search with a `scorer=` seam, lint (wrong-API rules + undefined-name check against the installed manim), `render_check` (child-process render, timeline, layout probe: cut-off / overlap / cramped / text-on-shape / offscreen, beat-end frame sampling, contact sheet, concise errors with LaTeX log excerpts and known-error hints), `check_requirements`, the `manimkit` CLI, and the `manimkit` agent skill. Tested with nine fresh agents on unseen requests over three rounds.
