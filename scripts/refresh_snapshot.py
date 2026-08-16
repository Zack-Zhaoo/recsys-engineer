#!/usr/bin/env python3
"""Move the knowledge snapshot to a new cut-off date, then audit what that claims.

Purpose:
    The snapshot date is asserted in ~20 places across SKILL.md, LICENSE.md,
    the READMEs, the two source catalogs, validate_skill.py and several
    knowledge files. Editing them by hand means either a failed validation or,
    worse, a shipped product whose stated cut-off contradicts itself.

    Bumping the date is a claim that the knowledge is current to that date, so
    this tool does two things: it rewrites the mechanical parts, and it then
    audits whether the content actually backs the new claim — newest catalog
    entry, and which files carry snapshot-dated prose a human must re-read.

Usage examples:
    python3 scripts/refresh_snapshot.py --date 2027-02-01
    python3 scripts/refresh_snapshot.py --date 2027-02-01 --build-date 2027-02-06 --apply

Arguments:
    --date is the new knowledge cut-off. --build-date defaults to today.
    Without --apply the script only reports; nothing is written.

Prerequisites and side effects:
    Python 3.9+. With --apply it rewrites date strings across the skill, then
    runs validate_skill.py. It never edits workspace/ and never adds or removes
    knowledge content.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re
import subprocess
import sys


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR
SCANNED_SUFFIXES = {".md", ".yaml", ".py"}
EXCLUDED_DIRS = {"workspace", "__pycache__", "dist"}
BUILD_LINE_PATTERN = re.compile(r"^(- 构建日期：)(\S+)$", re.MULTILINE)
SNAPSHOT_HEADING_PATTERN = re.compile(r"^(#{2,3} )(\d{4}-\d{2})( 快照)$", re.MULTILINE)
FRESHNESS_GAP_DAYS = 60


def iso_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a date in YYYY-MM-DD format") from exc
    return value


def current_snapshot_date() -> str:
    text = (SKILL_DIR / "scripts" / "validate_skill.py").read_text(encoding="utf-8")
    match = re.search(r'^SNAPSHOT_DATE = "(\d{4}-\d{2}-\d{2})"', text, re.MULTILINE)
    if not match:
        raise SystemExit("Could not read SNAPSHOT_DATE from validate_skill.py")
    return match.group(1)


def scanned_files() -> list[Path]:
    files = []
    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if any(part in EXCLUDED_DIRS or part.startswith(".") for part in path.relative_to(SKILL_DIR).parts):
            continue
        files.append(path)
    return files


def newest_catalog_entries() -> list[tuple[str, str]]:
    """Return (catalog label, newest publication date or year) for both catalogs."""
    results = []
    papers = json.loads((SKILL_DIR / "knowledge" / "sources" / "catalog.yaml").read_text(encoding="utf-8"))
    years = [entry.get("year") for entry in papers.get("entries", []) if isinstance(entry.get("year"), int)]
    results.append(("论文目录", str(max(years)) if years else "无条目"))

    industry = json.loads(
        (SKILL_DIR / "knowledge" / "industry" / "articles" / "catalog.yaml").read_text(encoding="utf-8")
    )
    published = [entry.get("published") for entry in industry.get("entries", []) if isinstance(entry.get("published"), str)]
    results.append(("工业文章目录", max(published) if published else "无条目"))
    return results


def audit_freshness(new_date: str) -> list[str]:
    warnings = []
    for label, newest in newest_catalog_entries():
        if len(newest) == 4:  # year-only, papers
            if int(newest) < int(new_date[:4]):
                warnings.append(f"{label} 最新条目为 {newest} 年，但截止日已推到 {new_date}")
            continue
        if newest == "无条目":
            continue
        gap = (date.fromisoformat(new_date) - date.fromisoformat(newest)).days
        if gap > FRESHNESS_GAP_DAYS:
            warnings.append(f"{label} 最新条目 {newest}，距新截止日 {new_date} 有 {gap} 天没有新增材料")
    return warnings


def review_checklist(old_date: str) -> list[Path]:
    """Files whose prose asserts something about the snapshot and must be re-read."""
    flagged = []
    for path in scanned_files():
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if old_date in text or SNAPSHOT_HEADING_PATTERN.search(text):
            flagged.append(path)
    return flagged


def rewrite(old_date: str, new_date: str, build_date: str, apply: bool) -> int:
    old_month, new_month = old_date[:7], new_date[:7]
    touched: list[tuple[Path, int]] = []

    for path in scanned_files():
        text = path.read_text(encoding="utf-8")
        updated = text.replace(old_date, new_date)
        updated = SNAPSHOT_HEADING_PATTERN.sub(
            lambda m: f"{m.group(1)}{new_month}{m.group(3)}" if m.group(2) == old_month else m.group(0),
            updated,
        )
        if path.name == "snapshot.md":
            updated = BUILD_LINE_PATTERN.sub(lambda m: f"{m.group(1)}{build_date}", updated)
        if updated != text:
            changes = sum(1 for a, b in zip(text.splitlines(), updated.splitlines()) if a != b)
            touched.append((path, changes or 1))
            if apply:
                path.write_text(updated, encoding="utf-8")

    if not touched:
        print(f"没有找到需要修改的位置（当前截止日已是 {new_date}？）")
        return 1

    verb = "已更新" if apply else "将更新"
    print(f"{verb} {len(touched)} 个文件：{old_date} → {new_date}\n")
    for path, changes in touched:
        print(f"  {path.relative_to(REPO_ROOT)}  ({changes} 行)")
    return 0


def run_validation() -> bool:
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "validate_skill.py"), str(SKILL_DIR)],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode == 0


def refresh(new_date: str, build_date: str, apply: bool) -> int:
    old_date = current_snapshot_date()
    if new_date <= old_date:
        print(f"新截止日 {new_date} 不晚于当前截止日 {old_date}，拒绝执行。")
        return 1
    if build_date < new_date:
        print(f"构建日期 {build_date} 早于知识截止日 {new_date}，请检查。")
        return 1

    flagged = review_checklist(old_date)
    if rewrite(old_date, new_date, build_date, apply) != 0:
        return 1

    if apply:
        print()
        if not run_validation():
            print("\n校验未通过，请修复后再打包。")
            return 1

    print("\n内容新鲜度审计：")
    warnings = audit_freshness(new_date)
    if warnings:
        for warning in warnings:
            print(f"  ! {warning}")
        print("  改日期不会让知识变新。上述缺口需要补录材料，否则新截止日是一个无法兑现的声明。")
    else:
        print("  两个来源目录的最新条目与新截止日之间没有明显缺口。")

    print(f"\n需人工复核的文件（{len(flagged)} 个，正文含快照声明）：")
    for path in flagged:
        print(f"  {path.relative_to(REPO_ROOT)}")

    if not apply:
        print("\n以上为预演，未做任何修改。确认无误后加 --apply 执行。")
    else:
        print("\n复核完成后运行：python3 scripts/build_skill_package.py")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=iso_date, required=True, help="新的知识截止日，格式 YYYY-MM-DD")
    parser.add_argument("--build-date", type=iso_date, default=None, help="新的构建日期，默认今天")
    parser.add_argument("--apply", action="store_true", help="真正写入；默认只预演")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_date = args.build_date or datetime.now().strftime("%Y-%m-%d")
    return refresh(args.date, build_date, args.apply)


if __name__ == "__main__":
    sys.exit(main())
