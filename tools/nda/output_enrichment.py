"""
# output_enrichment.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Output enrichment for NDA results.

Adds comparisons, scaling information, and flags to NDA results
to help researchers understand the physics context of their estimates.
"""

from typing import Dict, Any, List, Optional
import math


# Reference decays for comparison (width in GeV, lifetime in seconds)
REFERENCE_DECAYS = {
    "H -> bb": {
        "width_gev": 2.4e-3,
        "lifetime_s": 2.7e-22,
        "description": "Higgs to bottom quarks (SM)",
    },
    "H -> gamma gamma": {
        "width_gev": 9.4e-6,
        "lifetime_s": 7.0e-20,
        "description": "Higgs to photons (loop-induced)",
    },
    "mu -> e nu nu": {
        "width_gev": 3.0e-19,
        "lifetime_s": 2.2e-6,
        "description": "Muon decay",
    },
    "tau -> mu nu nu": {
        "width_gev": 2.3e-12,
        "lifetime_s": 2.9e-13,
        "description": "Tau to muon decay",
    },
    "Z -> e+ e-": {
        "width_gev": 8.4e-2,
        "lifetime_s": 7.8e-24,
        "description": "Z boson to electrons",
    },
    "W -> e nu": {
        "width_gev": 2.3e-1,
        "lifetime_s": 2.9e-24,
        "description": "W boson to electron",
    },
    "pi+ -> mu nu": {
        "width_gev": 2.5e-17,
        "lifetime_s": 2.6e-8,
        "description": "Charged pion decay",
    },
    "neutron -> p e nu": {
        "width_gev": 7.5e-28,
        "lifetime_s": 879,
        "description": "Neutron beta decay",
    },
}

# Lifetime categories for context
LIFETIME_CONTEXT = {
    "prompt": "Decays at the interaction vertex, unresolvable as a track.",
    "short": "Decays within mm-cm of vertex. May form a displaced vertex.",
    "medium": "Decays over meters. Forms a track in detector.",
    "long": "Decays over long distances. May escape detector.",
    "stable": "Effectively stable on detector timescales.",
}


def enrich_nda_output(
    result: Dict[str, Any],
    diagram: Any,
    coupling: float,
    color_factor: float
) -> Dict[str, Any]:
    """
    Enrich NDA output with comparisons, scaling, and flags.

    This function adds context that helps researchers interpret NDA results:
    - Comparisons to known SM decays
    - Scaling behavior with parameters
    - Flags for unusual or potentially problematic results
    - Assumptions made in the calculation

    Args:
        result: Base NDA result dictionary
        diagram: Diagram object (tools.nda.simple_diagram.Diagram)
        coupling: Coupling value used
        color_factor: Color factor used

    Returns:
        Enriched result dictionary
    """
    width_gev = result.get("width_gev", 0)
    lifetime_s = result.get("lifetime_s", float('inf'))

    # Add comparisons to reference decays
    result["comparisons"] = _generate_comparisons(width_gev, lifetime_s)

    # Add scaling information
    result["scaling"] = _generate_scaling_info(diagram, coupling, color_factor)

    # Add assumptions
    result["assumptions"] = _generate_assumptions(diagram, result)

    # Add flags for anomalies
    result["flags"] = _generate_flags(result, diagram, coupling)

    # Add lifetime context
    category = result.get("lifetime_category", "unknown")
    if category in LIFETIME_CONTEXT:
        result["lifetime_context"] = LIFETIME_CONTEXT[category]

    # Add related processes
    result["related_processes"] = _suggest_related_processes(diagram)

    return result


def _generate_comparisons(width_gev: float, lifetime_s: float) -> List[Dict[str, Any]]:
    """Generate comparisons to reference decays."""
    comparisons = []

    for name, ref in REFERENCE_DECAYS.items():
        ref_width = ref["width_gev"]
        ratio = width_gev / ref_width if ref_width > 0 else float('inf')

        # Only include comparisons within 10 orders of magnitude
        if 1e-10 < ratio < 1e10:
            comparison = {
                "reference": name,
                "ratio": ratio,
                "description": ref["description"],
            }

            # Add human-readable comparison
            if ratio > 10:
                comparison["relation"] = f"~{ratio:.0f}x larger than {name}"
            elif ratio > 1:
                comparison["relation"] = f"~{ratio:.1f}x larger than {name}"
            elif ratio > 0.1:
                comparison["relation"] = f"~{ratio:.1f}x (comparable to {name})"
            else:
                comparison["relation"] = f"~{1/ratio:.0f}x smaller than {name}"

            comparisons.append(comparison)

    # Sort by ratio closest to 1
    comparisons.sort(key=lambda x: abs(math.log10(x["ratio"])) if x["ratio"] > 0 else float('inf'))

    return comparisons[:3]  # Top 3 most relevant comparisons


def _generate_scaling_info(diagram: Any, coupling: float, color_factor: float) -> Dict[str, Any]:
    """Generate scaling information with parameters."""
    n_body = len(diagram.final)
    mother_mass = diagram.initial[0].mass
    n_vertices = len(diagram.vertices)
    n_loops = sum(1 for p in diagram.propagators if getattr(p, 'is_loop_propagator', False))

    scaling = {
        "with_coupling": f"Gamma ~ g^{2 * n_vertices}",
        "with_mass": f"Gamma ~ M^{2*n_body - 3}" if n_body > 2 else "Gamma ~ M",
    }

    # Add sensitivity analysis
    scaling["sensitivity"] = []

    # Coupling sensitivity
    coupling_power = 2 * n_vertices
    scaling["sensitivity"].append({
        "parameter": "coupling",
        "current_value": coupling,
        "effect": f"Doubling coupling increases width by factor {2**coupling_power:.1f}",
    })

    # Mass sensitivity
    mass_power = 2 * n_body - 3 if n_body > 2 else 1
    scaling["sensitivity"].append({
        "parameter": "mother_mass",
        "current_value": mother_mass,
        "effect": f"Doubling mass changes width by factor {2**mass_power:.1f}",
    })

    # Propagator mass sensitivity (if applicable)
    for i, prop in enumerate(diagram.propagators):
        if prop.mass > 0:
            scaling["sensitivity"].append({
                "parameter": f"propagator_{i}_mass",
                "current_value": prop.mass,
                "effect": "Doubling propagator mass decreases width by factor ~4",
            })

    return scaling


def _generate_assumptions(diagram: Any, result: Dict[str, Any]) -> List[str]:
    """Generate list of assumptions made in the calculation."""
    assumptions = []

    # Phase space assumptions
    n_body = len(diagram.final)
    final_masses = [p.mass for p in diagram.final]
    mother_mass = diagram.initial[0].mass

    if all(m == 0 or m is None for m in final_masses):
        assumptions.append("Massless final state approximation used for phase space")
    elif mother_mass and sum(m or 0 for m in final_masses) < 0.1 * mother_mass:
        assumptions.append("Final state masses are small compared to mother mass")
    else:
        assumptions.append("Near-threshold effects may modify the estimate")

    # Matrix element assumptions
    operator_dim = result.get("process_info", {}).get("operator_dimension", 4)
    if operator_dim == 4:
        assumptions.append("Renormalizable interaction assumed")
    else:
        assumptions.append(f"Effective operator (dimension-{operator_dim}) assumed")

    # Loop assumptions
    n_loops = sum(1 for p in diagram.propagators if getattr(p, 'is_loop_propagator', False))
    if n_loops > 0:
        assumptions.append(f"Loop factor 1/(16pi^2)^{n_loops} applied")
        assumptions.append("No numerical loop integral - pure NDA estimate")

    # Spin assumptions
    assumptions.append("Spin averaging/summing applied (unpolarized)")

    return assumptions


def _generate_flags(
    result: Dict[str, Any],
    diagram: Any,
    coupling: float
) -> List[Dict[str, str]]:
    """Generate flags for anomalies or potential issues."""
    flags = []

    width_gev = result.get("width_gev", 0)
    mother_mass = diagram.initial[0].mass

    # Flag 1: Very large coupling
    if coupling > 1:
        flags.append({
            "type": "warning",
            "flag": "large_coupling",
            "message": f"Coupling ({coupling}) > 1 may indicate perturbation theory breakdown",
        })

    # Flag 2: Very wide particle
    if mother_mass and width_gev > 0.1 * mother_mass:
        flags.append({
            "type": "warning",
            "flag": "wide_resonance",
            "message": f"Width/Mass ratio ({width_gev/mother_mass:.2f}) > 10%, narrow-width approximation may fail",
        })

    # Flag 3: Heavy propagator suppression
    if mother_mass:
        for prop in diagram.propagators:
            if prop.mass > 10 * mother_mass:
                flags.append({
                    "type": "info",
                    "flag": "heavy_propagator",
                    "message": f"Heavy propagator (M={prop.mass} GeV >> E={mother_mass} GeV) - strong suppression",
                })

    # Flag 4: Near threshold
    if mother_mass:
        final_mass_sum = sum(p.mass or 0 for p in diagram.final)
        if final_mass_sum > 0.8 * mother_mass:
            flags.append({
                "type": "warning",
                "flag": "near_threshold",
                "message": f"Near kinematic threshold - phase space suppression significant",
            })

    # Flag 5: Loop without NLO
    n_loops = sum(1 for p in diagram.propagators if getattr(p, 'is_loop_propagator', False))
    if n_loops > 0:
        flags.append({
            "type": "info",
            "flag": "loop_estimate",
            "message": "Loop diagram estimated via NDA - actual loop integral may differ by O(1) factors",
        })

    # Flag 6: Extremely long or short lifetime
    lifetime_s = result.get("lifetime_s", 0)
    if lifetime_s > 1e15:
        flags.append({
            "type": "info",
            "flag": "extremely_stable",
            "message": "Lifetime exceeds age of universe - effectively stable",
        })
    elif lifetime_s < 1e-30:
        flags.append({
            "type": "info",
            "flag": "extremely_short",
            "message": "Extremely short lifetime - check for phase space or coupling suppression",
        })

    return flags


def _suggest_related_processes(diagram: Any) -> List[str]:
    """Suggest related processes the user might want to explore."""
    suggestions = []

    initial_spin = diagram.initial[0].spin
    n_final = len(diagram.final)
    has_loop = any(getattr(p, 'is_loop_propagator', False) for p in diagram.propagators)
    has_propagator = len(diagram.propagators) > 0

    # Suggest loop version if tree-level
    if not has_loop and n_final == 2:
        suggestions.append("Consider loop-induced version: add {F(m)} or {V(m)} propagator")

    # Suggest different final states
    if n_final == 2:
        suggestions.append("Compare with 3-body decay: add another final state particle")

    # Suggest different propagators
    if has_propagator and not has_loop:
        suggestions.append("Compare Fermi theory: remove propagator for effective vertex")

    # Suggest radiative corrections
    if initial_spin == 0:
        suggestions.append("Consider radiative decay: S(M) -> V(0) V(0)")

    return suggestions[:3]  # Top 3 suggestions
