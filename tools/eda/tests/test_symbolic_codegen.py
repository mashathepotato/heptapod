#!/usr/bin/env python3
"""
# test_symbolic_codegen.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Tests for SymbolicFeynCalcCodeGenerator and ComputeSymbolicAmplitude.

Tests verify:
1. SymbolicFeynCalcCodeGenerator produces code without numerical mass assignments
2. ComputeSymbolicAmplitude tool returns correct output structure

Run with:
    python test_symbolic_codegen.py
"""

import json
import sys
import tempfile
import shutil
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.eda.feyncalc_codegen import (
    SymbolicFeynCalcCodeGenerator,
    FeynCalcCodeGenerator,
    ProcessType,
)
from tools.nda.simple_diagram import parse_diagram, Diagram
from tools.nda.symbolic_diagram import (
    parse_symbolic_diagram,
    _default_coupling_for_type,
)
from tools.nda.diagram_resolution import resolve_diagram


# ---------------------------------------------------------------------------
# Diagram factories
# ---------------------------------------------------------------------------

def _make_h_to_bb_numerical() -> Diagram:
    """Numerical H -> b bbar diagram."""
    return parse_diagram({
        "initial": [{"label": "H", "spin": 0, "mass": 125.0}],
        "final": [
            {"label": "b", "spin": "1/2", "mass": 4.18},
            {"label": "bbar", "spin": "1/2", "mass": 4.18},
        ],
        "vertices": [{"type": "scalar", "coupling": "y_b"}],
        "couplings": {"y_b": 0.024},
        "color_factor": 3.0,
    })


def _make_h_to_bb_resolved():
    """Resolved symbolic H -> bb."""
    sym = parse_symbolic_diagram({
        "initial": [{"label": "H"}],
        "final": [{"label": "b"}, {"label": "bbar"}],
        "vertices": [{"type": "yukawa", "coupling": "y_b"}],
    })
    return resolve_diagram(sym)


# ---------------------------------------------------------------------------
# SymbolicFeynCalcCodeGenerator
# ---------------------------------------------------------------------------

def test_symbolic_code_generator():
    """Test SymbolicFeynCalcCodeGenerator."""
    print("=" * 60)
    print("Testing SymbolicFeynCalcCodeGenerator")
    print("=" * 60)

    all_passed = True

    # no numerical masses
    diagram = _make_h_to_bb_numerical()
    gen = SymbolicFeynCalcCodeGenerator()
    result = gen.generate(diagram)

    ok = result.process_type == ProcessType.DECAY_1TO2 and result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: generates code with correct process type")

    ok = "= 125" not in result.code and "= 4.18" not in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: no numerical masses in code")

    ok = "symbolic" in result.code.lower() or "Masses" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: contains symbolic marker")

    # symbolic results only
    ok = (
        "SYMBOLIC_RESULT" in result.code
        and "LATEX_RESULT" in result.code
        and "NUMERICAL_RESULT" not in result.code
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: SYMBOLIC/LATEX markers, no NUMERICAL")

    # standard codegen still has numerics
    gen_std = FeynCalcCodeGenerator()
    result_std = gen_std.generate(diagram)
    ok = ("= 125" in result_std.code or "= 125.0" in result_std.code) and "NUMERICAL_RESULT" in result_std.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: standard codegen has numerical values")

    # amplitude structure preserved
    ok = (
        "FeynCalc" in result.code
        and "ampSq" in result.code
        and "width" in result.code
        and ("SpinorUBar" in result.code or "SpinorV" in result.code)
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: amplitude structure preserved")

    # resolved diagram
    diagram_res = _make_h_to_bb_resolved()
    gen2 = SymbolicFeynCalcCodeGenerator()
    result_res = gen2.generate(diagram_res)
    ok = (
        result_res.process_type == ProcessType.DECAY_1TO2
        and result_res.code
        and "NUMERICAL_RESULT" not in result_res.code
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: resolved diagram works")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Symbolic codegen conjugation
# ---------------------------------------------------------------------------

def test_symbolic_codegen_conjugation():
    """Test complex coupling conjugation in symbolic codegen."""
    print("=" * 60)
    print("Testing symbolic codegen conjugation")
    print("=" * 60)

    all_passed = True

    # numeric couplings: no conjugation rules
    diagram = _make_h_to_bb_numerical()
    gen = SymbolicFeynCalcCodeGenerator()
    result = gen.generate(diagram)
    ok = "-> Conjugate[" not in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: numeric couplings: no conjugation rules")

    # unresolved coupling: should add conjugation
    diagram = parse_diagram({
        "initial": [{"label": "H", "spin": 0, "mass": 125.0}],
        "final": [
            {"label": "b", "spin": "1/2", "mass": 4.18},
            {"label": "bbar", "spin": "1/2", "mass": 4.18},
        ],
        "vertices": [{"type": "scalar", "coupling": "y_b"}],
        "color_factor": 3.0,
    })
    gen = SymbolicFeynCalcCodeGenerator()
    result = gen.generate(diagram)
    ok = "y_b -> Conjugate[y_b]" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: unresolved coupling gets conjugation")

    # assume_real_couplings
    gen = SymbolicFeynCalcCodeGenerator(assume_real_couplings=True)
    result = gen.generate(diagram)
    ok = "-> Conjugate[" not in result.code and "ComplexConjugate[amp]" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: assume_real_couplings skips conjugation")

    print()
    return all_passed


# ---------------------------------------------------------------------------
# ComputeSymbolicAmplitude tool
# ---------------------------------------------------------------------------

def test_compute_symbolic_amplitude():
    """Test ComputeSymbolicAmplitude tool."""
    print("=" * 60)
    print("Testing ComputeSymbolicAmplitude tool")
    print("=" * 60)

    from tools.eda.compute_symbolic_amplitude_tool import ComputeSymbolicAmplitude
    all_passed = True

    # H -> bb
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "H", "spin": 0}],
                "final": [{"label": "b", "spin": "1/2"}, {"label": "bbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            base_directory=tmp_dir,
        )
        result_str = tool._run()
        result = json.loads(result_str)
        ok = (
            result["status"] == "ok"
            and result["process_type"] == "DECAY_1TO2"
            and "mode" not in result
            and "momentum_map" not in result
            and "script_path" in result
        )
        if ok:
            script_path = Path(result["script_path"])
            ok = script_path.exists()
            if ok:
                code = script_path.read_text()
                ok = "FeynCalc" in code and "NUMERICAL_RESULT" not in code
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: H -> bb")
    finally:
        shutil.rmtree(tmp_dir)

    # missing diagram
    tmp_dir = tempfile.mkdtemp()
    try:
        try:
            ComputeSymbolicAmplitude(diagram=None, base_directory=tmp_dir)
            ok = False
        except Exception:
            ok = True
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: missing diagram raises")
    finally:
        shutil.rmtree(tmp_dir)

    # always saves file
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "H", "spin": 0}],
                "final": [{"label": "b", "spin": "1/2"}, {"label": "bbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok" and "script_path" in result and Path(result["script_path"]).exists()
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: always saves file")
    finally:
        shutil.rmtree(tmp_dir)

    # custom script name
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "H", "spin": 0}],
                "final": [{"label": "b", "spin": "1/2"}, {"label": "bbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            script_name="test_symbolic_h_bb",
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok" and "test_symbolic_h_bb.wl" in result["script_path"]
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: custom script name")
    finally:
        shutil.rmtree(tmp_dir)

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Generic (non-SM) symbolic codegen
# ---------------------------------------------------------------------------

def test_generic_symbolic_codegen():
    """Test model-agnostic symbolic code generation with non-SM particles."""
    print("=" * 60)
    print("Testing generic symbolic codegen")
    print("=" * 60)

    from tools.eda.compute_symbolic_amplitude_tool import ComputeSymbolicAmplitude
    all_passed = True

    # generic fermion-scalar decay
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "S", "spin": 0}],
                "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y"}],
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok" and result["process_type"] == "DECAY_1TO2" and "mode" not in result
        if ok:
            code = Path(result["script_path"]).read_text()
            ok = "FeynCalc" in code
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: generic fermion-scalar decay")
    finally:
        shutil.rmtree(tmp_dir)

    # generic vector to fermions
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "V", "spin": 1}],
                "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
                "vertices": [{"type": "gauge-vector", "coupling": "g"}],
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok"
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: generic vector to fermions")
    finally:
        shutil.rmtree(tmp_dir)

    # missing spin returns error
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "F"}],
                "final": [{"label": "f"}, {"label": "S"}],
                "vertices": [{"type": "yukawa", "coupling": "y"}],
            },
            base_directory=tmp_dir,
        )
        result_str = tool._run()
        ok = "error" in result_str.lower() and "spin" in result_str.lower()
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: missing spin returns error")
    finally:
        shutil.rmtree(tmp_dir)

    # string mass does not crash
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "V", "spin": 1, "mass": "mV"}],
                "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
                "vertices": [{"type": "gauge-vector", "coupling": "g"}],
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok"
        if ok:
            code = Path(result["script_path"]).read_text()
            ok = "DoPolarizationSums" in code and "VirtualBoson" not in code
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: string mass does not crash")
    finally:
        shutil.rmtree(tmp_dir)

    # SM particles with spins still work
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "H", "spin": 0}],
                "final": [{"label": "b", "spin": "1/2"}, {"label": "bbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y_b"}],
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok" and result["process_type"] == "DECAY_1TO2"
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: SM particles with spins still work")
    finally:
        shutil.rmtree(tmp_dir)

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Chiral symbolic amplitude
# ---------------------------------------------------------------------------

def test_chiral_symbolic_amplitude():
    """Test chiral dict coupling through the full symbolic tool pipeline."""
    print("=" * 60)
    print("Testing chiral symbolic amplitude")
    print("=" * 60)

    from tools.eda.compute_symbolic_amplitude_tool import ComputeSymbolicAmplitude
    all_passed = True

    # V -> tau+ tau- with chiral dict coupling
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "V", "spin": 1}],
                "final": [
                    {"label": "tau+", "spin": "1/2"},
                    {"label": "tau-", "spin": "1/2"},
                ],
                "vertices": [{"type": "chiral", "coupling": {"gL": "gL", "gR": "gR"}}],
            },
            script_name="V_to_tautau_chiral_symbolic",
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok" and result["process_type"] == "DECAY_1TO2"
        if ok:
            code = Path(result["script_path"]).read_text()
            ok = (
                "GA[7]" in code
                and "GA[6]" in code
                and "gL -> Conjugate[gL]" in code
                and "gR -> Conjugate[gR]" in code
            )
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: chiral V -> tau+tau-")
    finally:
        shutil.rmtree(tmp_dir)

    # assume_real_couplings
    tmp_dir = tempfile.mkdtemp()
    try:
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "V", "spin": 1}],
                "final": [
                    {"label": "tau+", "spin": "1/2"},
                    {"label": "tau-", "spin": "1/2"},
                ],
                "vertices": [{"type": "chiral", "coupling": {"gL": "gL", "gR": "gR"}}],
            },
            assume_real_couplings=True,
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok"
        if ok:
            code = Path(result["script_path"]).read_text()
            ok = "-> Conjugate[" not in code and "ComplexConjugate[amp]" in code
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: chiral assume_real_couplings")
    finally:
        shutil.rmtree(tmp_dir)

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Bosonic symbolic codegen
# ---------------------------------------------------------------------------

def test_bosonic_symbolic_codegen():
    """Test bosonic vertex configurations (SSS, SSV, SVV, VVV)."""
    print("=" * 60)
    print("Testing bosonic symbolic codegen")
    print("=" * 60)

    from tools.eda.compute_symbolic_amplitude_tool import ComputeSymbolicAmplitude
    all_passed = True

    test_cases = [
        (
            "SSS scalar cubic",
            {
                "initial": [{"label": "S", "spin": 0}],
                "final": [{"label": "S1", "spin": 0}, {"label": "S2", "spin": 0}],
                "vertices": [{"type": "scalar-3pt", "coupling": "lam"}],
            },
            lambda r, c: r["process_type"] == "DECAY_1TO2" and "lam" in c and "width" in c,
        ),
        (
            "SSV scalar to scalar+vector",
            {
                "initial": [{"label": "S", "spin": 0}],
                "final": [{"label": "S1", "spin": 0}, {"label": "V", "spin": 1}],
                "vertices": [{"type": "scalar-3pt", "coupling": "g"}],
            },
            lambda r, c: "PolarizationVector" in c and "FVD" in c,
        ),
        (
            "SVV scalar to vectors",
            {
                "initial": [{"label": "S", "spin": 0}],
                "final": [{"label": "V1", "spin": 1}, {"label": "V2", "spin": 1}],
                "vertices": [{"type": "scalar-3pt", "coupling": "g"}],
            },
            lambda r, c: "PolarizationVector" in c and "MTD" in c,
        ),
        (
            "VVV triple gauge",
            {
                "initial": [{"label": "V0", "spin": 1}],
                "final": [{"label": "V1", "spin": 1}, {"label": "V2", "spin": 1}],
                "vertices": [{"type": "scalar-3pt", "coupling": "g"}],
            },
            lambda r, c: "PolarizationVector" in c and "FVD" in c and "MTD" in c,
        ),
        (
            "SSV vector parent",
            {
                "initial": [{"label": "V", "spin": 1}],
                "final": [{"label": "S1", "spin": 0}, {"label": "S2", "spin": 0}],
                "vertices": [{"type": "scalar-3pt", "coupling": "g"}],
            },
            lambda r, c: "PolarizationVector" in c,
        ),
    ]

    for label, diagram_dict, check_fn in test_cases:
        tmp_dir = tempfile.mkdtemp()
        try:
            tool = ComputeSymbolicAmplitude(diagram=diagram_dict, base_directory=tmp_dir)
            result = json.loads(tool._run())
            ok = result["status"] == "ok"
            if ok:
                code = Path(result["script_path"]).read_text()
                ok = check_fn(result, code)
            if not ok:
                all_passed = False
            print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: {label}")
        finally:
            shutil.rmtree(tmp_dir)

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Simplifications parameter
# ---------------------------------------------------------------------------

def test_simplifications_parameter():
    """Test simplifications parameter on SymbolicFeynCalcCodeGenerator."""
    print("=" * 60)
    print("Testing simplifications parameter")
    print("=" * 60)

    all_passed = True
    diagram = _make_h_to_bb_numerical()

    # substitutions
    gen = SymbolicFeynCalcCodeGenerator(
        simplifications={"substitutions": {"mfbar": "mf"}}
    )
    result = gen.generate(diagram)
    ok = (
        "mfbar -> mf" in result.code
        and "widthSimplified" in result.code
        and "SYMBOLIC_RESULT[width_simplified]" in result.code
        and "LATEX_RESULT[width_simplified]" in result.code
    )
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: substitutions")

    # limit
    gen = SymbolicFeynCalcCodeGenerator(
        simplifications={"limit": {"var": "mf", "point": "0"}}
    )
    result = gen.generate(diagram)
    ok = "Limit[widthSimplified, mf -> 0]" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: limit")

    # series
    gen = SymbolicFeynCalcCodeGenerator(
        simplifications={"series": {"var": "eps", "point": "0", "order": 2}}
    )
    result = gen.generate(diagram)
    ok = "Normal[Series[widthSimplified, {eps, 0, 2}]]" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: series")

    # assumptions with simplify
    gen = SymbolicFeynCalcCodeGenerator(
        simplifications={
            "assumptions": ["M > 0", "mf > 0"],
            "simplify": "FullSimplify",
        }
    )
    result = gen.generate(diagram)
    ok = "Assuming[{M > 0, mf > 0}, FullSimplify[widthSimplified]]" in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: assumptions with FullSimplify")

    # no simplifications = no extra output
    gen = SymbolicFeynCalcCodeGenerator()
    result = gen.generate(diagram)
    ok = "width_simplified" not in result.code
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: no simplifications -> no _simplified markers")

    # simplifications via tool
    tmp_dir = tempfile.mkdtemp()
    try:
        from tools.eda.compute_symbolic_amplitude_tool import ComputeSymbolicAmplitude
        tool = ComputeSymbolicAmplitude(
            diagram={
                "initial": [{"label": "S", "spin": 0}],
                "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
                "vertices": [{"type": "yukawa", "coupling": "y"}],
            },
            simplifications={
                "substitutions": {"mfbar": "mf"},
                "simplify": "Simplify",
            },
            base_directory=tmp_dir,
        )
        result = json.loads(tool._run())
        ok = result["status"] == "ok"
        if ok:
            code = Path(result["script_path"]).read_text()
            ok = "mfbar -> mf" in code and "width_simplified" in code
        if not ok:
            all_passed = False
        print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: simplifications via tool")
    finally:
        shutil.rmtree(tmp_dir)

    print()
    return all_passed


# ---------------------------------------------------------------------------
# Default coupling
# ---------------------------------------------------------------------------

def test_default_coupling():
    """Test automatic coupling generation when coupling is omitted."""
    print("=" * 60)
    print("Testing default coupling")
    print("=" * 60)

    all_passed = True

    # chiral auto coupling
    sym = parse_symbolic_diagram({
        "initial": [{"label": "S", "spin": 0}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "yukawa-chiral"}],
    })
    v = sym.vertices[0]
    ok = isinstance(v.coupling, dict) and v.coupling == {"gL": "gL", "gR": "gR"}
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: yukawa-chiral auto coupling")

    # scalar auto coupling
    sym = parse_symbolic_diagram({
        "initial": [{"label": "S", "spin": 0}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "yukawa"}],
    })
    ok = sym.vertices[0].coupling == "g"
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: yukawa auto coupling")

    # VA auto coupling
    sym = parse_symbolic_diagram({
        "initial": [{"label": "V", "spin": 1}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "vector-axial"}],
    })
    v = sym.vertices[0]
    ok = isinstance(v.coupling, dict) and v.coupling == {"gV": "gV", "gA": "gA"}
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: vector-axial auto coupling")

    # explicit not overridden
    sym = parse_symbolic_diagram({
        "initial": [{"label": "S", "spin": 0}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "yukawa-chiral", "coupling": "y"}],
    })
    ok = sym.vertices[0].coupling == "y"
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: explicit coupling not overridden")

    # tensor auto coupling
    sym = parse_symbolic_diagram({
        "initial": [{"label": "V", "spin": 1}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "tensor"}],
    })
    ok = sym.vertices[0].coupling == "g"
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: tensor auto coupling")

    # scalar-va auto coupling
    sym = parse_symbolic_diagram({
        "initial": [{"label": "S", "spin": 0}],
        "final": [{"label": "f", "spin": "1/2"}, {"label": "fbar", "spin": "1/2"}],
        "vertices": [{"type": "scalar-va"}],
    })
    v = sym.vertices[0]
    ok = isinstance(v.coupling, dict) and v.coupling == {"gS": "gS", "gP": "gP"}
    if not ok:
        all_passed = False
    print(f"  {'[✓] PASS' if ok else '[✗] FAIL'}: scalar-va auto coupling")

    # _default_coupling_for_type function
    checks = [
        (_default_coupling_for_type("yukawa"), "g"),
        (_default_coupling_for_type("scalar"), "g"),
        (_default_coupling_for_type("chiral"), {"gL": "gL", "gR": "gR"}),
        (_default_coupling_for_type("yukawa-chiral"), {"gL": "gL", "gR": "gR"}),
        (_default_coupling_for_type("vector-axial"), {"gV": "gV", "gA": "gA"}),
        (_default_coupling_for_type("va"), {"gV": "gV", "gA": "gA"}),
        (_default_coupling_for_type("scalar-va"), {"gS": "gS", "gP": "gP"}),
        (_default_coupling_for_type("axial-vector"), "gA"),
        (_default_coupling_for_type("tensor"), "g"),
        (_default_coupling_for_type("dipole"), "g"),
        (_default_coupling_for_type("tensor-chiral"), {"gL": "gL", "gR": "gR"}),
    ]
    dc_ok = True
    for actual, expected in checks:
        if actual != expected:
            dc_ok = False
            break
    if not dc_ok:
        all_passed = False
    print(f"  {'[✓] PASS' if dc_ok else '[✗] FAIL'}: _default_coupling_for_type")

    print()
    return all_passed


# ==================== Runner ==================== #

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Symbolic Codegen Tests")
    print("=" * 60 + "\n")

    tests = [
        ("SymbolicFeynCalcCodeGenerator", test_symbolic_code_generator),
        ("Symbolic codegen conjugation", test_symbolic_codegen_conjugation),
        ("ComputeSymbolicAmplitude tool", test_compute_symbolic_amplitude),
        ("Generic symbolic codegen", test_generic_symbolic_codegen),
        ("Chiral symbolic amplitude", test_chiral_symbolic_amplitude),
        ("Bosonic symbolic codegen", test_bosonic_symbolic_codegen),
        ("Simplifications parameter", test_simplifications_parameter),
        ("Default coupling", test_default_coupling),
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
