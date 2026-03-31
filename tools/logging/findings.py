"""
# findings.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Results Ledger — shared markdown file that tools auto-append findings to.

Each tool appends a numbered section to {base_directory}/findings.md so the
agent can read it at the end of a multi-step analysis and produce a summary.
"""

import os
import re


FINDINGS_FILENAME = "findings.md"
FINDINGS_HEADER = "# Analysis Findings\n"


def append_finding(base_directory: str, heading: str, entries: list) -> str:
    """Append a finding section to the shared ledger.

    Args:
        base_directory: Sandbox root directory.
        heading: Section title (e.g., "NDA: H → bb̄").
        entries: List of bullet-point strings (without leading "- ").

    Returns:
        Path to the findings file.
    """
    filepath = os.path.join(base_directory, FINDINGS_FILENAME)

    # Read existing content (or start fresh)
    existing = ""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing = f.read()

    # Auto-number: count existing ## N. headers
    section_numbers = re.findall(r"^## (\d+)\.", existing, re.MULTILINE)
    next_num = max((int(n) for n in section_numbers), default=0) + 1

    # Build new section
    bullets = "\n".join(f"- {entry}" for entry in entries if entry)
    section = f"\n## {next_num}. {heading}\n{bullets}\n"

    # Write (create with header if new)
    if not existing:
        existing = FINDINGS_HEADER

    with open(filepath, "w") as f:
        f.write(existing + section)

    return filepath


def read_findings(base_directory: str) -> str:
    """Read the current findings ledger contents.

    Args:
        base_directory: Sandbox root directory.

    Returns:
        Contents of findings.md, or empty string if not found.
    """
    filepath = os.path.join(base_directory, FINDINGS_FILENAME)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r") as f:
        return f.read()
