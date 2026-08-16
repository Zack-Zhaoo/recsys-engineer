#!/usr/bin/env python3
"""Validate recsys-engineer structure, links, evidence IDs, license, and workspace state.

Purpose:
    Provide a deterministic public-release gate beyond the generic AgentSkill
    validator. It checks the fixed 2026-08-01 snapshot and ensures that the
    distributable workspace contains no fabricated personal data.

Usage examples:
    python3 scripts/validate_skill.py
    python3 scripts/validate_skill.py /path/to/recsys-engineer
    python3 scripts/validate_skill.py --allow-personalized

Arguments:
    The optional path defaults to the skill directory containing this script.
    --allow-personalized skips only the clean-public-workspace checks.

Prerequisites and side effects:
    Python 3.9+ is required. The command is read-only and uses only the standard
    library; it does not access the network or alter skill/workspace files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


SNAPSHOT_DATE = "2026-08-01"
REQUIRED_FILES = [
    "SKILL.md",
    "LICENSE.md",
    "USAGE.md",
    "knowledge/snapshot.md",
    "knowledge/core/landscape.md",
    "knowledge/core/foundations.md",
    "knowledge/core/learning-paths.md",
    "knowledge/core/glossary.md",
    "knowledge/funnel/end-to-end.md",
    "knowledge/funnel/retrieval.md",
    "knowledge/funnel/pre-ranking.md",
    "knowledge/funnel/ranking.md",
    "knowledge/funnel/reranking-and-policy.md",
    "knowledge/funnel/feedback-loop.md",
    "knowledge/paradigms/large-ranking-models.md",
    "knowledge/paradigms/generative-recommendation.md",
    "knowledge/paradigms/llm-in-recommendation.md",
    "knowledge/paradigms/agentic-recommendation.md",
    "knowledge/paradigms/multimodal-recommendation.md",
    "knowledge/engineering/data-and-sampling.md",
    "knowledge/engineering/features-and-embeddings.md",
    "knowledge/engineering/training-and-serving.md",
    "knowledge/engineering/evaluation-and-experimentation.md",
    "knowledge/engineering/reliability-and-governance.md",
    "knowledge/research/frontier-map.md",
    "knowledge/research/open-problems.md",
    "knowledge/research/experiment-design.md",
    "knowledge/industry/landscape.md",
    "knowledge/industry/timeline.md",
    "knowledge/industry/production-cases.md",
    "knowledge/industry/articles/index.md",
    "knowledge/industry/articles/catalog.yaml",
    "knowledge/industry/articles/meta.md",
    "knowledge/industry/articles/youtube.md",
    "knowledge/industry/articles/meituan.md",
    "knowledge/industry/articles/bytedance.md",
    "knowledge/industry/articles/alibaba.md",
    "knowledge/industry/articles/tencent.md",
    "knowledge/industry/articles/kuaishou.md",
    "knowledge/industry/articles/ximalaya.md",
    "knowledge/sources/evidence-policy.md",
    "knowledge/sources/catalog.yaml",
    "perspective/index.md",
    "perspective/principles.md",
    "perspective/research-evaluation.md",
    "perspective/learning-philosophy.md",
    "perspective/idea-and-experiment-loop.md",
    "perspective/product-and-governance.md",
    "perspective/frontier-theses/map.md",
    "perspective/frontier-theses/agentic-recommendation.md",
    "perspective/frontier-theses/auto-rs.md",
    "perspective/frontier-theses/rs-in-ai.md",
    "perspective/frontier-theses/one-model-limits.md",
    "playbooks/learn-recsys.md",
    "playbooks/design-system.md",
    "playbooks/diagnose-system.md",
    "playbooks/compare-methods.md",
    "playbooks/analyze-paper.md",
    "playbooks/capture-idea.md",
    "playbooks/develop-idea.md",
    "playbooks/turn-idea-into-experiment.md",
    "playbooks/review-experiment.md",
    "schemas/profile.schema.json",
    "schemas/mastery.schema.json",
    "schemas/idea.schema.json",
    "workspace/profile.json",
    "workspace/mastery.json",
    "workspace/thinking/journal.md",
    "workspace/thinking/positions.json",
    "workspace/ideas/index.json",
    "README.md",
    "README.en.md",
    "scripts/manage_workspace.py",
    "scripts/upgrade.py",
    "scripts/validate_skill.py",
    "scripts/build_skill_package.py",
    "scripts/refresh_snapshot.py",
]
SOURCE_PATTERN = re.compile(r"\[(SRC-[A-Z0-9-]+)\]")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PLACEHOLDER_PATTERN = re.compile(r"\{\{([^{}]+)\}\}")
# Build output and VCS metadata live inside the repo but are not part of the skill.
IGNORED_DIRS = {"dist", "__pycache__"}


def iter_files(root: Path, pattern: str = "*"):
    """Yield skill files, skipping build output, caches and dot-directories."""
    for path in sorted(root.rglob(pattern)):
        parts = path.relative_to(root).parts[:-1] if path.is_file() else path.relative_to(root).parts
        if any(part in IGNORED_DIRS or part.startswith(".") for part in parts):
            continue
        yield path


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON-compatible file {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"Expected a JSON object in {path}")
        return {}
    return value


def validate_frontmatter(root: Path, errors: list[str]) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return
    text = skill_path.read_text(encoding="utf-8")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds the 500-line progressive-disclosure limit")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        errors.append("SKILL.md is missing valid YAML frontmatter fences")
        return
    frontmatter = match.group(1)
    fields = re.findall(r"^([A-Za-z0-9_-]+):", frontmatter, flags=re.MULTILINE)
    if fields != ["name", "description"]:
        errors.append(f"SKILL.md frontmatter must contain only name and description, found: {fields}")
    if not re.search(r"^name:\s*recsys-engineer\s*$", frontmatter, flags=re.MULTILINE):
        errors.append("SKILL.md name must be recsys-engineer")
    if SNAPSHOT_DATE not in text:
        errors.append(f"SKILL.md must state the fixed snapshot date {SNAPSHOT_DATE}")


def validate_links(root: Path, errors: list[str]) -> None:
    for markdown_path in iter_files(root, "*.md"):
        text = markdown_path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (markdown_path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"Link escapes skill root: {markdown_path.relative_to(root)} -> {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"Broken link: {markdown_path.relative_to(root)} -> {raw_target}")


def validate_no_placeholders(root: Path, errors: list[str]) -> None:
    """Block release while any {{...}} authoring slot is still unfilled."""
    for markdown_path in iter_files(root, "*.md"):
        text = markdown_path.read_text(encoding="utf-8")
        for slot in sorted(set(PLACEHOLDER_PATTERN.findall(text))):
            errors.append(f"Unfilled placeholder {{{{{slot}}}}} in {markdown_path.relative_to(root)}")


def validate_sources(root: Path, errors: list[str]) -> None:
    identifiers: list[str] = []
    catalog_specs = [
        (root / "knowledge" / "sources" / "catalog.yaml", "paper"),
        (root / "knowledge" / "industry" / "articles" / "catalog.yaml", "industry"),
    ]
    for catalog_path, catalog_type in catalog_specs:
        catalog = load_json(catalog_path, errors)
        if not catalog:
            continue
        label = str(catalog_path.relative_to(root))
        if catalog.get("snapshot_date") != SNAPSHOT_DATE:
            errors.append(f"{label} snapshot_date must be {SNAPSHOT_DATE}")
        entries = catalog.get("entries", [])
        if not isinstance(entries, list):
            errors.append(f"{label} entries must be a list")
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"{label} contains a non-object entry")
                continue
            source_id = entry.get("id")
            if not isinstance(source_id, str) or not source_id.startswith("SRC-"):
                errors.append(f"Invalid source id in {label}: {source_id!r}")
                continue
            identifiers.append(source_id)
            if not str(entry.get("url", "")).startswith("https://"):
                errors.append(f"Source {source_id} must use an https URL")
            if not isinstance(entry.get("title"), str) or not entry["title"].strip():
                errors.append(f"Source {source_id} must have a title")
            if catalog_type == "paper":
                if not isinstance(entry.get("year"), int) or entry["year"] > 2026:
                    errors.append(f"Source {source_id} is outside the fixed snapshot year")
                continue
            for field in ("company_group", "publisher", "kind"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    errors.append(f"Industry source {source_id} must have {field}")
            if entry.get("authority") not in {"official", "team", "secondary"}:
                errors.append(f"Industry source {source_id} has invalid authority")
            if not isinstance(entry.get("topics"), list) or not entry["topics"]:
                errors.append(f"Industry source {source_id} must have topics")
            published = entry.get("published")
            if published is None:
                date_status = entry.get("date_status")
                if not isinstance(date_status, str) or not re.fullmatch(r"unverified|year-only-\d{4}", date_status):
                    errors.append(f"Industry source {source_id} needs a date_status")
                elif date_status.startswith("year-only-") and int(date_status[-4:]) > 2026:
                    errors.append(f"Industry source {source_id} is outside the snapshot year")
            elif not isinstance(published, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", published):
                errors.append(f"Industry source {source_id} has invalid published date")
            elif published > SNAPSHOT_DATE:
                errors.append(f"Industry source {source_id} is after the snapshot date")
    if len(identifiers) != len(set(identifiers)):
        errors.append("Source catalogs contain duplicate source ids")
    known = set(identifiers)
    used: set[str] = set()
    for path in iter_files(root, "*.md"):
        used.update(SOURCE_PATTERN.findall(path.read_text(encoding="utf-8")))
    for source_id in sorted(used - known):
        errors.append(f"Unknown evidence source id: {source_id}")
    for source_id in sorted(known - used):
        errors.append(f"Cataloged source is not referenced by knowledge files: {source_id}")


def validate_json_files(root: Path, errors: list[str]) -> None:
    for path in iter_files(root, "*.json"):
        load_json(path, errors)


def validate_clean_workspace(root: Path, errors: list[str]) -> None:
    profile = load_json(root / "workspace" / "profile.json", errors)
    if profile:
        if profile.get("role") is not None or profile.get("experience_years") is not None:
            errors.append("Public workspace profile must not contain a role or experience")
        for field in ("domains", "goals", "notes"):
            if profile.get(field) != []:
                errors.append(f"Public workspace profile.{field} must be empty")
        interests = profile.get("interests", {})
        if any(interests.get(field) != [] for field in ("funnel", "paradigms", "topics")):
            errors.append("Public workspace profile interests must be empty")
        if profile.get("updated_at") is not None:
            errors.append("Public workspace profile.updated_at must be null")

    mastery = load_json(root / "workspace" / "mastery.json", errors)
    for module_name, module in mastery.get("modules", {}).items():
        if module.get("level") != "unassessed" or module.get("evidence") != []:
            errors.append(f"Public workspace mastery must be unassessed: {module_name}")
        if module.get("updated_at") is not None:
            errors.append(f"Public workspace mastery timestamp must be null: {module_name}")

    positions = load_json(root / "workspace" / "thinking" / "positions.json", errors)
    if positions.get("positions") != []:
        errors.append("Public workspace positions must be empty")
    ideas = load_json(root / "workspace" / "ideas" / "index.json", errors)
    if ideas.get("ideas") != []:
        errors.append("Public workspace ideas must be empty")
    cards = root / "workspace" / "ideas" / "cards"
    if cards.exists() and any(cards.iterdir()):
        errors.append("Public workspace must not contain idea cards")
    events = root / "workspace" / "history" / "events.jsonl"
    if events.exists() and events.read_text(encoding="utf-8").strip():
        errors.append("Public workspace must not contain history events")
    journal = root / "workspace" / "thinking" / "journal.md"
    if journal.exists() and re.search(r"^## \d{4}-\d{2}-\d{2}T", journal.read_text(encoding="utf-8"), re.MULTILINE):
        errors.append("Public workspace journal must not contain personal entries")


def validate_layout(root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"Missing required file: {relative}")
    for path in iter_files(root):
        if path.is_dir() and path.name == "references":
            errors.append(f"Use knowledge/ instead of references/: {path.relative_to(root)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the recsys-engineer skill directory",
    )
    parser.add_argument(
        "--allow-personalized",
        action="store_true",
        help="Skip clean-public-workspace checks for a user's local copy",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.skill_root.resolve()
    errors: list[str] = []
    validate_layout(root, errors)
    validate_frontmatter(root, errors)
    validate_json_files(root, errors)
    validate_links(root, errors)
    validate_no_placeholders(root, errors)
    validate_sources(root, errors)
    if not args.allow_personalized:
        validate_clean_workspace(root, errors)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
