#!/usr/bin/env python3
"""Lint Obsidian links inside the vault.

The Obsidian vault root is `vault/`, so vault-internal wikilinks should be
relative to that root, for example `[[Operations/ACTION_LEDGER.md]]`.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


VAULT_ROOT = Path("vault")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
CODE_SPAN_WIKILINK_RE = re.compile(r"`(\[\[[^\]]+\]\])`")

PREFIX_REWRITES = {
    "vault/": "",
    "personal/Career/": "Career/",
    "personal/Finance/": "Finance/",
    "personal/Health/": "Health/",
    "personal/Immigration/": "Immigration/",
    "personal/People/": "People/",
}


@dataclass
class Finding:
    path: Path
    line: int
    kind: str
    value: str


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def split_target(raw: str) -> tuple[str, str]:
    alias = ""
    target = raw
    if "|" in target:
        target, alias = target.split("|", 1)
        alias = "|" + alias
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    return target, anchor + alias


def rewrite_target(target: str) -> str:
    for old, new in PREFIX_REWRITES.items():
        if target.startswith(old):
            return new + target[len(old):]
    return target


def target_exists(target: str) -> bool:
    if not target or target.startswith(("http://", "https://")):
        return True
    if target.startswith(("/Users/", "clawd/", "../")):
        return False

    candidate = VAULT_ROOT / target
    if candidate.exists():
        return True
    if candidate.suffix:
        return False
    return candidate.with_suffix(".md").exists()


def lint_file(path: Path) -> list[Finding]:
    text = path.read_text(errors="replace")
    findings: list[Finding] = []

    for match in CODE_SPAN_WIKILINK_RE.finditer(text):
        findings.append(
            Finding(path, line_number(text, match.start()), "code-spanned-wikilink", match.group(1))
        )

    for match in WIKILINK_RE.finditer(text):
        raw = match.group(1)
        target, _suffix = split_target(raw)

        if target.startswith(("vault/", "personal/", "/Users/", "clawd/", "../")):
            findings.append(
                Finding(path, line_number(text, match.start()), "bad-prefix", raw)
            )
            continue

        if not target_exists(target):
            findings.append(
                Finding(path, line_number(text, match.start()), "missing-target", raw)
            )

    return findings


def fix_file(path: Path) -> bool:
    text = path.read_text()
    original = text

    text = CODE_SPAN_WIKILINK_RE.sub(r"\1", text)

    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        target, suffix = split_target(raw)
        new_target = rewrite_target(target)
        return f"[[{new_target}{suffix}]]"

    text = WIKILINK_RE.sub(replace, text)

    if text != original:
        path.write_text(text)
        return True
    return False


def iter_markdown() -> list[Path]:
    if not VAULT_ROOT.exists():
        return []
    return sorted(VAULT_ROOT.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Rewrite safe prefix/code-span issues")
    args = parser.parse_args()

    if args.fix:
        changed = [path for path in iter_markdown() if fix_file(path)]
        for path in changed:
            print(f"fixed {path}")

    findings: list[Finding] = []
    for path in iter_markdown():
        findings.extend(lint_file(path))

    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.value}")

    if findings:
        print(f"{len(findings)} finding(s)")
        return 1

    print("0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
