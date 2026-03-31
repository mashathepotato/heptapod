#!/usr/bin/env python3
"""
# test_findings.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for the findings ledger module.

Run with:
    python test_findings.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add repo root to path
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.logging.findings import append_finding, read_findings, FINDINGS_HEADER


def test_creates_file_with_header():
    """First call creates findings.md with header."""
    print("=" * 60)
    print("Testing creates_file_with_header")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        path = append_finding(tmp, "Test Heading", ["Entry 1", "Entry 2"])
        assert os.path.exists(path), "findings.md was not created"
        content = open(path).read()
        assert content.startswith(FINDINGS_HEADER), "Missing header"
        assert "## 1. Test Heading" in content, "Missing section heading"
        assert "- Entry 1" in content, "Missing entry 1"
        assert "- Entry 2" in content, "Missing entry 2"
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_auto_numbers_sections():
    """Subsequent calls increment section numbers."""
    print("=" * 60)
    print("Testing auto_numbers_sections")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        append_finding(tmp, "First", ["A"])
        append_finding(tmp, "Second", ["B"])
        append_finding(tmp, "Third", ["C"])

        content = read_findings(tmp)
        assert "## 1. First" in content
        assert "## 2. Second" in content
        assert "## 3. Third" in content
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_empty_entries_skipped():
    """Empty entry strings are filtered out."""
    print("=" * 60)
    print("Testing empty_entries_skipped")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        append_finding(tmp, "Heading", ["Good", "", "Also good"])
        content = read_findings(tmp)
        assert "- Good" in content
        assert "- Also good" in content
        lines = content.split("\n")
        assert not any(line.strip() == "-" for line in lines), "Bare dash line found"
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_returns_filepath():
    """Returns path to findings file."""
    print("=" * 60)
    print("Testing returns_filepath")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        path = append_finding(tmp, "Test", ["X"])
        assert path == os.path.join(tmp, "findings.md")
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_returns_empty_when_no_file():
    """Returns empty string when findings.md doesn't exist."""
    print("=" * 60)
    print("Testing returns_empty_when_no_file")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        assert read_findings(tmp) == "", "Expected empty string"
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_returns_content():
    """Returns file contents after appending."""
    print("=" * 60)
    print("Testing returns_content")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        append_finding(tmp, "Heading", ["Entry"])
        content = read_findings(tmp)
        assert "## 1. Heading" in content
        assert "- Entry" in content
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def test_accumulates_multiple():
    """Multiple appends accumulate in order."""
    print("=" * 60)
    print("Testing accumulates_multiple")
    print("=" * 60)

    tmp = tempfile.mkdtemp()
    try:
        append_finding(tmp, "Diagrams: H → b b̄", ["Found 1 diagram"])
        append_finding(tmp, "NDA: H → b b̄", ["Γ = 2.69e-02 GeV"])
        content = read_findings(tmp)
        assert "## 1. Diagrams" in content
        assert "## 2. NDA" in content
        pos1 = content.index("## 1.")
        pos2 = content.index("## 2.")
        assert pos1 < pos2, "Sections not in order"
        print("  PASS")
        return True
    except AssertionError as e:
        print(f"  [✗] FAIL: {e}")
        return False
    finally:
        shutil.rmtree(tmp)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Findings Ledger Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Creates file with header", test_creates_file_with_header),
        ("Auto numbers sections", test_auto_numbers_sections),
        ("Empty entries skipped", test_empty_entries_skipped),
        ("Returns filepath", test_returns_filepath),
        ("Returns empty when no file", test_returns_empty_when_no_file),
        ("Returns content", test_returns_content),
        ("Accumulates multiple", test_accumulates_multiple),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, "[✓] PASS" if result else "[✗] FAIL"))
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            results.append((name, "[✗] ERROR"))

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, status in results:
        print(f"  {status}: {name}")

    passed = sum(1 for _, s in results if s == "[✓] PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
