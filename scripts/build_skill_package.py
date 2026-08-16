#!/usr/bin/env python3
"""Build the distributable recsys-engineer.skill archive.

Purpose:
    Package this repository into a single archive that unpacks to a
    `recsys-engineer/` directory, ready to drop into ~/.claude/skills/.

    The build refuses to run unless validate_skill.py passes, so an archive
    with broken links, unfilled {{placeholders}}, a missing license or a dirty
    public workspace can never be shipped by accident.

Usage examples:
    python3 scripts/build_skill_package.py
    python3 scripts/build_skill_package.py --output /tmp/recsys-engineer.skill

Prerequisites and side effects:
    Python 3.9+. Writes only the output archive (dist/ by default, which is
    git-ignored); never modifies skill content. Exits non-zero if validation
    fails.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import zipfile


SKILL_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_PREFIX = "recsys-engineer"
DEFAULT_OUTPUT = SKILL_ROOT / "dist" / "recsys-engineer.skill"
EXCLUDED_DIRS = {"__pycache__", "dist"}
EXCLUDED_SUFFIXES = {".pyc"}


def collect_entries(root: Path) -> list[tuple[Path, str]]:
    """Return (source path, archive name) pairs in a stable, reproducible order.

    Archive names are rooted at ARCHIVE_PREFIX rather than the local directory
    name, so a clone into any folder still produces the same archive layout.
    """
    entries: list[tuple[Path, str]] = []
    for directory, subdirs, filenames in os.walk(root):
        subdirs[:] = sorted(d for d in subdirs if not d.startswith(".") and d not in EXCLUDED_DIRS)
        current = Path(directory)
        relative = current.relative_to(root)
        prefix = Path(ARCHIVE_PREFIX) / relative
        entries.append((current, f"{prefix.as_posix()}/"))
        for filename in sorted(filenames):
            if filename.startswith(".") or Path(filename).suffix in EXCLUDED_SUFFIXES:
                continue
            entries.append((current / filename, (prefix / filename).as_posix()))
    return entries


def run_validation() -> bool:
    result = subprocess.run(
        [sys.executable, str(SKILL_ROOT / "scripts" / "validate_skill.py"), str(SKILL_ROOT)],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode == 0


def build(output: Path) -> int:
    print("Validating skill before packaging...")
    if not run_validation():
        print("\nBuild aborted: the skill did not pass validation.")
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    entries = collect_entries(SKILL_ROOT)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        for source, archive_name in entries:
            archive.write(source, archive_name)

    size_kb = output.stat().st_size / 1024
    print(f"\nBuilt {output} ({len(entries)} entries, {size_kb:.0f} KB)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path of the archive to write (default: dist/recsys-engineer.skill)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return build(args.output.resolve())


if __name__ == "__main__":
    sys.exit(main())
