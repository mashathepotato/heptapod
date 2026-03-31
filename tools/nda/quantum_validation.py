"""
# quantum_validation.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Quantum number conservation validation for Feynman diagrams.

Validates that quantum numbers are conserved at each vertex.
"""

from typing import List, Tuple
from dataclasses import dataclass

try:
    from .particle_database import infer_quantum_numbers, SM_PARTICLES
except ImportError:
    from particle_database import infer_quantum_numbers, SM_PARTICLES


# Particle swap suggestions for common lepton number issues
LEPTON_PARTICLE_SWAPS = {
    "lepton_e": [
        ("nu_e", "nu_e_bar", "electron neutrino ↔ antineutrino"),
        ("e", "e+", "electron ↔ positron"),
    ],
    "lepton_mu": [
        ("nu_mu", "nu_mu_bar", "muon neutrino ↔ antineutrino"),
        ("mu", "mu+", "muon ↔ antimuon"),
    ],
    "lepton_tau": [
        ("nu_tau", "nu_tau_bar", "tau neutrino ↔ antineutrino"),
        ("tau", "tau+", "tau ↔ antitau"),
    ],
}


def _suggest_fixes(quantum_number: str, particles: list, diff: float) -> str:
    """
    Suggest particle swaps to fix a quantum number violation.

    Args:
        quantum_number: The violated quantum number (e.g., "lepton_e")
        particles: List of final state particles to check
        diff: The difference (outgoing - incoming) that needs to be corrected

    Returns:
        Hint string with suggested fixes
    """
    if quantum_number not in LEPTON_PARTICLE_SWAPS:
        return ""

    suggestions = []
    swaps = LEPTON_PARTICLE_SWAPS[quantum_number]

    for particle, antiparticle, desc in swaps:
        # Check if any final particles match these labels
        for p in particles:
            if p.label is None:
                continue
            label_lower = p.label.lower().replace("-", "").replace("+", "")

            # If diff > 0, we have too much of this lepton number
            # Suggest replacing particles with antiparticles
            if diff > 0:
                if particle in label_lower or label_lower == particle:
                    suggestions.append(f"replace '{p.label}' with '{antiparticle}' ({desc})")
            # If diff < 0, we need more of this lepton number
            # Suggest replacing antiparticles with particles
            else:
                if "bar" in label_lower or antiparticle.replace("_bar", "") in label_lower:
                    suggestions.append(f"replace '{p.label}' with '{particle}' ({desc})")

    if suggestions:
        return " Hint: try to " + " or ".join(suggestions[:2])
    return ""


@dataclass
class QuantumNumberViolation:
    """Represents a quantum number conservation violation."""
    quantum_number: str
    vertex_index: int
    incoming_total: float
    outgoing_total: float
    hint: str = ""

    def __str__(self) -> str:
        base_msg = (
            f"{self.quantum_number} not conserved: "
            f"incoming={self.incoming_total:.2f}, outgoing={self.outgoing_total:.2f}"
        )
        if self.hint:
            return base_msg + "." + self.hint
        return base_msg


def validate_quantum_numbers(
    diagram,
    strict: bool = False,
    tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Validate quantum number conservation for a diagram.

    Args:
        diagram: Diagram object
        strict: If True, raise error on violation. If False, return warnings.
        tolerance: Numerical tolerance for floating point comparisons

    Returns:
        (is_valid, list_of_warnings)

    Algorithm:
    1. Infer missing quantum numbers from particle labels
    2. Check global conservation (initial → final)
    3. Report violations with clear messages

    Note: For now, we only validate global conservation (initial vs final).
    Future: Vertex-level validation requires diagram topology mapping.
    """
    warnings = []
    violations = []

    # Step 1: Infer missing quantum numbers
    initial_particles = [infer_quantum_numbers(p) for p in diagram.initial]
    final_particles = [infer_quantum_numbers(p) for p in diagram.final]

    # Step 2: Check global conservation
    quantum_numbers = [
        "charge", "lepton_e", "lepton_mu", "lepton_tau", "baryon_number"
    ]

    for qn in quantum_numbers:
        # Calculate totals
        initial_total = sum(
            getattr(p, qn, 0.0) or 0.0 for p in initial_particles
        )
        final_total = sum(
            getattr(p, qn, 0.0) or 0.0 for p in final_particles
        )

        # Check conservation
        if abs(initial_total - final_total) > tolerance:
            diff = final_total - initial_total
            hint = _suggest_fixes(qn, final_particles, diff)
            violation = QuantumNumberViolation(
                quantum_number=qn,
                vertex_index=-1,  # Global violation (not vertex-specific)
                incoming_total=initial_total,
                outgoing_total=final_total,
                hint=hint
            )
            violations.append(violation)
            warnings.append(str(violation))

    # Step 3: Check if any particles have undefined quantum numbers
    all_particles = initial_particles + final_particles
    undefined_particles = []

    for i, p in enumerate(all_particles):
        if p.label and p.charge is None:
            state = "initial" if i < len(initial_particles) else "final"
            idx = i if state == "initial" else i - len(initial_particles)
            undefined_particles.append(f"{state} particle {idx} (label={p.label})")

    if undefined_particles:
        warnings.append(
            f"Quantum numbers not defined for: {', '.join(undefined_particles)}. "
            f"Cannot validate conservation for these particles. "
            f"Consider adding to particle database or specifying manually."
        )

    is_valid = len(violations) == 0

    if not is_valid and strict:
        raise ValueError(
            f"Quantum number conservation violated:\n" +
            "\n".join([str(v) for v in violations])
        )

    return (is_valid, warnings)
