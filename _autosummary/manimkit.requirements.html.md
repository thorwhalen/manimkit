# manimkit.requirements

What rendering needs, whether you have it, and how to get what is missing.

`manimkit` itself is pure Python. Rendering needs the `manim` package (which
brings Cairo, Pango and PyAV) and, for any `MathTex`/`Tex`/numbered axis, a LaTeX
install with `dvisvgm`. [`check_requirements()`](#manimkit.requirements.check_requirements) reports each one with the
command that fixes it on this platform.

```pycon
>>> reqs = check_requirements()
>>> {r.name for r in reqs} >= {'manim', 'latex', 'dvisvgm'}
True
```

### Functions

| [`check_requirements`](#manimkit.requirements.check_requirements)()   | Check manim, LaTeX and dvisvgm; never installs anything.                                                             |
|-------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| [`requirements_report`](#manimkit.requirements.requirements_report)()  | Human-readable [`check_requirements()`](#manimkit.requirements.check_requirements), plus what to do without LaTeX. |

### Classes

| [`Requirement`](#manimkit.requirements.Requirement)(name, ok[, detail, fix, needed_for])   | One dependency: present or not, what we found, how to fix.   |
|-----------------------------------------------------------------------------------------------------|--------------------------------------------------------------|

### *class* manimkit.requirements.Requirement(name, ok, detail='', fix='', needed_for='')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

One dependency: present or not, what we found, how to fix.

### manimkit.requirements.check_requirements()

Check manim, LaTeX and dvisvgm; never installs anything.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`Requirement`](#manimkit.requirements.Requirement)]

### manimkit.requirements.requirements_report()

Human-readable [`check_requirements()`](#manimkit.requirements.check_requirements), plus what to do without LaTeX.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
