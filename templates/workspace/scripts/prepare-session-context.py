#!/usr/bin/env python3
"""Prepare session bootstrap context for this repo.

This script rebuilds the compact and full docs indexes used for session
routing. It is intentionally lightweight; deeper context still lives in the
vault and project docs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path.cwd()
DOCS_INDEX_SCRIPT = PROJECT_DIR / "scripts" / "build-docs-index.py"


def main() -> None:
    subprocess.run(
        [sys.executable, str(DOCS_INDEX_SCRIPT), "--project-dir", str(PROJECT_DIR)],
        check=True,
        cwd=PROJECT_DIR,
    )
    print(f"Prepared session routing context in {PROJECT_DIR}")


if __name__ == "__main__":
    main()
