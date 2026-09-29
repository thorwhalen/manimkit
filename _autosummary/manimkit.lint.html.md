# manimkit.lint

Static checks for the mistakes LLMs make most when writing ManimCE code.

Two kinds of check, both before any render:

- **rules**: a list of known wrong-API patterns (ManimGL names, pre-0.18 names,
  LaTeX-in-a-Python-string traps), each with the right replacement;
- **names**: every capitalised name the file uses but does not define is looked up
  in the *installed* manim; a miss is reported with close matches. This catches
  hallucinated classes and colour constants that no rule list anticipates.

```pycon
>>> issues = lint_code("from manim import *\nclass S(Scene):\n"
...                    "    def construct(self):\n"
...                    "        self.play(ShowCreation(Circle()))\n", check_names=False)
>>> issues[0].message
'`ShowCreation` is ManimGL / pre-0.10 — ManimCE uses `Create(mob)`.'
```

### Functions

| [`lint_code`](#manimkit.lint.lint_code)(code, \*[, check_names])   | Lint Manim source code.   |
|---------------------------------------------------------------------------------------|---------------------------|
| [`lint_scene`](#manimkit.lint.lint_scene)(path)                     | Lint a scene file.        |

### Classes

| [`LintIssue`](#manimkit.lint.LintIssue)(line, message[, kind])   | One finding: where, what, and (usually) the fix.   |
|-------------------------------------------------------------------------------------|----------------------------------------------------|

### *class* manimkit.lint.LintIssue(line, message, kind='rule')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

One finding: where, what, and (usually) the fix.

### manimkit.lint.lint_code(code, , check_names=True)

Lint Manim source code. `check_names` imports manim (about a second).

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`LintIssue`](#manimkit.lint.LintIssue)]

### manimkit.lint.lint_scene(path)

Lint a scene file.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`LintIssue`](#manimkit.lint.LintIssue)]
