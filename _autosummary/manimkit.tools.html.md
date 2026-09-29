# manimkit.tools

CLI-shaped wrappers: each returns the text an agent (or a human) reads.

The business logic lives in the other modules and returns data; these functions
only format it. `manimkit/__main__.py` dispatches this SSOT list with `cw`.

### Functions

| [`check`](#manimkit.tools.check)()                                         | Report whether manim, LaTeX and dvisvgm are available, and how to install what is missing.   |
|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| [`lint`](#manimkit.tools.lint)(file)                                      | Static checks for common ManimCE mistakes (ManimGL names, removed APIs, LaTeX traps).        |
| [`list_examples`](#manimkit.tools.list_examples)(\*[, origin])                     | List example ids and titles (origin: curated, gallery, api, or all).                         |
| [`render`](#manimkit.tools.render)(file[, scene, quality, frames, at, ...]) | Render SCENE from FILE (low quality by default), sample frames into a contact sheet, report. |
| [`search`](#manimkit.tools.search)(query, \*[, k, code, no_latex, origin])  | Find corpus examples for QUERY (plain words: 'bar chart race', 'move dot along curve').      |
| [`show`](#manimkit.tools.show)(example_id)                                | Print an example's metadata and full, runnable source.                                       |
| [`skill_path`](#manimkit.tools.skill_path)()                                    | Print the folder of the agent skills shipped with manimkit (to link into ~/.claude/skills).  |

### manimkit.tools.check()

Report whether manim, LaTeX and dvisvgm are available, and how to install what is missing.

### manimkit.tools.lint(file)

Static checks for common ManimCE mistakes (ManimGL names, removed APIs, LaTeX traps).

### manimkit.tools.list_examples(, origin='curated')

List example ids and titles (origin: curated, gallery, api, or all).

### manimkit.tools.render(file, scene='', , quality='l', frames=8, at='', out_dir='', no_latex=False)

Render SCENE from FILE (low quality by default), sample frames into a contact sheet, report.

–quality l|m|h|p|k (480p15, 720p30, 1080p60, 1440p60, 2160p60). –at 1.5,4 adds
frames at those seconds. –no-latex fails on any use of LaTeX (for machines without
TeX). Each run overwrites the previous frames and contact sheet.
Exit code 1 if the render failed.

### manimkit.tools.search(query, , k=5, code=False, no_latex=False, origin='')

Find corpus examples for QUERY (plain words: ‘bar chart race’, ‘move dot along curve’).

–code prints each hit’s full source; –no-latex skips examples that need LaTeX;
–origin curated|gallery|api restricts the source.

### manimkit.tools.show(example_id)

Print an example’s metadata and full, runnable source.

### manimkit.tools.skill_path()

Print the folder of the agent skills shipped with manimkit (to link into ~/.claude/skills).
