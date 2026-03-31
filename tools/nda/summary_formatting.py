"""
# summary_formatting.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Summary formatting utilities for NDA estimates.

Provides formatted output for decay width (and future cross-section) estimates,
designed to be useful for both human readers and LLM agent assistants.
"""

from typing import Dict, Any, Optional, List, Callable, Union


def format_value(value: float, precision: int = 2) -> str:
    """Format a numerical value in scientific notation."""
    if value == 0:
        return "0"
    return f"{value:.{precision}e}"


def format_decay_width_summary(
    nda_result: Dict[str, Any],
    process_label: Optional[str] = None,
    reference_width: Optional[float] = None,
    reference_label: str = "Experimental",
    include_breakdown: bool = True,
    output_format: str = "markdown"
) -> str:
    """
    Format NDA decay width result as a comprehensive summary.

    This produces output optimized for agent assistants and notebook display,
    showing the full breakdown of phase space, matrix element, and propagator
    contributions along with the final estimates.

    Args:
        nda_result: Result dictionary from EstimateDecayWidthNDATool
        process_label: Optional label for the process (e.g., "μ⁻ → e⁻ ν̄ₑ νμ")
        reference_width: Optional reference value for comparison (e.g., experimental)
        reference_label: Label for the reference value
        include_breakdown: Whether to include the component breakdown table
        output_format: "markdown" or "text"

    Returns:
        Formatted summary string
    """
    if nda_result.get("status") != "ok":
        return f"Error: {nda_result.get('error', 'Unknown error')}"

    lines = []

    # Header
    if process_label:
        lines.append(f"### NDA Estimate: {process_label}")
    else:
        lines.append("### NDA Decay Width Estimate")
    lines.append("")

    # Diagram properties
    diagram_info = nda_result.get("diagram", {})
    if diagram_info:
        lines.append("**Diagram Properties:**")
        lines.append(f"- Topology: `{diagram_info.get('topology', 'unknown')}`")
        lines.append(f"- Vertices: {diagram_info.get('n_vertices', '?')}")
        lines.append(f"- Propagators: {diagram_info.get('n_propagators', '?')}")
        if diagram_info.get('loop_order', 0) > 0:
            lines.append(f"- Loop order: {diagram_info['loop_order']}")
        interactions = diagram_info.get('interactions', [])
        if interactions:
            lines.append(f"- Interactions: {', '.join(interactions)}")
        lines.append("")

    # Component breakdown table
    breakdown = nda_result.get("breakdown", {})
    if include_breakdown and breakdown:
        lines.append("**Component Breakdown:**")
        lines.append("")
        lines.append("| Component | Formula | Numerical Value |")
        lines.append("|:----------|:--------|----------------:|")

        # Phase space
        ps = breakdown.get("phase_space", {})
        if ps:
            ps_formula = ps.get("formula", "-")
            ps_value = format_value(ps.get("value", 0))
            lines.append(f"| Phase Space (Φₙ) | ${ps_formula}$ | {ps_value} |")

        # Matrix element
        me = breakdown.get("matrix_element", {})
        if me:
            me_formula = me.get("formula", "-")
            me_value = format_value(me.get("value", 0))
            lines.append(f"| Matrix Element |M|² | ${me_formula}$ | {me_value} |")

        # Propagators
        props = breakdown.get("propagators", {})
        if props and props.get("count", 0) > 0:
            prop_formula = props.get("formula", "-")
            prop_value = format_value(props.get("value", 0))
            prop_count = props.get("count", 0)
            regimes = props.get("regimes", [])
            regime_str = f" ({', '.join(regimes[:2])})" if regimes else ""
            lines.append(f"| Propagators ({prop_count}){regime_str} | ${prop_formula}$ | {prop_value} |")

        # Loop factors
        loops = breakdown.get("loops", {})
        if loops:
            loop_formula = loops.get("formula", "-")
            loop_value = format_value(loops.get("value", 0))
            lines.append(f"| Loop Factor | ${loop_formula}$ | {loop_value} |")

        lines.append("")

    # Results table
    lines.append("**Results:**")
    lines.append("")
    lines.append("| Estimate | Width (GeV) | Notes |")
    lines.append("|:---------|------------:|:------|")

    # NDA estimate
    width_nda = nda_result.get("width_gev", 0)
    formula = nda_result.get("formula", "-")
    lines.append(f"| NDA (naive) | {format_value(width_nda)} | ${formula}$ |")

    # Improved estimate
    improved = nda_result.get("improved_estimate", {})
    if improved:
        width_improved = improved.get("width_gev", 0)
        method = improved.get("method", "arXiv:1402.1178")
        ratio_to_nda = improved.get("ratio_to_nda", 0)
        ratio_str = f" ({ratio_to_nda:.2f}× NDA)" if ratio_to_nda else ""
        lines.append(f"| Improved | {format_value(width_improved)} | {method}{ratio_str} |")

    # Reference value (e.g., experimental)
    if reference_width is not None:
        lines.append(f"| {reference_label} | {format_value(reference_width)} | Reference value |")

    lines.append("")

    # Comparison ratios
    if reference_width is not None and reference_width > 0:
        lines.append("**Comparison:**")
        ratio_nda = width_nda / reference_width
        lines.append(f"- NDA / {reference_label}: {ratio_nda:.1f}×")
        if improved:
            width_improved = improved.get("width_gev", 0)
            if width_improved > 0:
                ratio_improved = width_improved / reference_width
                lines.append(f"- Improved / {reference_label}: {ratio_improved:.2f}×")
        lines.append("")

    # Warnings
    warnings = nda_result.get("warnings", [])
    if warnings:
        lines.append("**Warnings:**")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def format_multi_diagram_summary(
    results: List[Dict[str, Any]],
    process_label: str,
    reference_width: float,
    couplings_fn: Optional[Callable[[Dict], str]] = None,
    include_formula: bool = True,
    include_physics_note: bool = True
) -> str:
    """
    Format multiple NDA results (e.g., different diagram classes) as a summary table.

    Produces tables like:

    | Heavy Props | Diagrams | Couplings | NDA Width | BR | NDA Formula |

    Args:
        results: List of result dictionaries with fields:
            - n_heavy: Number of heavy propagators
            - n_diagrams: Number of diagrams in this class
            - width_nda or width_gev: NDA width estimate
            - formula: NDA formula string
            - couplings_latex: LaTeX string for couplings (optional, or use couplings_fn)
        process_label: Label for the process (e.g., "mu -> 3e 2nu")
        reference_width: Reference total width for BR calculation (in GeV)
        couplings_fn: Optional function to extract coupling latex from result dict
        include_formula: Whether to include the NDA formula column
        include_physics_note: Whether to include physics interpretation note

    Returns:
        Formatted markdown string ready for display
    """
    if not results:
        return "No results to display."

    lines = []
    lines.append(f"**NDA Summary:** {process_label}")
    lines.append("")

    # Build header
    if include_formula:
        header = "| Heavy Props | Diagrams | Couplings | Width/Diagram | BR | NDA Formula |"
        align =  "|:-----------:|:--------:|:---------:|:-------------:|:------:|:------------|"
    else:
        header = "| Heavy Props | Diagrams | Couplings | Width/Diagram | BR |"
        align =  "|:-----------:|:--------:|:---------:|:-------------:|:------:|"

    lines.append(header)
    lines.append(align)

    # Sort results by n_heavy
    sorted_results = sorted(results, key=lambda r: (r.get("n_heavy", 0), r.get("n_vertices", 0)))

    # Track totals
    total_width_nda = 0
    total_diagrams = 0

    for r in sorted_results:
        n_heavy = r.get("n_heavy", "?")
        n_diagrams = r.get("n_diagrams", 1)

        # Get coupling latex
        if couplings_fn is not None:
            couplings = couplings_fn(r)
        else:
            couplings = r.get("couplings_latex", "-")

        # Get widths - support current and legacy field names
        width_nda = r.get("width_per_diagram", r.get("width_nda", r.get("width_gev", 0)))
        formula = r.get("formula", "-")

        # Calculate BR
        br_nda = width_nda / reference_width if reference_width > 0 else 0

        # Update totals (width × n_diagrams for incoherent sum)
        total_width_nda += width_nda * n_diagrams
        total_diagrams += n_diagrams

        # Format values
        width_nda_str = f"{width_nda:.2e}"
        br_nda_str = f"{br_nda:.2e}"
        formula_latex = f"${formula}$" if formula and formula != "-" else "-"

        if include_formula:
            lines.append(
                f"| {n_heavy} | {n_diagrams} | {couplings} | {width_nda_str} | "
                f"{br_nda_str} | {formula_latex} |"
            )
        else:
            lines.append(
                f"| {n_heavy} | {n_diagrams} | {couplings} | {width_nda_str} | "
                f"{br_nda_str} |"
            )

    # Total row
    total_br_nda = total_width_nda / reference_width if reference_width > 0 else 0

    total_width_nda_str = f"**{total_width_nda:.2e}**"
    total_br_nda_str = f"**{total_br_nda:.2e}**"

    if include_formula:
        lines.append(
            f"| **Total** | **{total_diagrams}** | - | {total_width_nda_str} | "
            f"{total_br_nda_str} | - |"
        )
    else:
        lines.append(
            f"| **Total** | **{total_diagrams}** | - | {total_width_nda_str} | "
            f"{total_br_nda_str} |"
        )

    lines.append("")

    # Summary statistics
    lines.append(f"Total NDA branching ratio: {total_br_nda:.2e}")
    lines.append(f"Based on {total_diagrams} diagrams")

    # Physics note
    if include_physics_note and len(sorted_results) >= 2:
        first_width = sorted_results[0].get("width_per_diagram", sorted_results[0].get("width_nda", sorted_results[0].get("width_gev", 1)))
        last_width = sorted_results[-1].get("width_per_diagram", sorted_results[-1].get("width_nda", sorted_results[-1].get("width_gev", 1)))
        if last_width > 0 and first_width > 0:
            ratio = first_width / last_width
            lines.append(f"\nPhysics note: Fewest-propagator diagrams dominate by ~{ratio:.0e}x")

    return "\n".join(lines)


def format_cross_section_summary(
    nda_result: Dict[str, Any],
    process_label: Optional[str] = None,
    sqrt_s: Optional[float] = None,
    reference_xsec: Optional[float] = None,
    reference_label: str = "Reference",
    include_breakdown: bool = True
) -> str:
    """
    Format NDA cross-section result as a comprehensive summary.

    Placeholder for future EstimateCrossSectionTool integration.
    The structure mirrors format_decay_width_summary but with appropriate
    labels and units for cross-sections.

    Args:
        nda_result: Result dictionary from EstimateCrossSectionTool (future)
        process_label: Optional label for the process (e.g., "pp → tt̄")
        sqrt_s: Center-of-mass energy in GeV
        reference_xsec: Optional reference cross-section for comparison
        reference_label: Label for the reference value
        include_breakdown: Whether to include the component breakdown table

    Returns:
        Formatted summary string
    """
    # TODO: Implement when EstimateCrossSectionTool is created
    # The structure will be similar to format_decay_width_summary but with:
    # - Cross-section units (fb, pb, etc.)
    # - Initial state flux factor instead of 1/(2M)
    # - Parton luminosity information if applicable

    lines = []
    lines.append("### NDA Cross-Section Estimate")
    lines.append("")
    lines.append("*Cross-section formatting not yet implemented.*")
    lines.append("*This will be added when EstimateCrossSectionTool is created.*")
    lines.append("")

    return "\n".join(lines)
