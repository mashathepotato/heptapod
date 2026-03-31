"""
# matrix_element.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
import json
import re
from typing import Optional, List, Union
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

SCHEMA_VERSION = "nda-matrixelement-1.0"

# ---------------------------------------------------------------------------
# NDA scaling families
#
# Each family defines the dimensional-analysis scaling for |M|^2.  Multiple
# vertex types share the same NDA scaling (e.g. all VFF couplings scale as
# g^2 M^2).  The vertex type names match those used by ComputeSymbolicAmplitude.
# ---------------------------------------------------------------------------

_SFF = {
    "latex": r"y \bar{\psi} \psi \phi",
    "scaling": "y^2 M^2",
    "coupling_symbol": "y",
    "description": "Scalar-fermion-fermion coupling",
    "family": "sff",
    "op_dim": 4,
}

_VFF = {
    "latex": r"g A^\mu \bar{\psi} \gamma_\mu \psi",
    "scaling": "g^2 M^2",
    "coupling_symbol": "g",
    "description": "Vector-fermion-fermion coupling",
    "family": "vff",
    "op_dim": 4,
}

_SCALAR_3PT = {
    "latex": r"\lambda \phi^3",
    "scaling": r"\lambda^2 M^2",
    "coupling_symbol": r"\lambda",
    "description": "Cubic scalar coupling",
    "family": "scalar-3pt",
    "op_dim": 4,
}

_SCALAR_4PT = {
    "latex": r"\lambda \phi^4",
    "scaling": r"\lambda^2",
    "coupling_symbol": r"\lambda",
    "description": "Quartic scalar coupling (Higgs-like)",
    "family": "scalar-4pt",
    "op_dim": 4,
}

_DIM5_WEINBERG = {
    "latex": r"\frac{1}{\Lambda} L L H H",
    "scaling": r"\frac{M^2}{\Lambda^2}",
    "coupling_symbol": r"G_F",
    "description": "Dimension-5 Weinberg operator (neutrino mass)",
    "family": "dim5-weinberg",
    "op_dim": 5,
}

_DIM6_4FERMION = {
    "latex": r"\frac{1}{\Lambda^2} (\bar{\psi}\psi)^2",
    "scaling": r"\frac{M^4}{\Lambda^4}",
    "coupling_symbol": r"G_F",
    "description": "Dimension-6 four-fermion operator",
    "family": "dim6-4fermion",
    "op_dim": 6,
}

_DIM5_SVV = {
    "latex": r"\frac{g}{\Lambda} \phi F_{\mu\nu} F^{\mu\nu}",
    "scaling": r"\frac{g^2 M^4}{\Lambda^2}",
    "coupling_symbol": "g",
    "description": "Dimension-5 scalar-vector-vector operator",
    "family": "dim5-svv",
    "op_dim": 5,
}

_CUSTOM = {
    "latex": "g^n M^d",
    "scaling": "g^n M^d",
    "coupling_symbol": "g",
    "description": "User-specified coupling and mass dimension",
    "family": "custom",
    "op_dim": 4,
}

# ---------------------------------------------------------------------------
# Unified vertex type → NDA scaling lookup
#
# One flat dict keyed by every accepted vertex type name.  Both the NDA path
# and the exact path use the same names; no alias layer needed.
# ---------------------------------------------------------------------------

INTERACTION_TYPES = {
    # SFF family (y^2 M^2 scaling)
    "yukawa":           _SFF,
    "pseudoscalar":     _SFF,
    "chiral":           _SFF,
    "yukawa-chiral":    _SFF,
    "scalar-chiral":    _SFF,
    "scalar-va":        _SFF,

    # VFF family (g^2 M^2 scaling)
    "vector":           _VFF,
    "gauge-vector":     _VFF,
    "axial-vector":     _VFF,
    "gauge-axial":      _VFF,
    "va":               _VFF,
    "vector-axial":     _VFF,
    "left-handed":      _VFF,
    "right-handed":     _VFF,
    "vector-chiral":    _VFF,
    "tensor":           _VFF,
    "dipole":           _VFF,
    "tensor-chiral":    _VFF,
    "dipole-chiral":    _VFF,

    # Bosonic
    "scalar-3pt":       _SCALAR_3PT,
    "scalar-4pt":       _SCALAR_4PT,

    # EFT operators
    "dim5-weinberg":    _DIM5_WEINBERG,
    "dim6-4fermion":    _DIM6_4FERMION,

    # Dim-5 SVV (field-strength operators)
    "field-strength":       _DIM5_SVV,
    "dim5-ff":              _DIM5_SVV,
    "dual-field-strength":  _DIM5_SVV,
    "dim5-ff-dual":         _DIM5_SVV,

    # Fallback
    "custom":           _CUSTOM,
}


def resolve_nda_interaction_type(vtype: str) -> str:
    """Resolve a vertex type string to a canonical key in INTERACTION_TYPES.

    Handles case normalization, hyphen/underscore equivalence, and strips
    valence suffixes like ``-3pt``, ``-4pt`` that EnumerateDiagrams appends.
    Returns 'custom' for unrecognized types.
    """
    normalized = vtype.lower().strip()

    # Try the original name first (handles real types like "scalar-4pt")
    if normalized in INTERACTION_TYPES:
        return normalized

    # Strip valence suffix (e.g., "-3pt", "-4pt") from EnumerateDiagrams output
    stripped = re.sub(r'-\d+pt$', '', normalized)
    if stripped != normalized and stripped in INTERACTION_TYPES:
        return stripped

    # Try with hyphens replaced by underscores and vice versa (on stripped form)
    for candidate in (normalized, stripped):
        alt = candidate.replace("_", "-")
        if alt in INTERACTION_TYPES:
            return alt
        alt = candidate.replace("-", "_")
        if alt in INTERACTION_TYPES:
            return alt

    return "custom"


# Spin states: UFO convention (2s+1)
SPIN_STATES = {
    "scalar": 1,      # s=0
    "fermion": 2,     # s=1/2
    "vector": 3,      # s=1 (massive)
    "vector-massless": 2,  # s=1 (massless, 2 transverse polarizations)
    "graviton": 5,    # s=2
}


class EstimateMatrixElementTool(BaseTool):
    """
    Estimates matrix element squared using dimensional analysis and spin counting.

    This tool calculates <|M|^2> for a given interaction type and particle content.
    It handles spin averaging/summing, color factors, and coupling constant scaling.

    Inputs (runtime):
      - interaction_type: Vertex type name (any name accepted by both NDA and exact paths).
          Examples: "yukawa", "va", "vector", "scalar-va", "gauge-vector", "chiral", etc.

      - mother_spin: Mother particle spin (use names or UFO codes)
          Options: "scalar"(=1), "fermion"(=2), "vector"(=3), or integer

      - final_state_spins: List of final state spins
          Example: ["fermion", "fermion"] or [2, 2]

      - coupling_value: Coupling constant value
          - Dimensionless for renormalizable interactions (e.g., 0.1 for sqrt(alpha_em))
          - May have dimensions for EFT operators (e.g., GeV^-2 for dim-6 4-fermion)
          - When coupling has dimensions, include them in the numerical value

      - energy_scale_gev: Characteristic energy (usually mother mass)

      - operator_dimension: (optional) Operator dimension for EFT (default: from vertex type)
          - 4: Renormalizable (|M|^2 ~ g^2 * E^2)
          - 6: Dimension-6 operators (|M|^2 scaling depends on interaction type)
          - >6: Higher-dimensional operators

      - cutoff_scale_gev: (optional) Cutoff scale for higher-dim operators (default: 1000 GeV)
          - Used for generic higher-dim operators (not dim6-4fermion)
          - Provides 1/Lambda^(2(d-4)) suppression

      - color_factor: (optional) Color factor (default: 1, use 3 for QCD)

    State:
      - base_directory: Sandbox root (not used, required by BaseTool)

    Behavior:
      1. Looks up interaction type from preset library
      2. Calculates spin averaging and summing factors
      3. Applies dimensional analysis for operator dimension
      4. Returns LaTeX formula and numerical estimate

    Output (JSON):
      {
        "status": "ok",
        "matrix_element_sq": 6.25e4,
        "formula": "|M|^2 ~ y^2 M^2",
        "interaction": "yukawa",
        "coupling": "y"
      }

    Errors:
      Returns self.format_error() on failures including:
        - Unknown interaction type
        - Invalid spin specification
        - Negative coupling or energy scale
    """

    # ======================== Runtime fields ======================== #
    interaction_type: str = RuntimeField(
        description="Vertex type name: 'yukawa', 'va', 'vector', 'scalar-va', 'chiral', 'scalar-3pt', 'dim6-4fermion', 'custom', etc."
    )
    mother_spin: Union[str, int] = RuntimeField(
        description="Mother particle spin: 'scalar', 'fermion', 'vector', or UFO code (1, 2, 3)"
    )
    final_state_spins: List[Union[str, int]] = RuntimeField(
        description="List of final state spins, e.g., ['fermion', 'fermion'] or [2, 2]"
    )
    coupling_value: float = RuntimeField(
        description="Coupling constant value (dimensionless for renormalizable, may have dimensions for EFT). Examples: 0.1 for sqrt(alpha_em), 1.166e-5 for G_F (GeV^-2)"
    )
    energy_scale_gev: float = RuntimeField(
        description="Characteristic energy scale in GeV (typically mother mass)"
    )
    operator_dimension: Optional[int] = RuntimeField(
        default=None,
        description="Operator dimension (default: inferred from vertex type; 4=renormalizable, >4=EFT)"
    )
    cutoff_scale_gev: Optional[float] = RuntimeField(
        default=1000.0,
        description="Cutoff scale in GeV for higher-dimensional operators (default: 1000 TeV scale)"
    )
    color_factor: Optional[float] = RuntimeField(
        default=1.0,
        description="Color factor (1=colorless, 3=QCD fundamental, 8=QCD adjoint)"
    )
    # ================================================================ #

    # ========================= State fields ========================= #
    base_directory: str = StateField(
        description="Base sandbox directory (not used)"
    )
    # ================================================================ #

    def _parse_spin(self, spin: Union[str, int]) -> int:
        """
        Convert spin name to UFO code (2s+1).

        Args:
            spin: Spin name or code

        Returns:
            UFO spin code

        Raises:
            ValueError: If spin is unknown
        """
        if isinstance(spin, int):
            return spin
        if isinstance(spin, str):
            spin_lower = spin.lower()
            if spin_lower in SPIN_STATES:
                return SPIN_STATES[spin_lower]
        raise ValueError(f"Unknown spin: {spin}")

    def _run(self) -> str:
        """
        Main execution method.

        Returns:
            JSON string with matrix element estimate
        """
        # Resolve vertex type to canonical key
        resolved = resolve_nda_interaction_type(self.interaction_type)
        if resolved not in INTERACTION_TYPES:
            available = sorted(set(INTERACTION_TYPES.keys()))
            return self.format_error(
                error="Unknown Interaction Type",
                reason=f"interaction_type='{self.interaction_type}' not recognized",
                context=f"Available types: {', '.join(available)}",
                suggestion="Choose from available types or use 'custom'"
            )

        interaction_info = INTERACTION_TYPES[resolved]

        # Parse spins
        try:
            mother_spin_code = self._parse_spin(self.mother_spin)
            final_spin_codes = [self._parse_spin(s) for s in self.final_state_spins]
        except ValueError as e:
            return self.format_error(
                error="Invalid Spin",
                reason=str(e),
                suggestion="Use 'scalar', 'fermion', 'vector', or UFO codes (1, 2, 3)"
            )

        # Validate coupling and energy
        if self.coupling_value < 0:
            return self.format_error(
                error="Invalid Coupling",
                reason=f"coupling_value must be non-negative, got {self.coupling_value}"
            )

        if self.energy_scale_gev <= 0:
            return self.format_error(
                error="Invalid Energy Scale",
                reason=f"energy_scale_gev must be positive, got {self.energy_scale_gev}"
            )

        # Operator dimension: use explicit value if given, else from scaling family
        op_dim = self.operator_dimension if self.operator_dimension is not None else interaction_info["op_dim"]

        # Spin averaging for initial state: 1 / (2s+1)
        spin_avg_factor = 1.0 / mother_spin_code

        # Spin summing for final states: product of (2s+1)
        spin_sum_factor = 1.0
        for spin_code in final_spin_codes:
            spin_sum_factor *= spin_code

        # Base matrix element estimate
        g_sq = self.coupling_value ** 2
        E = self.energy_scale_gev

        # Energy scaling based on operator dimension
        if op_dim == 4:
            # Renormalizable: |M|^2 ~ g^2 E^2
            energy_factor = E ** 2
            energy_scaling_power = 2
        else:
            # Higher-dimensional operators
            # Special case: For dim6-4fermion with G_F, the coupling already has dimensions GeV^-2
            # In this case, |M|^2 ~ G_F^2 * E^4 (not E^6/Lambda^4)
            if interaction_info["family"] == "dim6-4fermion":
                # G_F coupling already includes 1/M_W^2 suppression
                # |M|^2 ~ G_F^2 * E^4
                energy_factor = E ** 4
                energy_scaling_power = 4
            else:
                # Generic higher-dimensional: |M|^2 ~ (g^2 / Lambda^(2(d-4))) * E^(2(d-4)+2)
                Lambda = self.cutoff_scale_gev
                dim_suppression = Lambda ** (2 * (op_dim - 4))
                energy_power = 2 * (op_dim - 4) + 2
                energy_factor = (E ** energy_power) / dim_suppression
                energy_scaling_power = energy_power

        # Combine factors
        matrix_elem_sq = (
            spin_avg_factor *
            spin_sum_factor *
            self.color_factor *
            g_sq *
            energy_factor
        )

        # Build LaTeX formulas (symbolic and numeric)
        coupling_sym = interaction_info["coupling_symbol"]

        if op_dim == 4:
            # Symbolic version with explicit coupling symbol
            formula_latex_symbolic = rf"|M|^2 \sim {coupling_sym}^2 M^2"

            # Numeric version with substituted values
            formula_latex_numeric = (
                rf"|M|^2 \sim {coupling_sym}^2 M^2 "
                rf"\sim ({self.coupling_value:.3g})^2 ({E:.1f})^2 "
                rf"\approx {matrix_elem_sq:.3e}"
            )
        else:
            d = op_dim
            if coupling_sym == r"G_F":
                dim_analysis_power = 2 * d - 4
                effective_power = dim_analysis_power - 2*2
                formula_latex_symbolic = rf"|M|^2 \sim G_F^2 M^{{{effective_power}}}"
            else:
                formula_latex_symbolic = rf"|M|^2 \sim \frac{{{coupling_sym}^2 M^{{{energy_scaling_power}}}}}{{\Lambda^{{{2*(d-4)}}}}}"

            # Numeric version
            formula_latex_numeric = (
                rf"|M|^2 \sim \frac{{{coupling_sym}^2 M^{{{energy_scaling_power}}}}}{{\Lambda^{{{2*(d-4)}}}}} "
                rf"\sim \frac{{({self.coupling_value:.3g})^2 ({E:.1f})^{{{energy_scaling_power}}}}}{{({self.cutoff_scale_gev:.0f})^{{{2*(d-4)}}}}} "
                rf"\approx {matrix_elem_sq:.3e}"
            )

        # Build streamlined result
        result = {
            "status": "ok",
            "matrix_element_sq": matrix_elem_sq,
            "formula": formula_latex_symbolic,  # Clean symbolic form
            "interaction": resolved,
            "coupling": coupling_sym,
        }

        # Add EFT info only if relevant
        if op_dim > 4:
            result["operator_dim"] = op_dim

        return json.dumps(result, separators=(",", ":"), ensure_ascii=False)
