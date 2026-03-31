"""
# nda_formula_tool.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

EstimateDecayWidthFormulaNDA — returns the NDA scaling formula (LaTeX) for a
decay process without computing a numerical width.

Takes a SymbolicDiagram (labels + topology + vertex types) and returns
the dimensional analysis formula. No numerical masses or coupling values
are needed.
"""

import json
import math
import os
from collections import Counter
from typing import Optional, Dict, Any

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .symbolic_diagram import parse_symbolic_diagram, SymbolicDiagram
from .particle_database import get_particle_data

SCHEMA_VERSION = "nda-formula-2.0"

# Operator dimension for each vertex type
OPERATOR_DIM_MAP = {
    "yukawa": 4,
    "gauge-vector": 4,
    "gauge-axial": 4,
    "scalar-3pt": 4,
    "scalar-4pt": 4,
    "dim5-weinberg": 5,
    "dim6-4fermion": 6,
    "dim8-4fermion": 8,
    "custom": 4,
}


class EstimateDecayWidthFormulaNDATool(BaseTool):
    """
    Returns the NDA scaling formula for a decay process without computing
    a numerical width.

    Takes a SymbolicDiagram (particle labels + vertex types, no numerical
    masses or couplings required) and returns the symbolic formula as LaTeX.

    Input:
        diagram: SymbolicDiagram dict (labels + vertex types only)
        process_label: Optional display label

    Output:
        {
            "status": "ok",
            "formula": "\\Gamma \\sim \\frac{g_W^4 M^5}{64\\pi^3 M_W^4}",
            "scaling": {
                "phase_space_power": 2,
                "me_mass_power": 4,
                "total_mass_power": 5
            },
            "components": {
                "prefactor": "\\frac{1}{2M}",
                "phase_space": "\\Phi_3 \\sim ...",
                "matrix_element": "|M|^2 \\sim ...",
                "spin_averaging": "\\frac{1}{2s+1} = 1",
                "color_factor": "N_c = 1",
                "symmetry_factor": "S = 1",
                "propagator_suppression": "1/M_W^4"
            }
        }
    """

    # ======================== Runtime fields ======================== #
    diagram: Dict[str, Any] = RuntimeField(
        description=(
            "Symbolic diagram specification dict with keys: 'initial', "
            "'final', 'vertices', and optionally 'propagators', 'topology', "
            "'color_factor'. Particle labels required; masses/spins/coupling "
            "values are NOT needed."
        )
    )
    process_label: Optional[str] = RuntimeField(
        description="Process label for display (e.g., 'H → bb̄')",
        default=None,
    )
    # ================================================================ #

    # ========================= State fields ========================= #
    base_directory: str = StateField(
        description="Base sandbox directory for file operations"
    )
    # ================================================================ #

    def _setup(self):
        self.base_directory = os.path.abspath(self.base_directory)

    def _infer_spin(self, label: str) -> Optional[float]:
        """Infer spin from particle label using the SM database."""
        data = get_particle_data(label)
        if data is not None:
            return data.spin
        return None

    def _run(self) -> str:
        try:
            self._setup()
        except Exception as e:
            return self.format_error(error="Setup Error", reason=str(e))

        if self.diagram is None:
            return self.format_error(
                error="Missing Input",
                reason="'diagram' parameter is required",
            )

        # Unwrap EnumerateDiagrams output format if needed
        diagram = self.diagram
        if "diagram" in diagram and "initial" not in diagram:
            diagram = diagram["diagram"]

        # Parse as symbolic diagram
        try:
            sym = parse_symbolic_diagram(diagram)
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

        # ================================================================
        # Extract structural info
        # ================================================================
        n_body = len(sym.final)
        n_vertices = len(sym.vertices)
        n_propagators = len(sym.propagators)

        representative_vertex = sym.vertices[0].type
        operator_dim = OPERATOR_DIM_MAP.get(representative_vertex, 4)

        # Infer spins for determining phase space formula shape
        mother_label = sym.initial[0].label
        mother_spin = sym.initial[0].spin
        if mother_spin is None:
            mother_spin = self._infer_spin(mother_label)

        # Check for loop propagators
        has_loops = "loop" in sym.topology.lower()

        # ================================================================
        # Phase space scaling: M^(2n-4) / (pi factors)
        # ================================================================
        ps_power = 2 * n_body - 4  # mass power from phase space

        if n_body == 2:
            pi_factor = r"16\pi"
            ps_formula = r"\Phi_2 = \frac{1}{8\pi} \frac{|\vec{p}|}{M}"
        elif n_body == 3:
            pi_factor = r"64\pi^3"
            ps_formula = r"\Phi_3 \sim \frac{M^2}{256\pi^3}"
        else:
            pi_power = 2 * n_body - 3
            pi_factor = rf"\pi^{{{pi_power}}}"
            ps_formula = rf"\Phi_{n_body} \sim \frac{{M^{{{ps_power}}}}}{{(2\pi)^{{{3*n_body-4}}}}}"

        # ================================================================
        # Matrix element scaling
        # ================================================================
        if has_loops:
            me_mass_power = 2
        elif operator_dim == 4:
            me_mass_power = 2 * n_vertices
        elif operator_dim == 6:
            me_mass_power = 4
        else:
            me_mass_power = 2 * operator_dim - 4

        # Coupling term: preserve distinct coupling labels from each vertex
        # In |M|^2 each coupling appears squared (from M * M†)
        coupling_counts: Dict[str, int] = {}
        for v in sym.vertices:
            c = v.coupling
            # For dict couplings (chiral etc.), use a representative label
            if isinstance(c, dict):
                c = list(c.values())[0]
            coupling_counts[c] = coupling_counts.get(c, 0) + 2

        coupling_power = 2 * n_vertices

        # Build coupling term string
        coupling_parts = []
        for name, power in coupling_counts.items():
            if power == 2:
                coupling_parts.append(f"{name}^2")
            else:
                coupling_parts.append(f"{name}^{{{power}}}")
        coupling_term = " ".join(coupling_parts)

        # Matrix element formula
        me_formula = rf"|M|^2 \sim {coupling_term} M^{{{me_mass_power}}}"

        # ================================================================
        # Propagator suppression
        # ================================================================
        prop_symbols: list[str] = []
        light_prop_power = 0

        for prop in sym.propagators:
            prop_label = prop.label

            # Respect explicit regime if set by the user
            if prop.regime == "heavy":
                is_heavy, is_light = True, False
            elif prop.regime == "light":
                is_heavy, is_light = False, True
            elif prop.mass is not None and sym.initial[0].mass is not None:
                # Determine regime from mass ratio
                ratio = prop.mass / sym.initial[0].mass if sym.initial[0].mass > 0 else 0
                is_heavy = ratio > 5.0
                is_light = ratio < 0.2
            else:
                # Infer from known particle masses
                data = get_particle_data(prop_label)
                mother_data = get_particle_data(mother_label)
                if data and data.mass and mother_data and mother_data.mass and mother_data.mass > 0:
                    ratio = data.mass / mother_data.mass
                    is_heavy = ratio > 5.0
                    is_light = ratio < 0.2
                else:
                    # Default: assume heavy for named gauge bosons, light for photon/gluon
                    is_heavy = prop_label.upper() in ("W", "W+", "W-", "Z", "H", "T")
                    is_light = prop_label.lower() in ("gamma", "g", "photon", "gluon")

            if is_light:
                light_prop_power += 4
            else:
                prop_symbols.append(f"M_{{{prop_label}}}")

        # Build propagator suppression formula
        if prop_symbols:
            symbol_counts = Counter(prop_symbols)
            prop_terms = []
            for sym_str, count in symbol_counts.items():
                power = 4 * count
                if power == 4:
                    prop_terms.append(f"{sym_str}^4")
                else:
                    prop_terms.append(f"{sym_str}^{{{power}}}")
            prop_term = " ".join(prop_terms)
            prop_formula = rf"\frac{{1}}{{{prop_term}}}"
        else:
            prop_term = None
            prop_formula = None

        # ================================================================
        # Loop factor
        # ================================================================
        if has_loops:
            loop_formula = r"\frac{1}{(16\pi^2)}"
        else:
            loop_formula = None

        # ================================================================
        # Total mass power: (1/2M) * M^ps_power * M^me_mass_power - light_prop
        # The 1/(2M) prefactor contributes -1
        # ================================================================
        total_mass_power = -1 + ps_power + me_mass_power - light_prop_power

        if total_mass_power == 1:
            mass_term = "M"
        elif total_mass_power == 0:
            mass_term = "1"
        else:
            mass_term = f"M^{{{total_mass_power}}}"

        # ================================================================
        # Build unified formula
        # ================================================================
        # Denominator parts
        denom_parts = [pi_factor]
        if prop_term:
            denom_parts.append(prop_term)
        if has_loops:
            denom_parts.append(r"(16\pi^2)")

        denominator = " ".join(denom_parts)

        if mass_term == "1":
            formula = rf"\Gamma \sim \frac{{{coupling_term}}}{{{denominator}}}"
        else:
            formula = rf"\Gamma \sim \frac{{{coupling_term} {mass_term}}}{{{denominator}}}"

        # ================================================================
        # Build components dict (full factorisation of the width)
        # ================================================================
        # Prefactor: always 1/(2M)
        prefactor_str = r"\frac{1}{2M}"

        # Spin averaging: 1/(2s+1) for the mother particle
        if mother_spin is not None and mother_spin > 0:
            denom = int(2 * mother_spin + 1)
            spin_avg_str = rf"\frac{{1}}{{2s+1}} = \frac{{1}}{{{denom}}}"
        else:
            spin_avg_str = r"\frac{1}{2s+1} = 1"

        # Color factor
        color_val = sym.color_factor if sym.color_factor is not None else 1.0
        if color_val == 1.0:
            color_str = "N_c = 1"
        else:
            color_str = f"N_c = {int(color_val) if color_val == int(color_val) else color_val}"

        # Symmetry factor: count identical final-state labels
        final_labels = [p.label for p in sym.final]
        label_counts = Counter(final_labels)
        max_dup = max(label_counts.values())
        if max_dup > 1:
            sym_val = math.factorial(max_dup)
            symmetry_str = f"S = {max_dup}! = {sym_val}"
        else:
            symmetry_str = "S = 1"

        components: Dict[str, Any] = {
            "prefactor": prefactor_str,
            "phase_space": ps_formula,
            "matrix_element": me_formula,
            "spin_averaging": spin_avg_str,
            "color_factor": color_str,
            "symmetry_factor": symmetry_str,
        }
        if prop_formula:
            components["propagator_suppression"] = prop_formula
        if loop_formula:
            components["loop_factor"] = loop_formula

        result: Dict[str, Any] = {
            "status": "ok",
            "schema": SCHEMA_VERSION,
            "formula": formula,
            "formula_type": "scaling",
            "formula_note": (
                "Formula shows parametric scaling only. Numerical prefactors "
                "(spin sums, phase space fudge factors, O(1) constants) are not "
                "included. Do not compare formulas across multiplicities to get "
                "ratios — use numerical EstimateDecayWidthNDA results instead."
            ),
            "scaling": {
                "phase_space_power": ps_power,
                "me_mass_power": me_mass_power,
                "total_mass_power": total_mass_power,
                "coupling_power": coupling_power,
            },
            "components": components,
            "diagram": {
                "topology": sym.topology,
                "n_vertices": n_vertices,
                "n_propagators": n_propagators,
                "n_body": n_body,
                "loop_order": 1 if has_loops else 0,
                "operator_dimension": operator_dim,
            },
        }

        if self.process_label:
            result["process_label"] = self.process_label

        return json.dumps(result, separators=(",", ":"), ensure_ascii=False)
