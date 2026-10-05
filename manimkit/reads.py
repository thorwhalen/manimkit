"""What a render read: the files and folders a scene opens, recorded as it runs.

A scene can read anything: ``ImageMobject(Path.home() / "logo.png")``, a CSV
named by an environment variable, a path built in a helper. No static reading
of the file finds those, so a caller that caches renders (``an``'s shot cache,
an#291) cannot tell when one changes. :class:`ReadRecorder` asks the interpreter
instead: a :func:`sys.addaudithook` hook sees every ``open`` the render makes
for reading, and every folder it lists (``os.listdir``, ``os.scandir``, so a
``glob`` over a folder is a read of that folder), whatever built the path.

What it reports is what the SCENE depends on, so the files of the Python
installation (the standard library, site-packages, the files of every installed
distribution, editable ones included) and device files are left out, and so is the listing of a folder on
``sys.path`` and the bytecode and path hooks an import touches (the import
system looking for a module); a caller
passes the folders it writes to (the render's output) as ``exclude``. A path
that does not exist is still a read — the scene looked for it — so a caller can
key its absence.

Not seen: reads made by C code without Python's ``open`` (fonts opened by Pango,
TeX's own inputs, ffmpeg), reads in a subprocess, and an existence test
(``Path.exists``) that opens nothing.

>>> rec = ReadRecorder()
>>> rec._hook("open", ("/data/x.csv", "r", 0))
>>> rec._hook("open", ("/data/out.txt", "w", 0o1))
>>> rec._hook("os.listdir", ("/data",))
>>> [(r["kind"], Path(r["path"]).name) for r in rec.reads(installation=False)]
[('dir', 'data'), ('file', 'x.csv')]
"""

from __future__ import annotations

import os
import site
import sys
import sysconfig
from collections.abc import Iterable
from pathlib import Path

#: Audit events that LIST a folder (the argument is the folder, or ``None``/fd).
LIST_EVENTS: frozenset[str] = frozenset({"os.listdir", "os.scandir"})

_O_ACCMODE: int = getattr(os, "O_ACCMODE", 3)  # absent on Windows; 3 is its value

#: Path prefixes that are devices or kernel views, never data a scene depends on.
DEVICE_PREFIXES: tuple[str, ...] = ("/dev/", "/proc/", "/sys/")


def _is_read(mode, flags) -> bool:
    """Whether an ``open`` audit event opens for reading (``r``, ``r+``, ``a+``…)."""
    if isinstance(flags, int) and flags:
        return (flags & _O_ACCMODE) != os.O_WRONLY
    if isinstance(mode, str):
        return "r" in mode or "+" in mode
    return True  # unknown: count it, a spurious read only costs a re-render


def installation_roots() -> list[str]:
    """The folders of this Python installation and of every installed distribution.

    Their files are code and data the caller keys by version, not inputs of a
    scene: the prefixes, the standard library, site-packages (system and user),
    and — for an editable install, whose files live elsewhere — the folder of
    each imported top-level package that belongs to a distribution.
    """
    roots = {
        sys.prefix,
        sys.base_prefix,
        sys.exec_prefix,
        sys.base_exec_prefix,
        *(p for p in sysconfig.get_paths().values() if p),
    }
    try:
        roots.update(site.getsitepackages())
    except AttributeError:  # pragma: no cover - a virtualenv without it
        pass
    user_site = site.getusersitepackages() if site.ENABLE_USER_SITE else None
    if user_site:
        roots.add(user_site)
    roots.update(_distribution_package_roots())
    return sorted({os.path.realpath(r) for r in roots if r})


def _distribution_package_roots() -> set[str]:
    from importlib.metadata import packages_distributions

    try:
        top_levels = set(packages_distributions())
    except Exception:  # noqa: BLE001 - broken metadata: keep what we have
        return set()
    out = set()
    for name, module in list(sys.modules.items()):
        if "." in name or name not in top_levels:
            continue
        file = getattr(module, "__file__", None)
        if not file:
            continue
        path = Path(file)
        out.add(str(path.parent if path.name == "__init__.py" else path))
    return out


def _is_import_artifact(path: str) -> bool:
    """Bytecode (derived from a source file that is read too) and an editable
    install's path-hook pseudo-file: what importing a module touches."""
    parts = Path(path).parts
    return "__pycache__" in parts or parts[-1].startswith("__editable__.")


def _under(path: str, roots: Iterable[str]) -> bool:
    return any(path == r or path.startswith(r.rstrip(os.sep) + os.sep) for r in roots)


class ReadRecorder:
    """Records the files a process opens for reading and the folders it lists.

    :meth:`install` adds the audit hook (for good: an audit hook cannot be
    removed, so install it in a process that exists to render, as the runner
    does). :meth:`reads` reports them, sorted, as ``{"path", "kind"}`` dicts.
    """

    def __init__(self) -> None:
        self.files: set[str] = set()
        self.dirs: set[str] = set()
        self._busy = False

    def install(self) -> "ReadRecorder":
        sys.addaudithook(self._hook)
        return self

    def _hook(self, event: str, args: tuple) -> None:
        if self._busy or (event != "open" and event not in LIST_EVENTS):
            return
        self._busy = True
        try:  # an exception in an audit hook would fail the scene's own open
            if event == "open":
                path, mode, flags = (tuple(args) + (None, None, None))[:3]
                if _is_read(mode, flags):
                    self._note(path, self.files)
            else:
                self._note(args[0] if args else None, self.dirs)
        except Exception:  # noqa: BLE001
            pass
        finally:
            self._busy = False

    @staticmethod
    def _note(path, into: set[str]) -> None:
        if path is None:
            path = "."
        if isinstance(path, int):  # a file descriptor: no name to key
            return
        into.add(os.path.abspath(os.fsdecode(path)))

    def reads(
        self, *, exclude: Iterable[str | Path] = (), installation: bool = True
    ) -> list[dict]:
        """What was read, minus the folders in ``exclude`` and (by default) the
        Python installation (:func:`installation_roots`) and device files."""
        self._busy = True  # stop recording: what this report reads is not the scene's
        roots = [os.path.realpath(str(p)) for p in exclude]
        if installation:
            roots += installation_roots()
        # The import system lists every folder on sys.path to find a module.
        import_dirs = {os.path.realpath(p or ".") for p in sys.path} if installation else set()
        out = []
        for kind, paths in (("file", self.files), ("dir", self.dirs)):
            for path in paths:
                real = os.path.realpath(path)
                if real.startswith(DEVICE_PREFIXES) or _under(real, roots):
                    continue
                if kind == "dir" and real in import_dirs:
                    continue
                if _is_import_artifact(path):
                    continue
                out.append({"path": path, "kind": kind})
        return sorted(out, key=lambda r: (r["path"], r["kind"]))
