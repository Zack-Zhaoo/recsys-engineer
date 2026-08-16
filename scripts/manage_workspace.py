#!/usr/bin/env python3
"""Manage the personal workspace embedded in the recsys-engineer skill.

Purpose:
    Record profile facts, mastery evidence, thoughts, stable positions, and
    recommendation ideas without hand-editing linked JSON indexes.

Usage examples:
    python3 scripts/manage_workspace.py status
    python3 scripts/manage_workspace.py record-idea --title "A new reranker" \
        --note "Use uncertainty to allocate diversity." --funnel reranking \
        --scenario-fit high --implementation-cost low
    python3 scripts/manage_workspace.py set-mastery --path funnel.retrieval \
        --level apply --evidence "Implemented and diagnosed a two-tower model"

Arguments:
    Run with --help or `<command> --help` for all command-specific arguments.

Prerequisites and side effects:
    Python 3.9+ and a complete skill directory are required. Mutating commands
    atomically update files under workspace/ and append an audit event to
    workspace/history/events.jsonl. They do not modify knowledge/.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
from datetime import date, datetime, timedelta
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = SKILL_ROOT / "workspace"
LEVELS = ["unassessed", "aware", "explain", "apply", "design", "research"]
EVIDENCE_SOURCES = [
    "self-reported",
    "observed",
    "user-confirmed",
    "assistant",
    "co-developed",
    "external",
]
ORIGINS = ["user", "assistant", "co-developed", "external"]
IDEA_STATUSES = [
    "captured",
    "incubating",
    "clustered",
    "developing",
    "experiment-ready",
    "experimenting",
    "validated",
    "adopted",
    "rejected",
    "archived",
]
NOVELTY_STATUSES = [
    "unverified",
    "partially-searched",
    "supported",
    "overlapping",
    "not-novel",
]
TRIAGE_LEVELS = ["unknown", "low", "medium", "high"]
ACTION_TRACKS = ["undecided", "incubation-todo", "long-term-idea"]


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def iso_date(value: str) -> str:
    """Return an ISO date string or raise an argparse-friendly error."""
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a date in YYYY-MM-DD format") from exc
    return value


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"Required workspace file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


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


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def append_event(event_type: str, target: str, summary: str) -> None:
    path = WORKSPACE / "history" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"at": now_iso(), "type": event_type, "target": target, "summary": summary}
    # A single compact line keeps the audit trail append-only and easy to stream.
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def unique_extend(existing: list[str], additions: list[str] | None) -> list[str]:
    result = list(existing)
    for value in additions or []:
        cleaned = value.strip()
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result


def cmd_status(_: argparse.Namespace) -> None:
    profile = read_json(WORKSPACE / "profile.json")
    mastery = read_json(WORKSPACE / "mastery.json")
    positions = read_json(WORKSPACE / "thinking" / "positions.json")
    ideas = read_json(WORKSPACE / "ideas" / "index.json")
    level_counts = {level: 0 for level in LEVELS}
    for module in mastery.get("modules", {}).values():
        level = module.get("level", "unassessed")
        level_counts[level] = level_counts.get(level, 0) + 1
    idea_items = ideas.get("ideas", [])
    idea_statuses = {status: 0 for status in IDEA_STATUSES}
    due_for_review: list[str] = []
    today = date.today().isoformat()
    for item in idea_items:
        status = item.get("status", "captured")
        idea_statuses[status] = idea_statuses.get(status, 0) + 1
        review_after = item.get("review_after")
        if isinstance(review_after, str) and review_after <= today:
            due_for_review.append(item.get("id", "unknown"))
    print_json(
        {
            "profile_initialized": any(
                [
                    profile.get("role"),
                    profile.get("experience_years") is not None,
                    profile.get("domains"),
                    profile.get("goals"),
                    profile.get("notes"),
                ]
            ),
            "mastery": level_counts,
            "positions": len(positions.get("positions", [])),
            "ideas": len(idea_items),
            "idea_statuses": idea_statuses,
            "ideas_due_for_review": due_for_review,
            "events_file": (WORKSPACE / "history" / "events.jsonl").exists(),
        }
    )


def cmd_update_profile(args: argparse.Namespace) -> None:
    path = WORKSPACE / "profile.json"
    profile = read_json(path)
    changed = False
    if args.role is not None:
        profile["role"] = args.role.strip() or None
        changed = True
    if args.experience_years is not None:
        profile["experience_years"] = args.experience_years
        changed = True
    list_fields = {
        "domains": args.domain,
        "goals": args.goal,
        "notes": args.note,
    }
    for field, values in list_fields.items():
        if values:
            profile[field] = unique_extend(profile.get(field, []), values)
            changed = True
    interests = profile.setdefault("interests", {"funnel": [], "paradigms": [], "topics": []})
    for field, values in {
        "funnel": args.funnel,
        "paradigms": args.paradigm,
        "topics": args.topic,
    }.items():
        if values:
            interests[field] = unique_extend(interests.get(field, []), values)
            changed = True
    if not changed:
        raise ValueError("No profile field was supplied")
    profile["updated_at"] = now_iso()
    atomic_write_json(path, profile)
    append_event("profile.updated", "profile", "Updated recommendation profile")
    print_json(profile)


def cmd_set_mastery(args: argparse.Namespace) -> None:
    path = WORKSPACE / "mastery.json"
    mastery = read_json(path)
    modules = mastery.get("modules", {})
    if args.path not in modules:
        available = ", ".join(sorted(modules))
        raise ValueError(f"Unknown mastery path '{args.path}'. Available: {available}")
    timestamp = now_iso()
    previous = modules[args.path].get("level", "unassessed")
    modules[args.path]["level"] = args.level
    modules[args.path].setdefault("evidence", []).append(
        {"at": timestamp, "source": args.source, "detail": args.evidence.strip()}
    )
    modules[args.path]["updated_at"] = timestamp
    atomic_write_json(path, mastery)
    append_event(
        "mastery.updated",
        args.path,
        f"Changed mastery from {previous} to {args.level}: {args.evidence.strip()}",
    )
    print_json({"path": args.path, **modules[args.path]})


def cmd_append_thought(args: argparse.Namespace) -> None:
    path = WORKSPACE / "thinking" / "journal.md"
    if not path.exists():
        raise ValueError(f"Required workspace file is missing: {path}")
    timestamp = now_iso()
    topics = ", ".join(args.topic or []) or "general"
    entry = (
        f"\n\n## {timestamp} · {topics}\n\n"
        f"- 来源：{args.origin}\n"
        f"- 思考：{args.text.strip()}\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
        handle.flush()
        os.fsync(handle.fileno())
    append_event("thought.appended", "thinking/journal", args.text.strip()[:160])
    print_json({"at": timestamp, "topics": args.topic or [], "origin": args.origin})


def cmd_record_position(args: argparse.Namespace) -> None:
    path = WORKSPACE / "thinking" / "positions.json"
    document = read_json(path)
    positions = document.setdefault("positions", [])
    timestamp = now_iso()
    position_id = f"POS-{datetime.now().astimezone():%Y%m%d}-{secrets.token_hex(3)}"
    if args.supersedes:
        old = next((item for item in positions if item.get("id") == args.supersedes), None)
        if old is None:
            raise ValueError(f"Position to supersede was not found: {args.supersedes}")
        old["status"] = "superseded"
        old["superseded_by"] = position_id
        old["updated_at"] = timestamp
    position = {
        "id": position_id,
        "statement": args.statement.strip(),
        "rationale": args.rationale.strip(),
        "status": "active",
        "origin": args.origin,
        "topics": args.topic or [],
        "supersedes": args.supersedes,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    positions.append(position)
    atomic_write_json(path, document)
    append_event("position.recorded", position_id, args.statement.strip()[:160])
    print_json(position)


def idea_card(metadata: dict[str, Any], note: str, source_note: str | None) -> str:
    source_section = f"\n\n## 触发背景\n\n{source_note.strip()}" if source_note else ""
    return (
        "---\n"
        f"id: {json.dumps(metadata['id'], ensure_ascii=False)}\n"
        f"status: {json.dumps(metadata['status'], ensure_ascii=False)}\n"
        f"novelty: {json.dumps(metadata['novelty'], ensure_ascii=False)}\n"
        f"origin: {json.dumps(metadata['origin'], ensure_ascii=False)}\n"
        f"created_at: {json.dumps(metadata['created_at'], ensure_ascii=False)}\n"
        f"funnel: {json.dumps(metadata['funnel'], ensure_ascii=False)}\n"
        f"paradigms: {json.dumps(metadata['paradigms'], ensure_ascii=False)}\n"
        f"topics: {json.dumps(metadata['topics'], ensure_ascii=False)}\n"
        f"scenario_fit: {json.dumps(metadata['scenario_fit'], ensure_ascii=False)}\n"
        f"implementation_cost: {json.dumps(metadata['implementation_cost'], ensure_ascii=False)}\n"
        f"action_track: {json.dumps(metadata['action_track'], ensure_ascii=False)}\n"
        f"review_after: {json.dumps(metadata['review_after'], ensure_ascii=False)}\n"
        f"related_ideas: {json.dumps(metadata['related_ideas'], ensure_ascii=False)}\n"
        "---\n\n"
        f"# {metadata['title']}\n\n"
        f"## 核心表达\n\n{note.strip()}"
        f"{source_section}\n\n"
        "## 初始分流\n\n"
        f"- 场景适配度：`{metadata['scenario_fit']}`\n"
        f"- 实现成本：`{metadata['implementation_cost']}`\n"
        f"- 行动轨道：`{metadata['action_track']}`\n"
        f"- 复看日期：`{metadata['review_after'] or '未设置'}`\n\n"
        "## 待验证\n\n"
        "- 新颖性：未检索，保持 `unverified`。\n"
        "- 需要明确最强 Baseline、反例和可证伪实验。\n"
    )


def cmd_record_idea(args: argparse.Namespace) -> None:
    index_path = WORKSPACE / "ideas" / "index.json"
    index = read_json(index_path)
    timestamp = now_iso()
    idea_id = f"IDEA-{datetime.now().astimezone():%Y%m%d}-{secrets.token_hex(3)}"
    card_rel = f"workspace/ideas/cards/{idea_id}.md"
    action_track = args.action_track
    if action_track is None:
        if args.scenario_fit == "high" and args.implementation_cost == "low":
            action_track = "incubation-todo"
        elif args.scenario_fit == "low" or args.implementation_cost == "high":
            action_track = "long-term-idea"
        else:
            action_track = "undecided"
    if args.review_after is not None and action_track == "undecided":
        action_track = "incubation-todo"
    review_after = args.review_after
    if action_track == "incubation-todo" and review_after is None:
        review_after = (date.today() + timedelta(days=7)).isoformat()
    initial_status = "incubating" if action_track == "incubation-todo" else "captured"
    metadata = {
        "id": idea_id,
        "title": args.title.strip(),
        "status": initial_status,
        "novelty": "unverified",
        "origin": args.origin,
        "funnel": args.funnel or [],
        "paradigms": args.paradigm or [],
        "topics": args.topic or [],
        "scenario_fit": args.scenario_fit,
        "implementation_cost": args.implementation_cost,
        "action_track": action_track,
        "review_after": review_after,
        "related_ideas": [],
        "card": card_rel,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    card_path = SKILL_ROOT / card_rel
    atomic_write_text(card_path, idea_card(metadata, args.note, args.source_note))
    index.setdefault("ideas", []).append(metadata)
    atomic_write_json(index_path, index)
    append_event("idea.recorded", idea_id, args.title.strip())
    print_json(metadata)


def replace_frontmatter_field(text: str, field: str, value: Any) -> str:
    prefix = f"{field}: "
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = prefix + json.dumps(value, ensure_ascii=False)
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    raise ValueError(f"Idea card is missing frontmatter field: {field}")


def cmd_update_idea(args: argparse.Namespace) -> None:
    supplied = [
        args.status,
        args.novelty,
        args.note,
        args.scenario_fit,
        args.implementation_cost,
        args.action_track,
        args.review_after,
        args.related_idea,
    ]
    if all(value is None for value in supplied):
        raise ValueError("Supply a status, novelty, triage field, related idea, review date, or note")
    index_path = WORKSPACE / "ideas" / "index.json"
    index = read_json(index_path)
    metadata = next((item for item in index.get("ideas", []) if item.get("id") == args.id), None)
    if metadata is None:
        raise ValueError(f"Idea was not found: {args.id}")
    card_path = SKILL_ROOT / metadata["card"]
    if not card_path.exists():
        raise ValueError(f"Idea card is missing: {card_path}")
    card = card_path.read_text(encoding="utf-8")
    if args.status is not None:
        metadata["status"] = args.status
        card = replace_frontmatter_field(card, "status", args.status)
    if args.novelty is not None:
        metadata["novelty"] = args.novelty
        card = replace_frontmatter_field(card, "novelty", args.novelty)
    for field in ("scenario_fit", "implementation_cost", "action_track", "review_after"):
        value = getattr(args, field)
        if value is not None:
            metadata[field] = value
            card = replace_frontmatter_field(card, field, value)
    if args.related_idea:
        if args.id in args.related_idea:
            raise ValueError("An idea cannot be related to itself")
        known_ids = {item.get("id") for item in index.get("ideas", [])}
        unknown = [idea_id for idea_id in args.related_idea if idea_id not in known_ids]
        if unknown:
            raise ValueError(f"Related ideas were not found: {', '.join(unknown)}")
        related = unique_extend(metadata.get("related_ideas", []), args.related_idea)
        metadata["related_ideas"] = related
        card = replace_frontmatter_field(card, "related_ideas", related)
    if args.action_track == "incubation-todo":
        if metadata.get("review_after") is None:
            metadata["review_after"] = (date.today() + timedelta(days=7)).isoformat()
            card = replace_frontmatter_field(card, "review_after", metadata["review_after"])
        if args.status is None and metadata.get("status") == "captured":
            metadata["status"] = "incubating"
            card = replace_frontmatter_field(card, "status", "incubating")
    elif args.action_track == "long-term-idea":
        if args.status is None and metadata.get("status") == "incubating":
            metadata["status"] = "captured"
            card = replace_frontmatter_field(card, "status", "captured")
    if args.note is not None:
        card += f"\n\n## 进展 · {now_iso()}\n\n{args.note.strip()}\n"
    metadata["updated_at"] = now_iso()
    atomic_write_text(card_path, card)
    atomic_write_json(index_path, index)
    summary = args.note or args.status or args.novelty or "Updated idea triage"
    append_event("idea.updated", args.id, summary[:160])
    print_json(metadata)


def cmd_list_ideas(args: argparse.Namespace) -> None:
    ideas = read_json(WORKSPACE / "ideas" / "index.json").get("ideas", [])
    if args.status:
        ideas = [item for item in ideas if item.get("status") == args.status]
    print_json(ideas)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show a compact workspace summary")
    status.set_defaults(handler=cmd_status)

    profile = subparsers.add_parser("update-profile", help="Add stable profile facts or interests")
    profile.add_argument("--role")
    profile.add_argument("--experience-years", type=float)
    profile.add_argument("--domain", action="append")
    profile.add_argument("--goal", action="append")
    profile.add_argument("--funnel", action="append")
    profile.add_argument("--paradigm", action="append")
    profile.add_argument("--topic", action="append")
    profile.add_argument("--note", action="append")
    profile.set_defaults(handler=cmd_update_profile)

    mastery = subparsers.add_parser("set-mastery", help="Set a mastery level with evidence")
    mastery.add_argument("--path", required=True)
    mastery.add_argument("--level", required=True, choices=LEVELS)
    mastery.add_argument("--evidence", required=True)
    mastery.add_argument("--source", choices=EVIDENCE_SOURCES, default="observed")
    mastery.set_defaults(handler=cmd_set_mastery)

    thought = subparsers.add_parser("append-thought", help="Append a non-stable thought to the journal")
    thought.add_argument("--text", required=True)
    thought.add_argument("--topic", action="append")
    thought.add_argument("--origin", choices=ORIGINS, default="user")
    thought.set_defaults(handler=cmd_append_thought)

    position = subparsers.add_parser("record-position", help="Record a stable recommendation position")
    position.add_argument("--statement", required=True)
    position.add_argument("--rationale", required=True)
    position.add_argument("--topic", action="append")
    position.add_argument("--origin", choices=ORIGINS, default="user")
    position.add_argument("--supersedes")
    position.set_defaults(handler=cmd_record_position)

    idea = subparsers.add_parser("record-idea", help="Create an idea card and index entry")
    idea.add_argument("--title", required=True)
    idea.add_argument("--note", required=True)
    idea.add_argument("--source-note")
    idea.add_argument("--funnel", action="append")
    idea.add_argument("--paradigm", action="append")
    idea.add_argument("--topic", action="append")
    idea.add_argument("--origin", choices=ORIGINS, default="user")
    idea.add_argument("--scenario-fit", choices=TRIAGE_LEVELS, default="unknown")
    idea.add_argument("--implementation-cost", choices=TRIAGE_LEVELS, default="unknown")
    idea.add_argument("--action-track", choices=ACTION_TRACKS)
    idea.add_argument("--review-after", type=iso_date)
    idea.set_defaults(handler=cmd_record_idea)

    update = subparsers.add_parser("update-idea", help="Update idea status, novelty, or progress")
    update.add_argument("--id", required=True)
    update.add_argument("--status", choices=IDEA_STATUSES)
    update.add_argument("--novelty", choices=NOVELTY_STATUSES)
    update.add_argument("--note")
    update.add_argument("--scenario-fit", choices=TRIAGE_LEVELS)
    update.add_argument("--implementation-cost", choices=TRIAGE_LEVELS)
    update.add_argument("--action-track", choices=ACTION_TRACKS)
    update.add_argument("--review-after", type=iso_date)
    update.add_argument("--related-idea", action="append")
    update.set_defaults(handler=cmd_update_idea)

    list_ideas = subparsers.add_parser("list-ideas", help="List idea metadata")
    list_ideas.add_argument("--status", choices=IDEA_STATUSES)
    list_ideas.set_defaults(handler=cmd_list_ideas)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
