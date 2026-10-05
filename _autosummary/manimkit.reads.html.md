# manimkit.reads

What a render read: the files and folders a scene opens, recorded as it runs.

A scene can read anything: `ImageMobject(Path.home() / "logo.png")`, a CSV
named by an environment variable, a path built in a helper. No static reading
of the file finds those, so a caller that caches renders (`an`’s shot cache,
an#291) cannot tell when one changes. [`ReadRecorder`](#manimkit.reads.ReadRecorder) asks the interpreter
instead: a [`sys.addaudithook()`](https://docs.python.org/3/library/sys.html#sys.addaudithook) hook sees every `open` the render makes
for reading, every SQLite database it connects to, and every folder it lists
(`os.listdir`, `os.scandir`, so a `glob` over a folder is a read of that
folder), whatever built the path.

What it reports is what the SCENE depends on. Left out: the files of the Python
installation (the standard library and site-packages, system and user — what a
caller keys by version), package metadata (`*.dist-info`, `*.egg-info`),
the path hooks an import touches, the listing of a folder on `sys.path` (the
import system looking for a module) and device files; a caller passes the
folders it writes to (the render’s output) as `exclude`. Code imported from
anywhere else — an editable install, a folder put on `sys.path` — is
recorded, as its SOURCE file even when Python loaded only its cached bytecode:
it can change without any version moving. A path that does not exist is still
a read (the scene looked for it), so a caller can key its absence.

Each read carries the `stat` its file or folder had when it was FIRST read
(`[mtime_ns, size]`, `None` when absent), so a caller that digests the files
after the render can tell one edited while the render ran.

Not seen: reads made by C code without Python’s `open` (fonts opened by Pango,
TeX’s own inputs such as an `\input` in a preamble, OpenCV, ffmpeg), reads in
a subprocess, and an existence test (`Path.exists`) that opens nothing.

```pycon
>>> rec = ReadRecorder()
>>> rec._hook("open", ("/data/x.csv", "r", 0))
>>> rec._hook("open", ("/data/out.txt", "w", 0o1))
>>> rec._hook("os.listdir", ("/data",))
>>> [(r["kind"], Path(r["path"]).name) for r in rec.reads(installation=False)]
[('dir', 'data'), ('file', 'x.csv')]
```

### Module Attributes

| [`LIST_EVENTS`](#manimkit.reads.LIST_EVENTS)             | Audit events that LIST a folder (the argument is the folder, or `None`/fd).                                                                                                                                                                                                               |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`C_READ_EVENTS`](#manimkit.reads.C_READ_EVENTS)           | Audit events that read a file named by their first argument, opened by C code.                                                                                                                                                                                                            |
| [`DEVICE_PREFIXES`](#manimkit.reads.DEVICE_PREFIXES)         | Path prefixes that are devices or kernel views, never data a scene depends on.                                                                                                                                                                                                            |
| [`METADATA_SUFFIXES`](#manimkit.reads.METADATA_SUFFIXES)       | Folder suffixes that hold an installed distribution's metadata.                                                                                                                                                                                                                           |
| [`INSTALLATION_PATH_NAMES`](#manimkit.reads.INSTALLATION_PATH_NAMES) | The [`sysconfig.get_paths()`](https://docs.python.org/3/library/sysconfig.html#sysconfig.get_paths) entries that hold the installation's code (not `data`/`scripts`, which are the bare prefix on a system Python, so excluding them would drop every read under `/usr` or `/usr/local`). |

### Functions

| [`installation_roots`](#manimkit.reads.installation_roots)()   | The folders of this Python installation's code: the standard library and site-packages (system and user).   |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|

### Classes

| [`ReadRecorder`](#manimkit.reads.ReadRecorder)()   | Records the files a process opens for reading and the folders it lists.   |
|-------------------------------------------------------------------|---------------------------------------------------------------------------|

### manimkit.reads.C_READ_EVENTS *: [frozenset](https://docs.python.org/3/builtins/stdtypes.html#frozenset)[[str](https://docs.python.org/3/builtins/stdtypes.html#str)]* *= frozenset({'sqlite3.connect'})*

Audit events that read a file named by their first argument, opened by C code.

### manimkit.reads.DEVICE_PREFIXES *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]* *= ('/dev/', '/proc/', '/sys/')*

Path prefixes that are devices or kernel views, never data a scene depends on.

### manimkit.reads.INSTALLATION_PATH_NAMES *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]* *= ('stdlib', 'platstdlib', 'purelib', 'platlib')*

The [`sysconfig.get_paths()`](https://docs.python.org/3/library/sysconfig.html#sysconfig.get_paths) entries that hold the installation’s code
(not `data`/`scripts`, which are the bare prefix on a system Python, so
excluding them would drop every read under `/usr` or `/usr/local`).

### manimkit.reads.LIST_EVENTS *: [frozenset](https://docs.python.org/3/builtins/stdtypes.html#frozenset)[[str](https://docs.python.org/3/builtins/stdtypes.html#str)]* *= frozenset({'os.listdir', 'os.scandir'})*

Audit events that LIST a folder (the argument is the folder, or `None`/fd).

### manimkit.reads.METADATA_SUFFIXES *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]* *= ('.dist-info', '.egg-info')*

Folder suffixes that hold an installed distribution’s metadata.

### *class* manimkit.reads.ReadRecorder

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Records the files a process opens for reading and the folders it lists.

`install()` adds the audit hook (for good: an audit hook cannot be
removed, so install it in a process that exists to render, as the runner
does). [`reads()`](#manimkit.reads.ReadRecorder.reads) reports them, sorted, as `{"path", "kind", "stat"}`
dicts.

#### reads(, exclude=(), installation=True)

What was read, minus the folders in `exclude` and (by default) the
Python installation ([`installation_roots()`](#manimkit.reads.installation_roots)), import artefacts and
device files. Stops recording: what the report itself reads is not the
scene’s.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]

### manimkit.reads.installation_roots()

The folders of this Python installation’s code: the standard library and
site-packages (system and user). What a caller keys by version. An editable
install’s folder is NOT one of them: its files can change without any
version moving, so reads of them are reported.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
