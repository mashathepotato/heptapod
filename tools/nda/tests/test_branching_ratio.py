#!/usr/bin/env python3
"""
# test_branching_ratio.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for EstimateBranchingRatioNDATool.

Run with:
    python test_branching_ratio.py
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

# Path setup
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.nda import EstimateBranchingRatioNDATool, EstimateDecayWidthNDATool


# A simple 3-body muon decay diagram (mu- -> e- nu_ebar nu_mu) with 1 W propagator
MUON_DIAGRAM_1W = {
    "topology": "tree_3body_1prop",
    "initial": [{"label": "mu-", "spin": 0.5, "mass": 0.10566}],
    "final": [
        {"label": "e-", "spin": 0.5, "mass": 0.000511},
        {"label": "nu_ebar", "spin": 0.5, "mass": 0.0},
        {"label": "nu_mu", "spin": 0.5, "mass": 0.0}
    ],
    "vertices": [
        {"type": "gauge-vector", "coupling": "g_w"},
        {"type": "gauge-vector", "coupling": "g_w"}
    ],
    "propagators": [
        {"label": "W", "mass": 80.379, "spin": 1, "regime": "heavy"}
    ],
    "couplings": {"g_w": 0.653},
    "color_factor": 1.0
}

# A contact (Fermi) diagram for the same process — no propagator
MUON_DIAGRAM_CONTACT = {
    "topology": "tree_3body",
    "initial": [{"label": "mu-", "spin": 0.5, "mass": 0.10566}],
    "final": [
        {"label": "e-", "spin": 0.5, "mass": 0.000511},
        {"label": "nu_ebar", "spin": 0.5, "mass": 0.0},
        {"label": "nu_mu", "spin": 0.5, "mass": 0.0}
    ],
    "vertices": [
        {"type": "dim6-4fermion", "coupling": "G_F"}
    ],
    "propagators": [],
    "couplings": {"G_F": 1.166e-5},
    "color_factor": 1.0
}


def test_basic_branching_ratio():
    """Test BR calculation with two diagram classes and a fixed reference width."""
    print("=" * 60)
    print("Testing basic branching ratio")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        # Use an arbitrary reference width for testing
        reference_width = 3.0e-19  # ~ muon total width in GeV

        tool = EstimateBranchingRatioNDATool(
            diagram_classes=[
                {"diagram": MUON_DIAGRAM_1W, "n_diagrams": 5, "n_heavy": 1},
                {"diagram": MUON_DIAGRAM_CONTACT, "n_diagrams": 1, "n_heavy": 0},
            ],
            reference_width=reference_width,
            reference_label="Muon total width",
            process_label="Test BR",
            base_directory=base_dir,
        )

        result_json = tool._run()
        result = json.loads(result_json)

        assert result["status"] == "ok", f"Tool failed: {result}"
        assert result["n_classes"] == 2
        assert result["n_diagrams_total"] == 6
        assert result["partial_width_gev"] > 0
        assert result["branching_ratio"] > 0
        assert result["reference_width_gev"] == reference_width
        assert len(result["class_results"]) == 2

        print("  [✓] PASS: All basic BR checks passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_branching_ratio_summary_table():
    """Test that a markdown summary table is generated."""
    print("=" * 60)
    print("Testing branching ratio summary table")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateBranchingRatioNDATool(
            diagram_classes=[
                {"diagram": MUON_DIAGRAM_1W, "n_diagrams": 3, "n_heavy": 1},
            ],
            reference_width=3.0e-19,
            process_label="Test summary",
            include_summary=True,
            base_directory=base_dir,
        )

        result_json = tool._run()
        result = json.loads(result_json)

        assert result["status"] == "ok"
        assert "summary_table" in result
        table = result["summary_table"]
        assert "Heavy Props" in table
        assert "Diagrams" in table
        assert "Width/Diagram" in table
        assert "BR" in table

        print("  [✓] PASS: Summary table checks passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_branching_ratio_no_summary():
    """Test that summary table can be suppressed."""
    print("=" * 60)
    print("Testing branching ratio no summary")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateBranchingRatioNDATool(
            diagram_classes=[
                {"diagram": MUON_DIAGRAM_1W, "n_diagrams": 1, "n_heavy": 1},
            ],
            reference_width=3.0e-19,
            include_summary=False,
            base_directory=base_dir,
        )

        result_json = tool._run()
        result = json.loads(result_json)

        assert result["status"] == "ok"
        assert "summary_table" not in result

        print("  [✓] PASS: No-summary check passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_branching_ratio_bad_reference():
    """Test that invalid reference_width is rejected."""
    print("=" * 60)
    print("Testing branching ratio bad reference")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateBranchingRatioNDATool(
            diagram_classes=[
                {"diagram": MUON_DIAGRAM_1W, "n_diagrams": 1, "n_heavy": 1},
            ],
            reference_width=-1.0,
            base_directory=base_dir,
        )

        result_str = tool._run()
        # format_error returns plain text, not JSON
        assert "Error" in result_str or "Invalid" in result_str

        print("  [✓] PASS: Bad reference check passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_branching_ratio_empty_classes():
    """Test that empty diagram_classes list is rejected."""
    print("=" * 60)
    print("Testing branching ratio empty classes")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateBranchingRatioNDATool(
            diagram_classes=[],
            reference_width=3.0e-19,
            base_directory=base_dir,
        )

        result_str = tool._run()
        assert "Error" in result_str or "empty" in result_str.lower()

        print("  [✓] PASS: Empty classes check passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_single_nda_still_works():
    """Verify that the simplified single-diagram NDA tool still works."""
    print("=" * 60)
    print("Testing single NDA tool still works")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=MUON_DIAGRAM_1W,
            include_summary=False,
            base_directory=base_dir,
        )

        result_json = tool._run()
        result = json.loads(result_json)

        assert result["status"] == "ok"
        assert result["width_gev"] > 0
        assert "formula" in result
        # breakdown moved to findings ledger in lean returns
        assert "breakdown" not in result

        print("  [✓] PASS: Single NDA tool checks passed")
        return True
    finally:
        shutil.rmtree(base_dir)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Branching Ratio NDA Tool Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Basic branching ratio", test_basic_branching_ratio),
        ("Summary table", test_branching_ratio_summary_table),
        ("No summary", test_branching_ratio_no_summary),
        ("Bad reference width", test_branching_ratio_bad_reference),
        ("Empty classes", test_branching_ratio_empty_classes),
        ("Single NDA tool", test_single_nda_still_works),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, "[✓] PASS" if result else "[✗] FAIL"))
        except AssertionError as e:
            print(f"  [✗] FAIL: {name}: {e}")
            results.append((name, "[✗] FAIL"))
        except Exception as e:
            print(f"  [✗] ERROR in {name}: {e}")
            results.append((name, "[✗] ERROR"))

    # Summary
    print("\n" + "=" * 60)
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
