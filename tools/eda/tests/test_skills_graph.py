#!/usr/bin/env python3
"""
# test_skills_graph.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for SkillsGraph theory knowledge base.

Run with:
    python test_skills_graph.py
"""

import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.eda.theory.skills_graph import SkillsGraph


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

def test_loading():
    """Test that SkillsGraph loads and has expected categories."""
    print("=" * 60)
    print("Testing SkillsGraph loading")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    nodes = graph.list_all()
    ok = len(nodes) > 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: loads graph JSON ({len(nodes)} nodes)")

    categories = {n["category"] for n in nodes}
    expected = {
        "procedure", "feynman_rules", "spin_sums",
        "trace_identities", "phase_space", "feyncalc_reference",
        "worked_example",
    }
    ok = expected == categories
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: all categories present")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

def test_get():
    """Test SkillsGraph.get() method."""
    print("=" * 60)
    print("Testing SkillsGraph.get()")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    # existing node
    content = graph.get("procedures.decay_width_1to2")
    ok = content is not None and len(content) > 100 and (
        "decay" in content.lower() or "width" in content.lower()
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: get existing node")

    # nonexistent node
    content = graph.get("nonexistent.node")
    ok = content is None
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: get nonexistent node returns None")

    # worked example
    content = graph.get("worked_examples.h_to_bb")
    ok = content is not None and ("FeynCalc" in content or "feyncalc" in content.lower())
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: get worked example")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

def test_links():
    """Test SkillsGraph.links() method."""
    print("=" * 60)
    print("Testing SkillsGraph.links()")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    # links exist
    links = graph.links("feynman_rules.vertices_scalar")
    ok = len(links) > 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: links exist for vertices_scalar")

    # all links are valid keys
    all_keys = {n["key"] for n in graph.list_all()}
    broken = []
    for node in graph.list_all():
        for link in graph.links(node["key"]):
            if link not in all_keys:
                broken.append(f"{node['key']} -> {link}")
    ok = len(broken) == 0
    if not ok:
        all_passed = False
        for b in broken:
            print(f"    Broken link: {b}")
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: all links are valid keys")

    # nonexistent key
    links = graph.links("nonexistent.key")
    ok = links == []
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: nonexistent key returns empty list")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search():
    """Test SkillsGraph.search() method."""
    print("=" * 60)
    print("Testing SkillsGraph.search()")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    results = graph.search("gamma")
    ok = len(results) > 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: search 'gamma' returns results")

    # case insensitive
    results_lower = graph.search("feyncalc")
    results_upper = graph.search("FeynCalc")
    ok = len(results_lower) > 0 and len(results_upper) > 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: search is case insensitive")

    # no results
    results = graph.search("xyzzy_nonexistent_term_12345")
    ok = len(results) == 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: search for nonexistent term returns empty")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# List procedures / by category
# ---------------------------------------------------------------------------

def test_list_procedures():
    """Test SkillsGraph.list_procedures() and list_by_category()."""
    print("=" * 60)
    print("Testing list_procedures and list_by_category")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    # list procedures
    procs = graph.list_procedures()
    keys = [p["key"] for p in procs]
    ok = (
        len(procs) >= 2
        and "procedures.decay_width_1to2" in keys
        and "procedures.cross_section_2to2" in keys
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: list_procedures")

    # feynman rules
    nodes = graph.list_by_category("feynman_rules")
    ok = len(nodes) >= 3
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: list_by_category('feynman_rules') >= 3")

    # worked examples
    nodes = graph.list_by_category("worked_example")
    ok = len(nodes) >= 3
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: list_by_category('worked_example') >= 3")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Document content
# ---------------------------------------------------------------------------

def test_document_content():
    """Verify that all registered documents exist and have content."""
    print("=" * 60)
    print("Testing document content")
    print("=" * 60)

    graph = SkillsGraph()
    all_passed = True

    # all documents exist
    missing = []
    for node in graph.list_all():
        content = graph.get(node["key"])
        if content is None:
            missing.append(node["key"])
    ok = len(missing) == 0
    if not ok:
        all_passed = False
        for m in missing:
            print(f"    Missing: {m}")
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: all documents exist")

    # all documents have content
    empty = []
    for node in graph.list_all():
        content = graph.get(node["key"])
        if content is not None and len(content.strip()) < 50:
            empty.append(node["key"])
    ok = len(empty) == 0
    if not ok:
        all_passed = False
        for e in empty:
            print(f"    Nearly empty: {e}")
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: all documents have content (>50 chars)")

    print()
    return all_passed


# ==================== Runner ==================== #

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SkillsGraph Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Loading", test_loading),
        ("Get", test_get),
        ("Links", test_links),
        ("Search", test_search),
        ("List procedures / by category", test_list_procedures),
        ("Document content", test_document_content),
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
    print(f"\nTotal: {passed}/{total} test groups passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
