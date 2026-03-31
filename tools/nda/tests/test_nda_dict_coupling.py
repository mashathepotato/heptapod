#!/usr/bin/env python3
"""
# test_nda_dict_coupling.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for NDA dict coupling support (V-A, chiral, etc.).

Run with:
    python test_nda_dict_coupling.py
"""

import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

# Path setup
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.nda.nda_tool import EstimateDecayWidthNDATool


def _make_diagram(coupling, couplings=None):
    """Z -> e- e+ diagram with given coupling."""
    diagram = {
        "initial": [{"label": "Z", "spin": 1, "mass": 91.2}],
        "final": [
            {"label": "e-", "spin": "1/2", "mass": 0.000511},
            {"label": "e+", "spin": "1/2", "mass": 0.000511},
        ],
        "vertices": [{"type": "gauge-vector", "coupling": coupling}],
    }
    if couplings:
        diagram["couplings"] = couplings
    return diagram


def test_numeric_dict():
    """Dict with numeric values: g_eff = sqrt(gV^2 + gA^2)."""
    print("=" * 60)
    print("Testing numeric dict coupling")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=_make_diagram(coupling={"gV": 0.3, "gA": 0.4}),
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        assert result["width_gev"] > 0

        print("  [✓] PASS: Numeric dict coupling")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_string_ref_dict():
    """Dict with string refs resolved from couplings dict."""
    print("=" * 60)
    print("Testing string ref dict coupling")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=_make_diagram(
                coupling={"gV": "gV", "gA": "gA"},
                couplings={"gV": 0.3, "gA": 0.4},
            ),
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        assert result["width_gev"] > 0

        print("  [✓] PASS: String ref dict coupling")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_mixed_dict():
    """Dict with mix of numeric and string ref values."""
    print("=" * 60)
    print("Testing mixed dict coupling")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=_make_diagram(
                coupling={"gV": 0.3, "gA": "gA"},
                couplings={"gA": 0.4},
            ),
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        assert result["width_gev"] > 0

        print("  [✓] PASS: Mixed dict coupling")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_missing_ref_error():
    """Dict with unresolvable string ref raises error."""
    print("=" * 60)
    print("Testing missing ref error")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=_make_diagram(
                coupling={"gV": "missing_ref", "gA": 0.4},
                couplings={},
            ),
            base_directory=base_dir,
        )
        result_str = tool._run()
        # format_error returns plain text, not JSON
        assert "error" in result_str.lower() or "missing_ref" in result_str

        print("  [✓] PASS: Missing ref error")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_chiral_dict():
    """Chiral coupling dict: g_eff = sqrt(gL^2 + gR^2)."""
    print("=" * 60)
    print("Testing chiral dict coupling")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthNDATool(
            diagram=_make_diagram(coupling={"gL": 0.6, "gR": 0.8}),
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        assert result["width_gev"] > 0

        print("  [✓] PASS: Chiral dict coupling")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_numeric_vs_dict_consistency():
    """Dict {g: value} should give same result as scalar value."""
    print("=" * 60)
    print("Testing numeric vs dict consistency")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        # Single-component dict -- g_eff = sqrt(0.5^2) = 0.5
        tool_dict = EstimateDecayWidthNDATool(
            diagram=_make_diagram(coupling={"g": 0.5}),
            base_directory=base_dir,
        )
        result_dict = json.loads(tool_dict._run())

        # Scalar coupling = 0.5
        tool_scalar = EstimateDecayWidthNDATool(
            diagram={
                "initial": [{"label": "Z", "spin": 1, "mass": 91.2}],
                "final": [
                    {"label": "e-", "spin": "1/2", "mass": 0.000511},
                    {"label": "e+", "spin": "1/2", "mass": 0.000511},
                ],
                "vertices": [{"type": "gauge-vector", "coupling": 0.5}],
            },
            base_directory=base_dir,
        )
        result_scalar = json.loads(tool_scalar._run())

        assert result_dict["status"] == "ok"
        assert result_scalar["status"] == "ok"
        assert abs(result_dict["width_gev"] - result_scalar["width_gev"]) < 1e-10

        print("  [✓] PASS: Numeric vs dict consistency")
        return True
    finally:
        shutil.rmtree(base_dir)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NDA Dict Coupling Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Numeric dict", test_numeric_dict),
        ("String ref dict", test_string_ref_dict),
        ("Mixed dict", test_mixed_dict),
        ("Missing ref error", test_missing_ref_error),
        ("Chiral dict", test_chiral_dict),
        ("Numeric vs dict consistency", test_numeric_vs_dict_consistency),
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
