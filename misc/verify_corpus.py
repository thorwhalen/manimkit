"""Render every shipped example and report which fail or raise layout warnings.

Usage: python misc/verify_corpus.py OUT_DIR [--origin curated|gallery|all] [--jobs N]

Run it before committing a new or edited example. Output (videos, frames, a
summary JSON) goes to OUT_DIR, which must be outside the repo.
"""

import argparse
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from manimkit import curated_examples, render_check


def verify(ex, out_dir: Path):
    work = out_dir / ex.id.replace("/", "__")
    work.mkdir(parents=True, exist_ok=True)
    f = work / f"{Path(ex.id).name}.py"
    f.write_text(ex.runnable_code, encoding="utf-8")
    r = render_check(f, ex.scene, out_dir=work / "render", n_frames=4)
    return {
        "id": ex.id,
        "ok": r.ok,
        "duration": r.duration,
        "error": r.error,
        "warnings": [w["message"] for w in r.layout_warnings],
        "lint": r.lint,
        "sheet": r.contact_sheet,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("out_dir")
    p.add_argument("--origin", default="all")
    p.add_argument("--jobs", type=int, default=4)
    a = p.parse_args(argv)
    out = Path(a.out_dir)
    exs = [e for e in curated_examples() if a.origin == "all" or e.origin == a.origin]
    with ThreadPoolExecutor(a.jobs) as pool:
        results = list(pool.map(lambda e: verify(e, out), exs))
    (out / "summary.json").write_text(json.dumps(results, indent=2))
    bad = 0
    for r in results:
        flag = (
            "ok  " if r["ok"] and not r["warnings"] else ("WARN" if r["ok"] else "FAIL")
        )
        bad += flag != "ok  "
        print(f"{flag} {r['id']:45s} {r['duration'] or 0:6.2f}s  {r['error'] or ''}")
        for w in r["warnings"] + r["lint"]:
            print(f"       - {w}")
    print(f"{len(results) - bad}/{len(results)} clean")
    return 1 if any(not r["ok"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
