# PYTHON_ARGCOMPLETE_OK
"""``manimkit`` command line: search, show, lint, render, check."""

import functools

import cw

from manimkit.tools import _dispatch_funcs


def main():
    """Dispatch the tools to a CLI."""
    commands = {f.__name__.replace("list_examples", "list"): f for f in _dispatch_funcs}
    dispatch = functools.partial(cw.dispatch, convention=cw.MODERN)
    raise SystemExit(dispatch(commands, prog="manimkit"))


if __name__ == "__main__":
    main()
