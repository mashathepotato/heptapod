"""
# compare_phase_space.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
import json
import math
from typing import List, Optional
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

SCHEMA_VERSION = "nda-phasespace-compare-1.0"


class ComparePhaseSpaceTool(BaseTool):
    """
    Compares n-body phase space volumes across different final state multiplicities.

    This tool calculates phase space for multiple n-body configurations and
    produces a comparison table showing how phase space scales with multiplicity.
    Useful for understanding kinematic suppression in many-body decays.

    Uses the massless phase space formula from Eq. A.2 of arXiv:1402.1178:
        Φ_n(M) = M^(2n-4) / [2^(4n-5) × π^(2n-3) × (n-1)! × (n-2)!]

    Inputs (runtime):
      - mother_mass_gev: Mother particle mass in GeV
      - n_body_values: List of n-body multiplicities to compare (e.g., [3, 5, 7, 9])
      - reference_n_body: (optional) Which n-body to use as reference for ratios (default: first in list)

    State:
      - base_directory: Sandbox root (required by BaseTool, not used here)

    Output (JSON):
      {
        "status": "ok",
        "schema": "nda-phasespace-compare-1.0",
        "mother_mass_gev": 0.1057,
        "comparison_table": [
          {
            "n_body": 3,
            "phase_space": 3.5e-5,
            "ratio_to_reference": 1.0,
            "suppression_per_pair": null,
            "formula": "Φ_3 = M^2/(32π^3)"
          },
          ...
        ],
        "summary_markdown": "| n-body | Φ_n | Ratio | Suppression/pair |\\n..."
      }
    """

    # ======================== Runtime fields ======================== #
    mother_mass_gev: float = RuntimeField(
        description="Mother particle mass in GeV (characteristic energy scale)"
    )
    n_body_values: List[int] = RuntimeField(
        description="List of n-body multiplicities to compare (e.g., [3, 5, 7, 9])"
    )
    reference_n_body: Optional[int] = RuntimeField(
        default=None,
        description="Which n-body to use as reference for ratios (default: first in list)"
    )
    # ================================================================ #

    # ========================= State fields ========================= #
    base_directory: str = StateField(
        description="Base sandbox directory (not used for phase space calculations)"
    )
    # ================================================================ #

    def _calculate_phase_space_massless(self, M: float, n: int) -> float:
        """
        Calculate n-body phase space for massless final states.

        Φ_n(M) = (M^(2n-4)) / ((2^(4n-5)) (π^(2n-3)) (n-1)! (n-2)!)
        """
        fact_n_minus_1 = math.factorial(n - 1)
        fact_n_minus_2 = math.factorial(n - 2)

        numerator = M ** (2*n - 4)
        denominator = (
            (2 ** (4*n - 5)) *
            (math.pi ** (2*n - 3)) *
            fact_n_minus_1 *
            fact_n_minus_2
        )

        return numerator / denominator

    def _generate_formula(self, n: int) -> str:
        """Generate symbolic formula for n-body phase space."""
        power = 2*n - 4
        denom_power_2 = 4*n - 5
        denom_power_pi = 2*n - 3
        fact1 = n - 1
        fact2 = n - 2

        if n == 2:
            return "Φ_2 = 1/(8π)"
        elif n == 3:
            return "Φ_3 = M²/(32π³)"
        elif n == 4:
            denom_val = int((2 ** denom_power_2) * math.factorial(fact1) * math.factorial(fact2))
            return f"Φ_4 = M⁴/({denom_val}π⁵)"
        else:
            denom_val = int((2 ** denom_power_2) * math.factorial(fact1) * math.factorial(fact2))
            return f"Φ_{n} = M^{power}/({denom_val}π^{denom_power_pi})"

    def _format_scientific(self, value: float, precision: int = 2) -> str:
        """Format a number in scientific notation."""
        if value == 0:
            return "0"
        exp = int(math.floor(math.log10(abs(value))))
        mantissa = value / (10 ** exp)
        if exp == 0:
            return f"{mantissa:.{precision}f}"
        return f"{mantissa:.{precision}f}×10^{exp}"

    def _run(self) -> str:
        """Main execution method."""
        # Validate inputs
        if self.mother_mass_gev <= 0:
            return self.format_error(
                error="Invalid Mass",
                reason=f"mother_mass_gev must be positive, got {self.mother_mass_gev}",
                suggestion="Provide a positive mass in GeV"
            )

        if not self.n_body_values or len(self.n_body_values) < 1:
            return self.format_error(
                error="Invalid n_body_values",
                reason="Must provide at least one n-body value",
                suggestion="Provide a list like [3, 5, 7, 9]"
            )

        for n in self.n_body_values:
            if n < 2:
                return self.format_error(
                    error="Invalid n_body",
                    reason=f"All n_body values must be >= 2, got {n}",
                    suggestion="Use n >= 2 for valid phase space"
                )

        # Sort n-body values for consistent output
        n_values = sorted(self.n_body_values)

        # Determine reference
        ref_n = self.reference_n_body if self.reference_n_body else n_values[0]
        if ref_n not in n_values:
            return self.format_error(
                error="Invalid reference_n_body",
                reason=f"Reference {ref_n} not in n_body_values {n_values}",
                suggestion="Choose a reference that's in the list"
            )

        # Calculate phase space for all multiplicities
        M = self.mother_mass_gev
        results = []
        ref_phi = self._calculate_phase_space_massless(M, ref_n)

        prev_phi = None
        prev_n = None

        for n in n_values:
            phi = self._calculate_phase_space_massless(M, n)
            ratio_to_ref = phi / ref_phi

            # Calculate suppression per e+e- pair (2 additional particles)
            suppression_per_pair = None
            if prev_phi is not None and prev_n is not None:
                n_diff = n - prev_n
                if n_diff > 0:
                    # Suppression factor per pair of particles added
                    suppression_per_pair = (phi / prev_phi) ** (2.0 / n_diff)

            results.append({
                "n_body": n,
                "phase_space": phi,
                "ratio_to_reference": ratio_to_ref,
                "suppression_per_pair": suppression_per_pair,
                "formula": self._generate_formula(n)
            })

            prev_phi = phi
            prev_n = n

        # Build markdown table
        lines = [
            f"### Phase Space Comparison (M = {M:.4f} GeV)",
            "",
            "| n-body | Formula | Φ_n (GeV^2n-4) | Ratio to {}-body | Suppression/pair |".format(ref_n),
            "|--------|---------|----------------|------------------|------------------|"
        ]

        for r in results:
            phi_str = self._format_scientific(r["phase_space"])
            ratio_str = self._format_scientific(r["ratio_to_reference"])
            if r["suppression_per_pair"] is not None:
                supp_str = self._format_scientific(r["suppression_per_pair"])
            else:
                supp_str = "—"

            lines.append(f"| {r['n_body']} | {r['formula']} | {phi_str} | {ratio_str} | {supp_str} |")

        # Add scaling explanation
        lines.extend([
            "",
            "**Key insight**: Phase space suppression per e+e- pair is ~M⁴/(256π⁴) × 1/[n²(n²-1)],",
            "which depends on n and becomes stronger at higher multiplicities due to factorial growth."
        ])

        summary_markdown = "\n".join(lines)

        result = {
            "status": "ok",
            "schema": SCHEMA_VERSION,
            "mother_mass_gev": M,
            "reference_n_body": ref_n,
            "comparison_table": results,
            "summary_markdown": summary_markdown
        }

        return json.dumps(result, indent=2, ensure_ascii=False)
