#!/usr/bin/env python3
"""Build a docs index from markdown files.

Scans configured directories for `.md` files. When a file has YAML frontmatter,
the index uses `summary` and `read_when`; additional fields like
`last_updated` are ignored for index rendering. When a file has no frontmatter
summary, the index falls back to the first 150 characters of body content.
Outputs a compact routing index to DOCS_INDEX.md and a fuller generated index
to DOCS_INDEX.full.md.

Usage:
    python3 scripts/build-docs-index.py
    python3 scripts/build-docs-index.py --project-dir /path/to/project
"""

import sys
import re
from pathlib import Path
from typing import Optional

# Root-level docs to scan explicitly.
ROOT_DOCS = [
]

# Directories to scan (relative to project root).
SCAN_DIRS = [
    "vault",
    "wiki",
    "docs",
]

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "__pycache__",
    "vendor", ".venv", ".env", ".tox", ".mypy_cache", ".ruff_cache",
    "archive",
}

SKIP_NAMES = {"INDEX.md", "README.md", "CHANGELOG.md"}

SUMMARY_FALLBACK_CHARS = 150


def is_compact_skip(rel: Path) -> bool:
    """Return true when a markdown file is too noisy for startup routing."""
    parts = rel.parts

    if parts[:3] == ("vault", "Operations", ".machine"):
        return True

    if (
        len(parts) >= 5
        and parts[:3] == ("vault", "Knowledge", "domains")
        and parts[4] in {"raw", "source-cards"}
    ):
        return True

    if parts and parts[0] == "vault" and "proof" in parts:
        return True

    return False


def extract_frontmatter(file_path: Path) -> tuple[str, list[str], int]:
    """Extract routing fields from YAML frontmatter.

    Returns `(summary, read_when, body_start_line_count)`, where the third value
    is the number of lines consumed before the markdown body begins.
    """
    try:
        with file_path.open() as f:
            first_line = f.readline()
            if not first_line.startswith("---"):
                return "", [], 0
            fm_lines = []
            consumed_lines = 1
            for line in f:
                consumed_lines += 1
                if line.strip() == "---":
                    break
                fm_lines.append(line)
            else:
                return "", [], 0
    except IOError:
        return "", [], 0

    summary = ""
    read_when: list[str] = []
    collecting_read_when = False

    for line in "\n".join(fm_lines).split("\n"):
        stripped = line.strip()

        if stripped.startswith("summary:"):
            summary = stripped[len("summary:"):].strip().strip("'\"")
            collecting_read_when = False
        elif stripped.startswith("read_when:"):
            collecting_read_when = True
        elif collecting_read_when and stripped.startswith("- "):
            hint = stripped[2:].strip()
            if hint:
                read_when.append(hint)
        elif collecting_read_when and stripped:
            collecting_read_when = False

    return summary, read_when, consumed_lines


def summarize_body(file_path: Path, body_start_line_count: int) -> str:
    """Return a compact summary excerpt from the markdown body."""
    try:
        text = file_path.read_text()
    except IOError:
        return ""

    if body_start_line_count:
        lines = text.splitlines()
        text = "\n".join(lines[body_start_line_count:])

    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"^\s{0,3}#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()

    return text[:SUMMARY_FALLBACK_CHARS].rstrip()


def build_entry(file_path: Path, project_dir: Path) -> Optional[str]:
    """Build one docs index entry from a markdown file."""
    summary, read_when, body_start_line_count = extract_frontmatter(file_path)
    if not summary:
        summary = summarize_body(file_path, body_start_line_count)
    if not summary:
        return None

    rel = file_path.relative_to(project_dir)
    entry = f"- [[{rel}]] — {summary}"
    if read_when:
        entry += f"\n  Read when: {'; '.join(read_when)}"
    return entry


def scan_directory(dir_path: Path, project_dir: Path, *, compact: bool) -> list[str]:
    """Scan a directory for markdown files."""
    if not dir_path.exists():
        return []

    entries = []
    for md_file in sorted(dir_path.rglob("*.md")):
        rel = md_file.relative_to(project_dir)

        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if md_file.name in SKIP_NAMES:
            continue
        if compact and is_compact_skip(rel):
            continue

        entry = build_entry(md_file, project_dir)
        if not entry:
            continue
        entries.append(entry)

    return entries


def scan_file(file_path: Path, project_dir: Path) -> Optional[str]:
    """Scan a single markdown file."""
    if not file_path.exists() or not file_path.is_file():
        return None

    return build_entry(file_path, project_dir)


def build_sections(project_dir: Path, *, compact: bool) -> tuple[list[str], int]:
    sections: list[str] = []
    total_docs = 0

    root_entries = []
    for root_doc in ROOT_DOCS:
        entry = scan_file(project_dir / root_doc, project_dir)
        if entry:
            root_entries.append(entry)

    if root_entries:
        sections.append("## core/\n\n" + "\n".join(root_entries))
        total_docs += len(root_entries)

    for scan_dir in SCAN_DIRS:
        dir_path = project_dir / scan_dir
        entries = scan_directory(dir_path, project_dir, compact=compact)
        if entries:
            sections.append(f"## {scan_dir}/\n\n" + "\n".join(entries))
            total_docs += len(entries)

    return sections, total_docs


def render_index(*, compact: bool, sections: list[str]) -> str:
    output = "# Docs Index\n\n"
    output += "Auto-generated by `scripts/build-docs-index.py`. "
    output += "Read matching docs before working on a task."
    if compact:
        output += (
            " This compact routing index omits machine state, raw knowledge "
            "captures, source cards, and proof folders. Use "
            "`DOCS_INDEX.full.md` when you need exhaustive artifact discovery."
        )
    else:
        output += " This full index includes lower-level artifacts omitted from the compact startup index."
    output += "\n\n"
    output += "\n\n".join(sections) + "\n"
    return output


def main():
    project_dir = Path.cwd()

    # Allow override via --project-dir flag
    if "--project-dir" in sys.argv:
        idx = sys.argv.index("--project-dir")
        if idx + 1 < len(sys.argv):
            project_dir = Path(sys.argv[idx + 1])

    compact_sections, compact_total = build_sections(project_dir, compact=True)
    full_sections, full_total = build_sections(project_dir, compact=False)

    if not compact_sections and not full_sections:
        print("No markdown docs found.", file=sys.stderr)
        sys.exit(0)

    compact_output_path = project_dir / "DOCS_INDEX.md"
    full_output_path = project_dir / "DOCS_INDEX.full.md"

    compact_output_path.write_text(render_index(compact=True, sections=compact_sections))
    full_output_path.write_text(render_index(compact=False, sections=full_sections))

    print(
        f"Wrote {compact_output_path} "
        f"({len(compact_sections)} sections, {compact_total} docs)"
    )
    print(
        f"Wrote {full_output_path} "
        f"({len(full_sections)} sections, {full_total} docs)"
    )


if __name__ == "__main__":
    main()
