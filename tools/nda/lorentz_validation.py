"""
# lorentz_validation.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Lorentz invariance validation for process structures.

Validates that vertex structures respect Lorentz invariance:
- Fermions must come in pairs at each vertex (spinor indices must contract)
- Only certain combinations of spins form Lorentz-invariant vertices

This prevents LLMs from constructing invalid diagrams like F-F-F vertices.
"""

from typing import Tuple, List, Set, FrozenSet
from collections import Counter


# Valid 3-point vertex spin combinations (as multisets)
# Each entry is a frozenset of (spin, count) tuples
VALID_3PT_VERTICES: Set[FrozenSet[Tuple[float, int]]] = {
    # S-S-S: Scalar cubic coupling (phi^3)
    frozenset([(0.0, 3)]),

    # S-F-F: Yukawa coupling (scalar + 2 fermions)
    frozenset([(0.0, 1), (0.5, 2)]),

    # S-V-V: Scalar-Vector-Vector (Higgs to gauge bosons)
    frozenset([(0.0, 1), (1.0, 2)]),

    # V-F-F: Gauge coupling (vector + 2 fermions)
    frozenset([(1.0, 1), (0.5, 2)]),

    # V-V-V: Non-abelian gauge triple vertex
    frozenset([(1.0, 3)]),

    # S-S-V: Scalar charged current (for charged scalars)
    frozenset([(0.0, 2), (1.0, 1)]),
}

# Valid 4-point vertex spin combinations
VALID_4PT_VERTICES: Set[FrozenSet[Tuple[float, int]]] = {
    # S-S-S-S: Scalar quartic (phi^4, Higgs potential)
    frozenset([(0.0, 4)]),

    # V-V-V-V: Non-abelian gauge quartic
    frozenset([(1.0, 4)]),

    # F-F-F-F: 4-fermion operator (effective theory)
    frozenset([(0.5, 4)]),

    # S-S-V-V: Scalar-gauge quartic
    frozenset([(0.0, 2), (1.0, 2)]),
}


def _spins_to_multiset(spins: List[float]) -> FrozenSet[Tuple[float, int]]:
    """Convert list of spins to a multiset representation."""
    counts = Counter(spins)
    return frozenset(counts.items())


def validate_vertex_spins(spins: List[float]) -> Tuple[bool, str]:
    """
    Validate that a vertex with given particle spins is Lorentz-invariant.

    The key constraint is that fermions (spin-1/2) must come in pairs
    to allow spinor index contraction.

    Args:
        spins: List of spin values for particles at the vertex

    Returns:
        (is_valid, error_message)

    Examples:
        >>> validate_vertex_spins([0, 0.5, 0.5])  # S-F-F Yukawa
        (True, "")

        >>> validate_vertex_spins([0.5, 0.5, 0.5])  # F-F-F invalid
        (False, "Fermion number at vertex is odd (3). Fermions must...")
    """
    n_fermions = sum(1 for s in spins if s == 0.5)

    # Fundamental constraint: fermions must come in pairs
    if n_fermions % 2 != 0:
        return False, (
            f"Fermion number at vertex is odd ({n_fermions}). "
            f"Fermions must come in pairs for Lorentz-invariant spinor contractions. "
            f"Spins at vertex: {spins}"
        )

    # Check against known valid vertices
    multiset = _spins_to_multiset(spins)
    n_particles = len(spins)

    if n_particles == 3:
        if multiset not in VALID_3PT_VERTICES:
            spin_str = _format_spin_combo(spins)
            valid_str = _format_valid_3pt()
            return False, (
                f"Invalid 3-point vertex: {spin_str}. "
                f"Valid 3-point vertices in QFT: {valid_str}"
            )
    elif n_particles == 4:
        if multiset not in VALID_4PT_VERTICES:
            spin_str = _format_spin_combo(spins)
            valid_str = _format_valid_4pt()
            return False, (
                f"Invalid 4-point vertex: {spin_str}. "
                f"Valid 4-point vertices: {valid_str}"
            )
    elif n_particles < 3:
        return False, (
            f"Vertex has only {n_particles} particles. "
            f"Minimum is 3 for a valid interaction vertex."
        )
    else:
        # Higher-point vertices: just check fermion pairing
        # (These are typically effective operators)
        pass

    return True, ""


def _format_spin_combo(spins: List[float]) -> str:
    """Format spin combination as human-readable string."""
    SPIN_NAMES = {0.0: "S", 0.5: "F", 1.0: "V", 2.0: "T"}
    counts = Counter(spins)
    parts = []
    for spin in sorted(counts.keys()):
        name = SPIN_NAMES.get(spin, f"spin-{spin}")
        count = counts[spin]
        if count > 1:
            parts.append(f"{count}x{name}")
        else:
            parts.append(name)
    return "-".join(parts)


def _format_valid_3pt() -> str:
    """Format valid 3-point vertices."""
    SPIN_NAMES = {0.0: "S", 0.5: "F", 1.0: "V", 2.0: "T"}
    results = []
    for combo in VALID_3PT_VERTICES:
        parts = []
        for spin, count in sorted(combo):
            name = SPIN_NAMES.get(spin, f"?")
            parts.extend([name] * count)
        results.append("-".join(parts))
    return ", ".join(sorted(results))


def _format_valid_4pt() -> str:
    """Format valid 4-point vertices."""
    SPIN_NAMES = {0.0: "S", 0.5: "F", 1.0: "V", 2.0: "T"}
    results = []
    for combo in VALID_4PT_VERTICES:
        parts = []
        for spin, count in sorted(combo):
            name = SPIN_NAMES.get(spin, f"?")
            parts.extend([name] * count)
        results.append("-".join(parts))
    return ", ".join(sorted(results))


def validate_process_lorentz(
    initial_spin: float,
    final_spins: List[float],
    propagator_spins: List[float] = None
) -> Tuple[bool, str]:
    """
    Validate Lorentz invariance of a process structure.

    This validates the overall process, inferring vertex structure from
    the particle content and checking each vertex.

    Args:
        initial_spin: Spin of initial state particle
        final_spins: List of final state particle spins
        propagator_spins: List of propagator spins (optional)

    Returns:
        (is_valid, error_message)

    Examples:
        >>> validate_process_lorentz(0, [0.5, 0.5])  # H -> FF
        (True, "")

        >>> validate_process_lorentz(0.5, [0.5, 0.5, 0.5])  # F -> FFF
        (False, "Fermion number...")
    """
    propagator_spins = propagator_spins or []

    # No propagators: single vertex decay
    if not propagator_spins:
        vertex_spins = [initial_spin] + final_spins
        return validate_vertex_spins(vertex_spins)

    # With propagators: check each vertex separately
    # Vertex 1: initial + propagator
    # Vertex 2: propagator + final states
    # (This is simplified - real diagrams can be more complex)

    # For single propagator case:
    if len(propagator_spins) == 1:
        prop_spin = propagator_spins[0]

        # Simplified validation: check total fermion count
        all_spins = [initial_spin] + final_spins + propagator_spins * 2  # prop appears twice

        # Total fermion lines (external) must be even
        external_fermions = sum(1 for s in [initial_spin] + final_spins if s == 0.5)
        if external_fermions % 2 != 0:
            return False, (
                f"External fermion count is odd ({external_fermions}). "
                f"Fermions must come in pairs for a valid amplitude. "
                f"Initial: {initial_spin}, Final: {final_spins}"
            )

    else:
        # Multiple propagators: just check external fermion count
        external_fermions = sum(1 for s in [initial_spin] + final_spins if s == 0.5)
        if external_fermions % 2 != 0:
            return False, (
                f"External fermion count is odd ({external_fermions}). "
                f"Fermions must come in pairs."
            )

    return True, ""
