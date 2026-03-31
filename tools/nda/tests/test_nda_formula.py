#!/usr/bin/env python3
"""
# test_nda_formula.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for EstimateDecayWidthFormulaNDATool -- verifies symbolic NDA formula
generation without numerical width computation.

Run with:
    python test_nda_formula.py
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

from tools.nda.nda_formula_tool import EstimateDecayWidthFormulaNDATool


def test_h_to_bb():
    """H -> bb formula: Yukawa 2-body decay."""
    print("=" * 60)
    print("Testing H -> bb formula")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "initial": [{"label": "H"}],
                "final": [{"label": "b"}, {"label": "bbar"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())

        assert result["status"] == "ok"
        assert "formula" in result
        # Formula should contain the coupling name
        assert "y_b" in result["formula"]
        # Should be a 2-body decay formula with 16pi
        assert r"16\pi" in result["formula"]
        # Should NOT contain any numerical width
        assert "width_gev" not in result

        # Check scaling
        assert result["scaling"]["coupling_power"] == 2
        assert result["scaling"]["phase_space_power"] == 0  # 2*2-4 = 0
        assert result["scaling"]["me_mass_power"] == 2  # single vertex, dim-4

        print("  [✓] PASS: H -> bb formula")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_muon_decay():
    """mu -> e nu nu with W propagator: 3-body with propagator suppression."""
    print("=" * 60)
    print("Testing muon decay formula")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "topology": "tree_3body",
                "initial": [{"label": "mu-"}],
                "final": [
                    {"label": "e-"},
                    {"label": "nu_ebar"},
                    {"label": "nu_mu"},
                ],
                "vertices": [
                    {"type": "gauge-vector", "coupling": "g_W"},
                    {"type": "gauge-vector", "coupling": "g_W"},
                ],
                "propagators": [{"label": "W-"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())

        assert result["status"] == "ok"
        # Formula should have g_W^4 (two vertices)
        assert "g_W" in result["formula"]
        assert result["scaling"]["coupling_power"] == 4
        # Should have propagator suppression
        assert "propagator_suppression" in result["components"]
        # 3-body -> 64pi^3
        assert r"64\pi^3" in result["formula"]
        # Should have M_W in denominator
        assert "M_{W-}" in result["formula"]

        print("  [✓] PASS: Muon decay formula")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_2body_no_propagator():
    """Z -> ee: 2-body gauge vertex."""
    print("=" * 60)
    print("Testing 2-body no propagator")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "initial": [{"label": "Z"}],
                "final": [{"label": "e-"}, {"label": "e+"}],
                "vertices": [{"type": "gauge-vector", "coupling": "e"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())

        assert result["status"] == "ok"
        assert "e" in result["formula"]
        assert result["diagram"]["n_body"] == 2
        assert result["diagram"]["n_propagators"] == 0

        print("  [✓] PASS: 2-body no propagator")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_process_label():
    """Process label is included in output when provided."""
    print("=" * 60)
    print("Testing process label")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "initial": [{"label": "H"}],
                "final": [{"label": "b"}, {"label": "bbar"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            process_label="H \u2192 bb\u0304",
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["process_label"] == "H \u2192 bb\u0304"

        print("  [✓] PASS: Process label")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_missing_diagram():
    """Missing diagram raises validation error at instantiation."""
    print("=" * 60)
    print("Testing missing diagram")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        try:
            EstimateDecayWidthFormulaNDATool(
                diagram=None,
                base_directory=base_dir,
            )
            print("  [✗] FAIL: Expected exception for None diagram")
            return False
        except Exception:
            print("  [✓] PASS: Missing diagram raises exception")
            return True
    finally:
        shutil.rmtree(base_dir)


def test_numerical_coupling_rejected():
    """Numerical coupling in symbolic diagram should be rejected."""
    print("=" * 60)
    print("Testing numerical coupling rejected")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "initial": [{"label": "H"}],
                "final": [{"label": "b"}, {"label": "bbar"}],
                "vertices": [{"type": "yukawa", "coupling": 0.024}],
            },
            base_directory=base_dir,
        )
        result_str = tool._run()
        # Should fail because coupling must be a string -- may be JSON or plain text error
        assert "error" in result_str.lower() or "string name" in result_str.lower()

        print("  [✓] PASS: Numerical coupling rejected")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_components_structure():
    """Components dict has all expected keys."""
    print("=" * 60)
    print("Testing components structure")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "initial": [{"label": "H"}],
                "final": [{"label": "b"}, {"label": "bbar"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert "components" in result
        comp = result["components"]
        # All 6 mandatory keys must be present
        assert "prefactor" in comp
        assert "phase_space" in comp
        assert "matrix_element" in comp
        assert "spin_averaging" in comp
        assert "color_factor" in comp
        assert "symmetry_factor" in comp
        # H is spin-0 -> spin averaging = 1
        assert "= 1" in comp["spin_averaging"]
        # No identical final states -> S = 1
        assert comp["symmetry_factor"] == "S = 1"
        # Default color factor
        assert comp["color_factor"] == "N_c = 1"
        # Prefactor always 1/(2M)
        assert "2M" in comp["prefactor"]

        print("  [✓] PASS: Components structure")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_explicit_regime_heavy():
    """Explicit regime='heavy' on generic propagator produces suppression."""
    print("=" * 60)
    print("Testing explicit regime heavy")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "topology": "tree_3body",
                "initial": [{"label": "F"}],
                "final": [
                    {"label": "f1"},
                    {"label": "f2"},
                    {"label": "f3"},
                ],
                "vertices": [
                    {"type": "gauge-vector", "coupling": "g"},
                    {"type": "gauge-vector", "coupling": "g"},
                ],
                "propagators": [{"label": "X", "regime": "heavy"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        # Should have propagator suppression with M_X
        assert "propagator_suppression" in result["components"]
        assert "M_{X}" in result["formula"]

        print("  [✓] PASS: Explicit regime heavy")
        return True
    finally:
        shutil.rmtree(base_dir)


def test_explicit_regime_light():
    """Explicit regime='light' on generic propagator: no M_X in denominator."""
    print("=" * 60)
    print("Testing explicit regime light")
    print("=" * 60)

    base_dir = tempfile.mkdtemp()
    try:
        tool = EstimateDecayWidthFormulaNDATool(
            diagram={
                "topology": "tree_3body",
                "initial": [{"label": "F"}],
                "final": [
                    {"label": "f1"},
                    {"label": "f2"},
                    {"label": "f3"},
                ],
                "vertices": [
                    {"type": "gauge-vector", "coupling": "g"},
                    {"type": "gauge-vector", "coupling": "g"},
                ],
                "propagators": [{"label": "X", "regime": "light"}],
            },
            base_directory=base_dir,
        )
        result = json.loads(tool._run())
        assert result["status"] == "ok"
        # Should NOT have M_X in the formula -- light propagator adds to mass power
        assert "M_{X}" not in result["formula"]

        print("  [✓] PASS: Explicit regime light")
        return True
    finally:
        shutil.rmtree(base_dir)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NDA Formula Tool Tests")
    print("=" * 60 + "\n")

    tests = [
        ("H -> bb formula", test_h_to_bb),
        ("Muon decay formula", test_muon_decay),
        ("2-body no propagator", test_2body_no_propagator),
        ("Process label", test_process_label),
        ("Missing diagram", test_missing_diagram),
        ("Numerical coupling rejected", test_numerical_coupling_rejected),
        ("Components structure", test_components_structure),
        ("Explicit regime heavy", test_explicit_regime_heavy),
        ("Explicit regime light", test_explicit_regime_light),
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
