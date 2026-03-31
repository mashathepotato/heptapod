"""
# phase_space.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
import json
import math
from typing import Optional, List
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

SCHEMA_VERSION = "nda-phasespace-1.0"


class EstimatePhaseSpaceTool(BaseTool):
    """
    Estimates n-body phase space volume for massless final states.

    This tool calculates the Lorentz-invariant phase space (LIPS) volume
    for n-body decays assuming massless final state particles. It uses
    the formula from Eq. A.2 of arXiv:1402.1178:

    Φ_n(M) = (1 / (2^(4n-5) π^(2n-3))) x (M^(2n-4) / (n-1)!(n-2)!)

    This is purely kinematic - no coupling constants or spin factors.

    Inputs (runtime):
      - mother_mass_gev: Mother particle mass in GeV (energy scale)
      - n_body: Number of final state particles (n >= 2)
      - final_state_masses_gev: (optional) List of final state masses for corrections

    State:
      - base_directory: Sandbox root (required by BaseTool, not used here)

    Behavior:
      1. Validates that n >= 2
      2. Calculates phase space volume using the massless approximation
      3. Optionally applies mass corrections if final_state_masses provided
      4. Returns LaTeX formula showing the scaling

    Output (JSON):
      {
        "status": "ok",
        "schema": "nda-phasespace-1.0",
        "mother_mass_gev": 125.0,
        "n_body": 2,
        "phase_space_volume": 3.98e-2,
        "formula_latex": "\\Phi_2(M) = \\frac{1}{8\\pi} \\approx 0.0398",
        "scaling": "M^{2n-4} = M^{0}",
        "notes": ["Massless approximation", "Tree-level kinematics"]
      }

    Errors:
      Returns self.format_error() on failures including:
        - Invalid n_body (must be >= 2)
        - Negative or zero mother mass
    """

    # ======================== Runtime fields ======================== #
    mother_mass_gev: float = RuntimeField(
        description="Mother particle mass in GeV (characteristic energy scale)"
    )
    n_body: int = RuntimeField(
        description="Number of final state particles (must be >= 2)"
    )
    final_state_masses_gev: Optional[List[float]] = RuntimeField(
        default=None,
        description="Optional: List of final state masses in GeV for mass corrections"
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

        Args:
            M: Mother particle mass (GeV)
            n: Number of final state particles

        Returns:
            Phase space volume
        """
        # Factorial calculations
        fact_n_minus_1 = math.factorial(n - 1)
        fact_n_minus_2 = math.factorial(n - 2)

        # Numerator: M^(2n-4)
        numerator = M ** (2*n - 4)

        # Denominator: 2^(4n-5) * π^(2n-3) * (n-1)! * (n-2)!
        denominator = (
            (2 ** (4*n - 5)) *
            (math.pi ** (2*n - 3)) *
            fact_n_minus_1 *
            fact_n_minus_2
        )

        return numerator / denominator

    def _generate_latex_formula(self, M: float, n: int, phi_n: float, symbolic: bool = True) -> str:
        """
        Generate LaTeX formula for the phase space volume.

        Args:
            M: Mother mass
            n: Number of particles
            phi_n: Numerical phase space value
            symbolic: If True, use symbolic M; if False, substitute numerical value

        Returns:
            LaTeX string
        """
        power = 2*n - 4
        denom_power_2 = 4*n - 5
        denom_power_pi = 2*n - 3
        fact1 = n - 1
        fact2 = n - 2

        # Calculate numerical coefficient
        import math
        coeff_numeric = 1.0 / ((2 ** denom_power_2) * (math.pi ** denom_power_pi) *
                               math.factorial(fact1) * math.factorial(fact2))

        # Special cases for cleaner expressions
        if n == 2:
            # 2-body: Φ_2 = 1/(8π) ≈ 0.0398
            if symbolic:
                return r"\Phi_2 = \frac{1}{8\pi}"
            else:
                return rf"\Phi_2 = \frac{{1}}{{8\pi}} \approx {coeff_numeric:.4f}"

        elif n == 3:
            # 3-body: Φ_3 = M^2/(32π^3)
            if symbolic:
                return r"\Phi_3 = \frac{M^2}{32\pi^3}"
            else:
                return rf"\Phi_3 = \frac{{M^2}}{{32\pi^3}} \approx \frac{{M^2}}{{{1/(coeff_numeric):.1f}}}"

        elif n == 4:
            # 4-body: Φ_4 = M^4/(2048 π^5 × 12)
            denom_val = int((2 ** denom_power_2) * math.factorial(fact1) * math.factorial(fact2))
            if symbolic:
                return rf"\Phi_4 = \frac{{M^4}}{{{denom_val} \pi^5}}"
            else:
                return rf"\Phi_4 = \frac{{M^4}}{{{denom_val} \pi^5}} \approx \frac{{M^4}}{{{1/coeff_numeric:.1e}}}"

        else:
            # General case
            denom_val = int((2 ** denom_power_2) * math.factorial(fact1) * math.factorial(fact2))
            if symbolic:
                if power == 0:
                    return rf"\Phi_{{{n}}} = \frac{{1}}{{{denom_val} \pi^{{{denom_power_pi}}}}}"
                else:
                    return rf"\Phi_{{{n}}} = \frac{{M^{{{power}}}}}{{{denom_val} \pi^{{{denom_power_pi}}}}}"
            else:
                return (
                    rf"\Phi_{{{n}}} = \frac{{M^{{{power}}}}}{{{denom_val} \pi^{{{denom_power_pi}}}}} "
                    rf"\approx {phi_n:.4e}"
                )

    def _run(self) -> str:
        """
        Main execution method.

        Returns:
            JSON string with phase space estimate
        """
        # Validate inputs
        if self.n_body < 2:
            return self.format_error(
                error="Invalid n_body",
                reason=f"n_body must be >= 2, got {self.n_body}",
                suggestion="Set n_body to 2 for two-body decays, 3 for three-body, etc."
            )

        if self.mother_mass_gev <= 0:
            return self.format_error(
                error="Invalid Mass",
                reason=f"mother_mass_gev must be positive, got {self.mother_mass_gev}",
                suggestion="Provide a positive mass in GeV"
            )

        # Check mass threshold if final state masses provided
        if self.final_state_masses_gev:
            if len(self.final_state_masses_gev) != self.n_body:
                return self.format_error(
                    error="Mass List Mismatch",
                    reason=f"Provided {len(self.final_state_masses_gev)} masses but n_body={self.n_body}",
                    suggestion="Ensure final_state_masses_gev has exactly n_body elements"
                )

            total_final_mass = sum(self.final_state_masses_gev)
            if self.mother_mass_gev < total_final_mass:
                return self.format_error(
                    error="Kinematically Forbidden",
                    reason=f"M_mother ({self.mother_mass_gev:.3f} GeV) < Σm_final ({total_final_mass:.3f} GeV)",
                    suggestion="This decay is kinematically impossible"
                )

        # Calculate phase space
        try:
            phi_n = self._calculate_phase_space_massless(self.mother_mass_gev, self.n_body)
        except Exception as e:
            return self.format_error(
                error="Calculation Error",
                reason=str(e),
                suggestion="Check input parameters"
            )

        # Generate both symbolic and numerical LaTeX formulas
        latex_formula_symbolic = self._generate_latex_formula(self.mother_mass_gev, self.n_body, phi_n, symbolic=True)
        latex_formula_numeric = self._generate_latex_formula(self.mother_mass_gev, self.n_body, phi_n, symbolic=False)

        # Scaling with mass
        power = 2 * self.n_body - 4
        if power == 0:
            scaling = "M^{0} = 1"
        else:
            scaling = f"M^{{{power}}}"

        # Build streamlined result
        result = {
            "status": "ok",
            "phase_space_volume": phi_n,
            "formula": latex_formula_symbolic,  # Clean symbolic form
            "scaling": scaling,                 # M^(2n-4)
            "n_body": self.n_body,
        }

        return json.dumps(result, separators=(",", ":"), ensure_ascii=False)
