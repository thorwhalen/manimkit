"""What a render read: the files and folders a scene opens, recorded as it runs.

A scene can read anything: ``ImageMobject(Path.home() / "logo.png")``, a CSV
named by an environment variable, a path built in a helper. No static reading
of the file finds those, so a caller that caches renders (``an``'s shot cache,
an#291) cannot tell when one changes. :class:`ReadRecorder` asks the interpreter
instead: a :func:`sys.addaudithook` hook sees every ``open`` the render makes
for reading, every SQLite database it connects to, and every folder it lists
(``os.listdir``, ``os.scandir``, so a ``glob`` over a folder is a read of that
folder), whatever built the path.

What it reports is what the SCENE depends on. Left out: the files of the Python
installation (the standard library and site-packages, system and user — what a
caller keys by version), package metadata (``*.dist-info``, ``*.egg-info``),
the path hooks an import touches, the listing of a folder on ``sys.path`` (the
import system looking for a module) and device files; a caller passes the
folders it writes to (the render's output) as ``exclude``. Code imported from
anywhere else — an editable install, a folder put on ``sys.path`` — is
recorded, as its SOURCE file even when Python loaded only its cached bytecode:
it can change without any version moving. A path that does not exist is still
a read (the scene looked for it), so a caller can key its absence.

Each read carries the ``stat`` its file or folder had when it was FIRST read
(``[mtime_ns, size]``, ``None`` when absent), so a caller that digests the files
after the render can tell one edited while the render ran.

Not seen: reads made by C code without Python's ``open`` (fonts opened by Pango,
TeX's own inputs such as an ``\\input`` in a preamble, OpenCV, ffmpeg), reads in
a subprocess, and an existence test (``Path.exists``) that opens nothing.

>>> rec = ReadRecorder()
>>> rec._hook("open", ("/data/x.csv", "r", 0))
>>> rec._hook("open", ("/data/out.txt", "w", 0o1))
>>> rec._hook("os.listdir", ("/data",))
>>> [(r["kind"], Path(r["path"]).name) for r in rec.reads(installation=False)]
[('dir', 'data'), ('file', 'x.csv')]
"""

from __future__ import annotations

import importlib.util
import os
import site
import sys
import sysconfig
import threading
from collections.abc import Iterable
from pathlib import Path

#: Audit events that LIST a folder (the argument is the folder, or ``None``/fd).
LIST_EVENTS: frozenset[str] = frozenset({"os.listdir", "os.scandir"})
#: Audit events that read a file named by their first argument, opened by C code.
C_READ_EVENTS: frozenset[str] = frozenset({"sqlite3.connect"})

_O_ACCMODE: int = getattr(os, "O_ACCMODE", 3)  # absent on Windows; 3 is its value

#: Path prefixes that are devices or kernel views, never data a scene depends on.
DEVICE_PREFIXES: tuple[str, ...] = ("/dev/", "/proc/", "/sys/")

#: Folder suffixes that hold an installed distribution's metadata.
METADATA_SUFFIXES: tuple[str, ...] = (".dist-info", ".egg-info")

#: The :func:`sysconfig.get_paths` entries that hold the installation's code
#: (not ``data``/``scripts``, which are the bare prefix on a system Python, so
#: excluding them would drop every read under ``/usr`` or ``/usr/local``).
INSTALLATION_PATH_NAMES: tuple[str, ...] = ("stdlib", "platstdlib", "purelib", "platlib")


def _is_read(mode, flags) -> bool:
    """Whether an ``open`` audit event opens for reading (``r``, ``r+``, ``a+``…)."""
    if isinstance(flags, int) and flags:
        return (flags & _O_ACCMODE) != os.O_WRONLY
    if isinstance(mode, str):
        return "r" in mode or "+" in mode
    return True  # unknown: count it, a spurious read only costs a re-render


def _norm(path: str) -> str:
    """The form two paths are compared in: real, and case-folded where the OS is."""
    return os.path.normcase(os.path.realpath(path))


def installation_roots() -> list[str]:
    """The folders of this Python installation's code: the standard library and
    site-packages (system and user). What a caller keys by version. An editable
    install's folder is NOT one of them: its files can change without any
    version moving, so reads of them are reported."""
    paths = sysconfig.get_paths()
    roots = {paths.get(name) for name in INSTALLATION_PATH_NAMES}
    try:
        roots.update(site.getsitepackages())
    except AttributeError:  # pragma: no cover - a virtualenv without it
        pass
    user_site = site.getusersitepackages() if site.ENABLE_USER_SITE else None
    if user_site:
        roots.add(user_site)
    return sorted({_norm(r) for r in roots if r})


def _source_of(path: str) -> str:
    """The source file a cached bytecode file was compiled from (Python reads
    only the ``.pyc`` while it is current, so the ``.py`` is never opened);
    any other path unchanged."""
    if "__pycache__" in Path(path).parts and path.endswith(".pyc"):
        try:
            return importlib.util.source_from_cache(path)
        except ValueError:
            return path
    return path


def _is_import_artifact(path: str) -> bool:
    """An editable install's path-hook pseudo-file and distribution metadata:
    what importing a module or looking up an entry point touches."""
    parts = Path(path).parts
    if not parts:
        return False
    return parts[-1].startswith("__editable__.") or any(
        p.endswith(METADATA_SUFFIXES) for p in parts
    )


def _under(path: str, roots: Iterable[str]) -> bool:
    return any(path == r or path.startswith(r.rstrip(os.sep) + os.sep) for r in roots)


def _stat(path: str) -> list[int] | None:
    try:
        st = os.stat(path)
    except (OSError, ValueError):
        return None
    return [st.st_mtime_ns, st.st_size]


class ReadRecorder:
    """Records the files a process opens for reading and the folders it lists.

    :meth:`install` adds the audit hook (for good: an audit hook cannot be
    removed, so install it in a process that exists to render, as the runner
    does). :meth:`reads` reports them, sorted, as ``{"path", "kind", "stat"}``
    dicts.
    """

    def __init__(self) -> None:
        self.files: dict[str, list[int] | None] = {}
        self.dirs: dict[str, list[int] | None] = {}
        self._local = threading.local()  # per thread: a read on another is never lost
        self._stopped = False

    def install(self) -> "ReadRecorder":
        sys.addaudithook(self._hook)
        return self

    def _hook(self, event: str, args: tuple) -> None:
        if self._stopped:
            return
        if event != "open" and event not in LIST_EVENTS and event not in C_READ_EVENTS:
            return
        if getattr(self._local, "busy", False):  # the hook's own work, re-entering
            return
        self._local.busy = True
        try:  # an exception in an audit hook would fail the scene's own open
            if event == "open":
                path, mode, flags = (tuple(args) + (None, None, None))[:3]
                if _is_read(mode, flags):
                    self._note(path, self.files)
            elif event in C_READ_EVENTS:
                self._note(args[0] if args else None, self.files)
            else:
                self._note(args[0] if args else None, self.dirs)
        except Exception:  # noqa: BLE001
            pass
        finally:
            self._local.busy = False

    @staticmethod
    def _note(path, into: dict) -> None:
        if path is None:
            path = "."
        if isinstance(path, int):  # a file descriptor: no name to key
            return
        path = os.fsdecode(path)
        if path == ":memory:":  # sqlite's in-memory database
            return
        path = _source_of(os.path.abspath(path))
        if path not in into:  # the state at the FIRST read is what was read
            into[path] = _stat(path)

    def reads(
        self, *, exclude: Iterable[str | Path] = (), installation: bool = True
    ) -> list[dict]:
        """What was read, minus the folders in ``exclude`` and (by default) the
        Python installation (:func:`installation_roots`), import artefacts and
        device files. Stops recording: what the report itself reads is not the
        scene's."""
        self._stopped = True
        roots = [_norm(str(p)) for p in exclude]
        if installation:
            roots += installation_roots()
        # The import system lists every folder on sys.path to find a module.
        import_dirs = {_norm(p or ".") for p in sys.path} if installation else set()
        out = []
        for kind, paths in (("file", self.files), ("dir", self.dirs)):
            for path, stat in paths.items():
                real = _norm(path)
                if real.startswith(DEVICE_PREFIXES) or _under(real, roots):
                    continue
                if kind == "dir" and real in import_dirs:
                    continue
                if _is_import_artifact(path):
                    continue
                out.append({"path": path, "kind": kind, "stat": stat})
        return sorted(out, key=lambda r: (r["path"], r["kind"]))
