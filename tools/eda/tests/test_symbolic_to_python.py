#!/usr/bin/env python3
"""
# test_symbolic_to_python.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for symbolic_to_python: Mathematica -> Python callable conversion.

Run with:
    python test_symbolic_to_python.py
"""

import math
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.eda.symbolic_to_python import (
    mathematica_to_sympy,
    mathematica_to_callable,
    mathematica_to_python_source,
    extract_variables,
)


# ---------------------------------------------------------------------------
# mathematica_to_sympy
# ---------------------------------------------------------------------------

def test_mathematica_to_sympy():
    """Test Mathematica InputForm -> sympy parsing."""
    print("=" * 60)
    print("Testing mathematica_to_sympy")
    print("=" * 60)

    all_passed = True

    # simple product
    expr = mathematica_to_sympy("g^2*M/(48*Pi)")
    ok = str(expr) == "M*g**2/(48*pi)"
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: simple product")

    # sqrt
    expr = mathematica_to_sympy("Sqrt[MH^2 - 4*mb^2]")
    ok = "sqrt" in str(expr)
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: sqrt")

    # rational exponent
    expr = mathematica_to_sympy("(1 - 4*mb^2/MH^2)^(3/2)")
    ok = expr is not None
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: rational exponent")

    # kallen lambda
    expr = mathematica_to_sympy(
        "Sqrt[(MH^2 - (m1 + m2)^2)*(MH^2 - (m1 - m2)^2)]/(2*MH)"
    )
    syms = {str(s) for s in expr.free_symbols}
    ok = syms == {"MH", "m1", "m2"}
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: kallen lambda variables")

    # empty raises
    try:
        mathematica_to_sympy("")
        ok = False
    except ValueError as e:
        ok = "Empty expression" in str(e)
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: empty raises ValueError")

    # whitespace only raises
    try:
        mathematica_to_sympy("   ")
        ok = False
    except ValueError as e:
        ok = "Empty expression" in str(e)
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: whitespace only raises ValueError")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# mathematica_to_callable
# ---------------------------------------------------------------------------

def test_mathematica_to_callable():
    """Test conversion to Python callable + numerical evaluation."""
    print("=" * 60)
    print("Testing mathematica_to_callable")
    print("=" * 60)

    all_passed = True

    # H -> bb width
    fn = mathematica_to_callable(
        "(3*yb^2*Sqrt[MH^2 - 4*mb^2]*(MH^2 - 4*mb^2))/(16*Pi*MH^2)",
        ["MH", "mb", "yb"],
    )
    width = fn(125.0, 4.18, 4.18 / 246.0)
    ok = 0.001 < width < 0.004
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: H->bb width = {width:.6f} GeV")

    # vector decay width
    fn = mathematica_to_callable("g^2*M/(48*Pi)", ["M", "g"])
    width = fn(3000.0, 0.1)
    expected = 0.1**2 * 3000 / (48 * math.pi)
    ok = abs(width - expected) / expected < 1e-10
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: vector decay width")

    # chiral width
    fn = mathematica_to_callable(
        "(gL^2 + gR^2)*M/(48*Pi)", ["M", "gL", "gR"]
    )
    width = fn(91.19, 0.27, 0.23)
    expected = (0.27**2 + 0.23**2) * 91.19 / (48 * math.pi)
    ok = abs(width - expected) / expected < 1e-10
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: chiral width")

    # mandelstam cross section
    fn = mathematica_to_callable(
        "e^4*(t^2 + u^2)/(2*s^2)", ["s", "t", "u", "e"]
    )
    val = fn(100.0, -25.0, -75.0, 0.303)
    ok = val > 0
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: mandelstam cross section > 0")

    # missing variable raises
    try:
        mathematica_to_callable("g^2*M/(48*Pi)", ["M", "g", "unknown"])
        ok = False
    except ValueError as e:
        ok = "not found in expression" in str(e)
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: missing variable raises ValueError")

    # parameter scan
    fn = mathematica_to_callable("g^2*M/(48*Pi)", ["M", "g"])
    masses = [100, 500, 1000, 3000, 10000]
    widths = [fn(m, 0.1) for m in masses]
    scan_ok = True
    for i in range(1, len(masses)):
        ratio = widths[i] / widths[0]
        expected_ratio = masses[i] / masses[0]
        if abs(ratio - expected_ratio) / expected_ratio >= 1e-10:
            scan_ok = False
            break
    if not scan_ok:
        all_passed = False
    print(f"  {'[✓] PASS' if scan_ok else '[✗] FAIL'}: parameter scan (width scales linearly with M)")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# mathematica_to_python_source
# ---------------------------------------------------------------------------

def test_mathematica_to_python_source():
    """Test Python source code generation."""
    print("=" * 60)
    print("Testing mathematica_to_python_source")
    print("=" * 60)

    all_passed = True

    # basic source
    src = mathematica_to_python_source("g^2*M/(48*Pi)", ["M", "g"], "width")
    ok = "def width(M, g):" in src and "import math" in src
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: basic source structure")

    # executable
    namespace = {}
    exec(src, namespace)
    result = namespace["width"](3000.0, 0.1)
    expected = 0.1**2 * 3000 / (48 * math.pi)
    ok = abs(result - expected) / expected < 1e-10
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: generated source is executable and correct")

    # custom function name
    src = mathematica_to_python_source(
        "yb^2*MH/(16*Pi)", ["MH", "yb"], "gamma_Hbb"
    )
    ok = "def gamma_Hbb(MH, yb):" in src
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: custom function name")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# extract_variables
# ---------------------------------------------------------------------------

def test_extract_variables():
    """Test automatic variable extraction."""
    print("=" * 60)
    print("Testing extract_variables")
    print("=" * 60)

    all_passed = True

    ok = extract_variables("g^2*M/(48*Pi)") == ["M", "g"]
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: simple")

    vars_list = extract_variables(
        "(3*yb^2*Sqrt[MH^2 - 4*mb^2]*(MH^2 - 4*mb^2))/(16*Pi*MH^2)"
    )
    ok = vars_list == ["MH", "mb", "yb"]
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: H->bb")

    ok = extract_variables("(gL^2 + gR^2)*M/(48*Pi)") == ["M", "gL", "gR"]
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: chiral")

    ok = extract_variables("e^4*(t^2 + u^2)/(2*s^2)") == ["e", "s", "t", "u"]
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: mandelstam")

    print()
    return all_passed


# ==================== Runner ==================== #

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("symbolic_to_python Tests")
    print("=" * 60 + "\n")

    tests = [
        ("mathematica_to_sympy", test_mathematica_to_sympy),
        ("mathematica_to_callable", test_mathematica_to_callable),
        ("mathematica_to_python_source", test_mathematica_to_python_source),
        ("extract_variables", test_extract_variables),
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
