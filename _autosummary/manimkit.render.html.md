# manimkit.render

Render a scene, look at it, and say concisely what went wrong.

[`render_check()`](#manimkit.render.render_check) is the loop an agent runs after every edit: lint, render at
low quality in a child process, sample frames into one contact-sheet PNG (which
the agent then *looks at*), and return a [`RenderReport`](#manimkit.render.RenderReport) whose `str()` is
a short, readable summary: duration, timeline, layout warnings, and — on failure —
the error with the offending lines of *your* file, not forty frames of manim.

### Functions

| [`render_check`](#manimkit.render.render_check)(file[, scene, quality, ...])   | Lint, render `scene` from `file`, sample frames, report.                 |
|----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| [`resolve_scene`](#manimkit.render.resolve_scene)(file[, scene])                | The scene to render: `scene` if given, else the file's only Scene class. |

### Classes

| [`RenderReport`](#manimkit.render.RenderReport)(ok, file[, scene, video, ...])   | What happened when a scene was rendered.   |
|------------------------------------------------------------------------------------------------|--------------------------------------------|

### *class* manimkit.render.RenderReport(ok, file, scene=None, video=None, image=None, contact_sheet=None, frames=<factory>, duration=None, scene_time=None, timeline=<factory>, layout_warnings=<factory>, lint=<factory>, error=None, error_kind=None, user_frames=<factory>, raised_in=None, latex_log=None, hint=None, stderr_tail=None, source_hash=None, unchanged=False, reads=None)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

What happened when a scene was rendered.

#### reads *: [list](https://docs.python.org/3/builtins/stdtypes.html#list) | [None](https://docs.python.org/3/builtins/constants.html#None)* *= None*

every file the render opened for reading and
every folder it listed, outside the Python installation and `out_dir`
(`[{"path", "kind"}]`, `kind` `"file"` or `"dir"`); `None` when
not recorded, or when the render died before reporting.

* **Type:**
  With `record_reads=True`

### manimkit.render.render_check(file, scene=None, , quality='l', n_frames=8, at=(), out_dir=None, probe=True, no_latex=False, lint=True, timeout=600, python=None, record_reads=False)

Lint, render `scene` from `file`, sample frames, report.

* **Parameters:**
  * **quality** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – `l` (480p15, the iteration default), `m`, `h`, `p`, `k`.
  * **n_frames** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – how many frames to sample: taken just before animations end
    (settled states), spread over the timeline; evenly spaced if the probe is
    off. The final frame is always added.
  * **at** ([`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)) – extra timestamps (seconds) to sample, e.g. where a warning points.
  * **out_dir** – where media, frames and the contact sheet go
    (default: `manimkit_renders/<file stem>/` next to the file).
  * **probe** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – record the timeline and check layout after every play/wait.
  * **no_latex** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – fail on the first use of LaTeX, for scenes that must run on a
    machine without a TeX install (this one may well have it).
  * **python** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – interpreter to render with (default: this one).
  * **record_reads** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – 

    record every file the render opens for reading and
    every folder it lists — whatever built the path — in
    [`RenderReport.reads`](#manimkit.render.RenderReport.reads) ([`manimkit.reads.ReadRecorder`](manimkit.reads.html.md#manimkit.reads.ReadRecorder)), so a
    > caller that caches renders can key the files a scene reads by a
    > computed path.
* **Return type:**
  [`RenderReport`](#manimkit.render.RenderReport)

### manimkit.render.resolve_scene(file, scene=None)

The scene to render: `scene` if given, else the file’s only Scene class.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
