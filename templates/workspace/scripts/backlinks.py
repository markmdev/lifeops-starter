#!/usr/bin/env python3
"""Print Obsidian-style backlinks for a markdown file.

Usage:
  python3 scripts/backlinks.py vault/Health/Health.md
  python3 scripts/backlinks.py "vault/Health/Health.md" --root .
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SCAN_DIRS = ["vault", "docs", "wiki"]
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def normalize_target(path: Path, root: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        rel = path
    rel_str = rel.as_posix()
    if rel_str.endswith('.md'):
        rel_str = rel_str[:-3]
    return rel_str


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    target = (root / args.target).resolve() if not Path(args.target).is_absolute() else Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"Target not found: {target}")

    target_keys = {
        normalize_target(target, root),
        target.relative_to(root).as_posix() if target.is_relative_to(root) else target.as_posix(),
    }

    matches: list[str] = []
    for scan_dir in SCAN_DIRS:
        base = root / scan_dir
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if path.resolve() == target:
                continue
            text = path.read_text()
            links = LINK_RE.findall(text)
            normalized = {link[:-3] if link.endswith('.md') else link for link in links}
            if normalized & target_keys:
                matches.append(path.relative_to(root).as_posix())

    if not matches:
        print("No backlinks found.")
        return 0

    for match in sorted(matches):
        print(match)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
