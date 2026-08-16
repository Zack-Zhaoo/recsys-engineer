#!/usr/bin/env python3
"""Upgrade an installed recsys-engineer to this version, preserving workspace/.

Purpose:
    SKILL.md promises that a knowledge or skill update never resets
    `workspace/`. This script is that promise's implementation. Copying a new
    release over an existing install by hand would erase the ideas, positions,
    mastery evidence and journal a user has accumulated; this replaces only the
    content layers and migrates the mastery map onto the new module list.

    Run it from the NEW version (the one you just unpacked), pointing at the
    OLD install you want to upgrade.

Usage examples:
    python3 scripts/upgrade.py --target ~/.claude/skills/recsys-engineer
    python3 scripts/upgrade.py --target ~/.claude/skills/recsys-engineer --apply

Arguments:
    --target is the installed skill directory to upgrade. Without --apply the
    script only reports what it would do. --backup-dir overrides the default
    timestamped backup location.

Prerequisites and side effects:
    Python 3.9+. With --apply it copies workspace/ to a backup directory, then
    replaces every top-level entry of the target except workspace/, build
    output, and dot-entries such as .git. It never writes to the source, never
    deletes the backup, and never touches profile, positions, ideas, journal or
    history content.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


SOURCE = Path(__file__).resolve().parents[1]
PRESERVED_DIR = "workspace"
# Never touched in the target: the user's own data, build output, and VCS state.
# Dot-entries are skipped wholesale so a git-clone install keeps its .git intact.
SKIPPED_TOP_LEVEL = {PRESERVED_DIR, "dist", "__pycache__"}


def content_items(source: Path) -> list[str]:
    """Top-level entries to replace — derived, so a new file is never missed."""
    return sorted(
        entry.name
        for entry in source.iterdir()
        if entry.name not in SKIPPED_TOP_LEVEL and not entry.name.startswith(".")
    )


JOURNAL_ENTRY_PATTERN = re.compile(r"^## \d{4}-\d{2}-\d{2}T", re.MULTILINE)
SNAPSHOT_LINE_PATTERN = re.compile(r"^- 知识截止：(\S+)", re.MULTILINE)


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    """Write a file beside its destination, fsync it, then replace atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def snapshot_date(skill_root: Path) -> str:
    text_path = skill_root / "knowledge" / "snapshot.md"
    if not text_path.is_file():
        return "unknown"
    match = SNAPSHOT_LINE_PATTERN.search(text_path.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def workspace_summary(skill_root: Path) -> dict[str, Any]:
    workspace = skill_root / PRESERVED_DIR
    mastery = load_json(workspace / "mastery.json").get("modules", {})
    journal = workspace / "thinking" / "journal.md"
    events = workspace / "history" / "events.jsonl"
    profile = load_json(workspace / "profile.json")
    return {
        "ideas": len(load_json(workspace / "ideas" / "index.json").get("ideas", [])),
        "idea_cards": len(list((workspace / "ideas" / "cards").glob("*.md"))) if (workspace / "ideas" / "cards").is_dir() else 0,
        "positions": len(load_json(workspace / "thinking" / "positions.json").get("positions", [])),
        "assessed_modules": sum(1 for m in mastery.values() if m.get("level") != "unassessed"),
        "journal_entries": len(JOURNAL_ENTRY_PATTERN.findall(journal.read_text(encoding="utf-8"))) if journal.is_file() else 0,
        "history_events": sum(1 for line in events.read_text(encoding="utf-8").splitlines() if line.strip()) if events.is_file() else 0,
        "profile_filled": bool(profile.get("role") or profile.get("domains") or profile.get("goals")),
    }


def describe(summary: dict[str, Any]) -> str:
    return (
        f"灵感 {summary['ideas']} 条（卡片 {summary['idea_cards']} 份）、"
        f"稳定观点 {summary['positions']} 条、"
        f"已评估能力模块 {summary['assessed_modules']} 个、"
        f"思考日志 {summary['journal_entries']} 条、"
        f"变更事件 {summary['history_events']} 条、"
        f"画像{'已填写' if summary['profile_filled'] else '为空'}"
    )


def plan_mastery_migration(source: Path, target: Path) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    """Return the merged mastery map plus carried-over, added and retired module keys."""
    template = load_json(source / PRESERVED_DIR / "mastery.json")
    current = load_json(target / PRESERVED_DIR / "mastery.json")
    if not template or not current:
        return {}, [], [], []

    merged = json.loads(json.dumps(template))
    template_modules = merged.get("modules", {})
    current_modules = current.get("modules", {})

    carried, retired = [], []
    for key, module in current_modules.items():
        has_content = module.get("level") != "unassessed" or module.get("evidence")
        if key in template_modules:
            if has_content:
                template_modules[key] = module
                carried.append(key)
        else:
            # Never silently drop a user's assessment, even for a renamed module.
            template_modules[key] = module
            if has_content:
                retired.append(key)
    added = [key for key in template_modules if key not in current_modules]
    return merged, sorted(carried), sorted(added), sorted(retired)


def append_event(target: Path, summary: str) -> None:
    path = target / PRESERVED_DIR / "history" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"at": now_iso(), "type": "skill-upgraded", "target": "skill", "summary": summary}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def replace_content(source: Path, target: Path) -> None:
    for item in content_items(source):
        origin = source / item
        destination = target / item
        if not origin.exists():
            continue
        if origin.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(origin, destination)
        else:
            shutil.copy2(origin, destination)


def run_validation(target: Path) -> bool:
    validator = target / "scripts" / "validate_skill.py"
    result = subprocess.run(
        [sys.executable, str(validator), str(target), "--allow-personalized"],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode == 0


def upgrade(target: Path, apply: bool, backup_dir: Path | None) -> int:
    if not (target / "SKILL.md").is_file():
        print(f"目标不是一个 recsys-engineer 安装目录（缺少 SKILL.md）：{target}")
        return 1
    if target == SOURCE:
        print("目标与当前版本是同一个目录。请从新版本包内运行，指向已安装的旧版本。")
        return 1
    if not (target / PRESERVED_DIR).is_dir():
        print(f"目标缺少 workspace/ 目录，无法确认这是一个正常安装：{target}")
        return 1

    before = workspace_summary(target)
    _, carried, added, retired = plan_mastery_migration(SOURCE, target)

    print(f"升级来源：{SOURCE}（知识截止 {snapshot_date(SOURCE)}）")
    print(f"升级目标：{target}（知识截止 {snapshot_date(target)}）")
    print(f"将被替换：{', '.join(content_items(SOURCE))}")
    print(f"将被保留：{PRESERVED_DIR}/")
    print(f"当前 workspace：{describe(before)}")
    if carried:
        print(f"能力评估将迁移 {len(carried)} 个模块：{', '.join(carried)}")
    if added:
        print(f"新版本新增 {len(added)} 个能力模块，将以 unassessed 加入")
    if retired:
        print(f"新版本已移除但你有记录的模块 {len(retired)} 个，将原样保留：{', '.join(retired)}")

    if not apply:
        print("\n以上为预演，未做任何修改。确认无误后加 --apply 执行。")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir or target.parent / f"{target.name}-workspace-backup-{stamp}"
    if backup.exists():
        print(f"备份目录已存在，请换一个 --backup-dir：{backup}")
        return 1
    shutil.copytree(target / PRESERVED_DIR, backup)
    print(f"\nworkspace 已备份到：{backup}")

    merged, _, _, _ = plan_mastery_migration(SOURCE, target)
    replace_content(SOURCE, target)
    if merged:
        atomic_write_text(
            target / PRESERVED_DIR / "mastery.json",
            json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        )

    # Log the upgrade before summarising, so the reported counts match what a
    # later `manage_workspace.py status` will show.
    append_event(target, f"升级到知识截止 {snapshot_date(SOURCE)} 的版本，workspace 备份于 {backup}")
    after = workspace_summary(target)

    print(f"升级后 workspace：{describe(after)}")
    print()
    if not run_validation(target):
        print(f"\n升级后校验未通过。你的 workspace 备份仍在 {backup}，可据此回滚。")
        return 1

    lost = [key for key in ("ideas", "idea_cards", "positions", "journal_entries") if after[key] < before[key]]
    if lost:
        print(f"\n警告：以下计数在升级后减少，请用备份核对：{', '.join(lost)}")
        return 1

    print("\n升级完成，workspace 内容已保留。确认无误后可删除备份目录。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="已安装的 recsys-engineer 目录，例如 ~/.claude/skills/recsys-engineer",
    )
    parser.add_argument("--apply", action="store_true", help="真正执行升级；默认只预演")
    parser.add_argument("--backup-dir", type=Path, default=None, help="自定义 workspace 备份目录")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return upgrade(args.target.expanduser().resolve(), args.apply, args.backup_dir)


if __name__ == "__main__":
    sys.exit(main())
