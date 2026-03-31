"""
# compute_symbolic_amplitude_tool.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

ComputeSymbolicAmplitude — generates FeynCalc code with mass/coupling
*symbols* instead of hardcoded numerical values.

Given a SymbolicDiagram specification, this tool resolves just enough
structure (spins, topology) to generate the amplitude, but keeps all
masses and couplings as Mathematica symbols. The generated code cannot
be numerically evaluated as-is — the agent can later call RunWolframScript
with numerical substitutions if needed.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .feyncalc_codegen import SymbolicFeynCalcCodeGenerator, ProcessType
from tools.nda.symbolic_diagram import parse_symbolic_diagram, build_diagram_from_symbolic
from tools.logging.findings import append_finding


class ComputeSymbolicAmplitude(BaseTool):
    """
    Generate FeynCalc code with symbolic masses and couplings.

    Takes a SymbolicDiagram (particle labels + vertex types) and produces
    a complete FeynCalc Mathematica script where masses and couplings are
    left as Mathematica symbols (e.g., mH, mb, yb) instead of numbers.

    This is useful for deriving analytic expressions for decay widths or
    cross sections. The generated script can be later executed with
    RunWolframScript after manually substituting numerical values.

    Input:
        diagram: SymbolicDiagram dict (labels + vertex types + optional coupling)
        script_name: Optional name for saved .wl file

    Output:
        {
            "status": "ok",
            "process_type": "DECAY_1TO2",
            "script_path": "/path/to/script.wl",
            "momentum_map": {...},
            "mode": "symbolic"
        }

    Vertex Reference (``coupling`` is optional — defaults shown below):

    SFF (Scalar/Pseudoscalar -> Fermion Pair):
      type                  | aliases                       | default coupling         | FeynCalc structure
      "yukawa" / "scalar"   |                               | "g"                      | I (g)
      "pseudoscalar"        |                               | "g"                      | I (g) GA[5]
      "chiral"              | "yukawa-chiral","scalar-chiral"| {"gL":"gL","gR":"gR"}   | I (gL GA[7] + gR GA[6])
      "scalar-va"           |                               | {"gS":"gS","gP":"gP"}   | I (gS + gP GA[5])

    VFF (Vector -> Fermion Pair):
      type                  | aliases                       | default coupling         | FeynCalc structure
      "vector"              | "gauge-vector"                | "g"                      | I (g) GAD[mu]
      "axial-vector"        |                               | "gA"                     | I (gA) GAD[mu].GA[5]
      "left-handed"         |                               | "g"                      | I (g) GAD[mu].GA[7]
      "right-handed"        |                               | "g"                      | I (g) GAD[mu].GA[6]
      "chiral"              | "vector-chiral"               | {"gL":"gL","gR":"gR"}   | I GAD[mu].(gL GA[7]+gR GA[6])
      "vector-axial" / "va" |                               | {"gV":"gV","gA":"gA"}   | I GAD[mu].(gV - gA GA[5])
      "tensor" / "dipole"   |                               | "g"                      | I (g) sigma^{mu nu} k_nu
      "tensor-chiral"       | "dipole-chiral"               | {"gL":"gL","gR":"gR"}   | I (gL PL+gR PR).sigma^{mu nu} k_nu

    Bosonic (dispatch by spin, not type name — any type string works):
      spin config           | example                              | FeynCalc structure
      [0,0,0] SSS           | S -> S1 S2                           | I g
      [0,0,1] SSV           | S -> S' V  or  V -> S1 S2            | I g ε·(p1-p2)
      [0,1,1] SVV           | S -> V1 V2                           | I g ε1·ε2
      [1,1,1] VVV           | V -> V1 V2                           | triple gauge vertex

    Examples:
        # Minimal: coupling auto-generated from type
        {"type": "chiral"}  ->  coupling defaults to {"gL": "gL", "gR": "gR"}

        # Explicit coupling overrides the default
        {"type": "chiral", "coupling": "y"}  ->  uses yL, yR

        # V-A vertex
        {"type": "vector-axial", "coupling": {"gV": "gV_e", "gA": "gA_e"}}

    The generated script is always saved to a .wl file. To execute it
    (after adding numerical substitutions), pass the script_path to
    RunWolframScript.
    """

    # ======================== Runtime fields ======================== #
    diagram: Dict[str, Any] = RuntimeField(
        description=(
            "Symbolic diagram specification dict with keys: 'initial', "
            "'final', 'vertices', and optionally 'propagators', 'topology'. "
            "Particle labels required; masses and coupling values are NOT needed."
        )
    )
    script_name: Optional[str] = RuntimeField(
        default=None,
        description="Name for saved .wl script (without extension)",
    )
    sqrt_s: Optional[float] = RuntimeField(
        default=None,
        description="Centre-of-mass energy in GeV (required for 2->2 scattering)",
    )
    assume_real_couplings: bool = RuntimeField(
        default=False,
        description="If True, treat all couplings as real (skip Conjugate in |M|²)",
    )
    simplifications: Optional[Dict[str, Any]] = RuntimeField(
        default=None,
        description=(
            "Post-computation simplifications applied in-script after the width/sigma. "
            "Keys: 'substitutions' (dict), 'limit' ({var, point}), 'series' "
            "({var, point, order}), 'assumptions' (list), 'simplify' (str). "
            "Result saved as SYMBOLIC_RESULT[width_simplified]."
        ),
    )
    # ================================================================ #

    # ========================= State fields ========================= #
    base_directory: str = StateField(
        description="Working directory for script output"
    )
    # ================================================================ #

    def _run(self) -> str:
        if not self.diagram:
            return self.format_error(
                error="Missing Parameter",
                reason="diagram is required",
                suggestion="Provide a symbolic diagram specification dict",
            )

        # Parse as symbolic diagram
        try:
            sym = parse_symbolic_diagram(self.diagram)
        except Exception as e:
            return self.format_error(
                error="Diagram Parse Error",
                reason=str(e),
            )

        is_valid, warnings = sym.validate()
        if not is_valid:
            return self.format_error(
                error="Diagram Validation Failed",
                reason="; ".join(warnings),
            )

        # Build a Diagram directly from the SymbolicDiagram (no SM lookup needed).
        # Requires spins on all particles — masses are left symbolic.
        try:
            resolved = build_diagram_from_symbolic(sym)
        except Exception as e:
            return self.format_error(
                error="Diagram Build Error",
                reason=str(e),
                suggestion=(
                    "Spins must be provided on all particles and propagators "
                    "for symbolic code generation. Add 'spin' to each particle dict."
                ),
            )

        # Generate code with symbolic masses
        generator = SymbolicFeynCalcCodeGenerator(
            assume_real_couplings=self.assume_real_couplings,
            simplifications=self.simplifications,
        )
        gen_result = generator.generate(resolved, sqrt_s=self.sqrt_s)

        if gen_result.process_type == ProcessType.UNSUPPORTED:
            output = {
                "status": "unsupported",
                "process_type": "UNSUPPORTED",
                "warnings": gen_result.warnings,
                "suggestion": (
                    "This topology is not yet supported by automatic code generation. "
                    "Use RunWolframScript with manually written FeynCalc code."
                ),
            }
            return json.dumps(output, indent=2)

        if not gen_result.code:
            output = {
                "status": "error",
                "process_type": gen_result.process_type.name,
                "warnings": gen_result.warnings,
            }
            return json.dumps(output, indent=2)

        # Always save the .wl file — this is the primary artifact
        if self.script_name:
            name = self.script_name
            if not name.endswith(".wl"):
                name += ".wl"
        else:
            # Auto-generate from process labels
            labels = [p.label for p in sym.initial] + [p.label for p in sym.final]
            safe = "_".join(l.replace("+", "p").replace("-", "m") for l in labels)
            name = f"symbolic_{safe}.wl"

        scripts_dir = Path(self.base_directory) / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = str(scripts_dir / name)
        with open(script_path, "w") as f:
            f.write(gen_result.code)

        output: Dict[str, Any] = {
            "status": "ok",
            "process_type": gen_result.process_type.name,
            "script_path": script_path,
        }
        if gen_result.warnings:
            output["warnings"] = gen_result.warnings
        if gen_result.channel:
            output["channel"] = gen_result.channel.name

        # Append findings (best-effort)
        try:
            labels = [p.label for p in sym.initial] + [p.label for p in sym.final]
            process_str = " → ".join([
                " ".join(p.label for p in sym.initial),
                " ".join(p.label for p in sym.final),
            ])
            vertex_info = ", ".join(
                f"{v.type}" for v in sym.vertices
            )
            entries = [
                f"Process: {process_str} ({gen_result.process_type.name})",
                f"Vertices: {vertex_info}",
                f"Script: {script_path}",
            ]
            append_finding(self.base_directory, f"Symbolic: {process_str}", entries)
        except Exception:
            pass

        return json.dumps(output, indent=2)
