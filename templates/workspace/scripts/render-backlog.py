#!/usr/bin/env python3
"""Render the human-readable Backlog from canonical operations state.

`ACTION_LEDGER.md` and `DECISION_QUEUE.md` remain the source of truth. This
script intentionally renders a readable working surface rather than dumping raw
ledger sections back at the user.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
LEDGER = ROOT / "vault/Operations/ACTION_LEDGER.md"
DECISIONS = ROOT / "vault/Operations/DECISION_QUEUE.md"
BACKLOG = ROOT / "vault/Backlog.md"


def collect_sections(text: str, names: set[str]) -> dict[str, list[str]]:
    current: str | None = None
    out = {name: [] for name in names}
    for line in text.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            current = title if title in names else None
            continue
        if current and line.strip() and not line.strip().startswith("_None"):
            out[current].append(line.rstrip())
    return out


def read_sections(path: Path, names: set[str]) -> dict[str, list[str]]:
    if not path.exists():
        return {name: [] for name in names}
    return collect_sections(path.read_text(), names)


def humanize_item(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("_None"):
        return None

    if stripped.startswith("- [x]"):
        return None

    stripped = re.sub(r"^- \[[ xX]\]\s*", "", stripped)
    parts = [part.strip() for part in stripped.split("|")]

    fields: dict[str, str] = {}
    for part in parts[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            fields[key.strip().lower()] = value.strip()

    summary = fields.get("next") or fields.get("summary") or parts[0]
    status = fields.get("status")
    owner = fields.get("owner")

    suffix = []
    if status and status not in {"open", "candidate", "waiting"}:
        suffix.append(f"status: {status}")
    if owner and owner not in {"{{COS_NAME}}", "{{OPERATOR_NAME}}"}:
        suffix.append(f"owner: {owner}")

    if suffix:
        return f"- {summary} ({'; '.join(suffix)})"
    return f"- {summary}"


def render_list(items: list[str]) -> str:
    rendered = [item for line in items if (item := humanize_item(line))]
    return "\n".join(rendered) if rendered else "_None._"


def main() -> int:
    ledger = read_sections(LEDGER, {"Active", "Waiting", "Candidates"})
    decisions = read_sections(DECISIONS, {"Open Decisions"})
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    candidates = list(ledger["Candidates"])
    for decision in decisions["Open Decisions"]:
        if not decision.strip().startswith("_None"):
            candidates.append("Decision needed | " + decision.strip().lstrip("- "))

    output = f"""---
summary: Human-readable backlog view rendered from the Action Ledger for {{USER_NAME}}
last_updated: "{generated}"
read_when:
  - backlog
  - current tasks
  - open loops outside today
  - planning
---

# Backlog

This is the human-readable backlog. It is rendered from [[Operations/ACTION_LEDGER.md]] and [[Operations/DECISION_QUEUE.md]], which remain the source of truth. Today's selected working set lives in [[Notes and Journal.md#Today]].

## How To Read This

- `Today` is the small daily cockpit.
- `Backlog` is unresolved work outside Today.
- `Waiting` means the next movement depends on another person, system, date, or response.
- `Candidate` means an idea is worth remembering, but not yet committed.
- Domains such as finance, school, projects, housing, and health are context labels. They are not separate planning systems.
- Multi-session builds may have context pages under `Projects/`, but tasks still live in the ledger.
- A Codex thread is only where a task may be worked on; it is not a task status.

## Active Backlog

{render_list(ledger["Active"])}

## Today-Adjacent

These are already visible in [[Notes and Journal.md#Today]], but they are included here so the backlog view stays complete.

_None._

## Waiting

{render_list(ledger["Waiting"])}

## Candidates

{render_list(candidates)}
"""

    BACKLOG.write_text(output)
    print(f"Rendered {BACKLOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
