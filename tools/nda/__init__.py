"""
# __init__.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Naive Dimensional Analysis (NDA) tools for decay width estimation.

This module provides order-of-magnitude estimates for decay widths using
dimensional analysis and simple diagram specifications.
"""

from .nda_tool import EstimateDecayWidthNDATool
from .nda_formula_tool import EstimateDecayWidthFormulaNDATool
from .branching_ratio_tool import EstimateBranchingRatioNDATool
from .phase_space import EstimatePhaseSpaceTool
from .compare_phase_space import ComparePhaseSpaceTool
from .matrix_element import EstimateMatrixElementTool
from .topology import (
    validate_graph_theory_constraint,
    validate_topology,
    calculate_loop_number,
    TOPOLOGIES
)
from .simple_diagram import (
    Diagram,
    parse_diagram,
    Particle,
    Vertex,
    Propagator,
)
from .symbolic_diagram import (
    SymbolicDiagram,
    SymbolicParticle,
    SymbolicVertex,
    SymbolicPropagator,
    parse_symbolic_diagram,
)
from .diagram_resolution import resolve_diagram
from .particle_database import (
    get_particle_data,
    infer_quantum_numbers,
    SM_PARTICLES,
)
from .quantum_validation import (
    validate_quantum_numbers,
    QuantumNumberViolation,
)
from .summary_formatting import (
    format_decay_width_summary,
    format_multi_diagram_summary,
    format_cross_section_summary,
)
from .lorentz_validation import (
    validate_vertex_spins,
    validate_process_lorentz,
    VALID_3PT_VERTICES,
    VALID_4PT_VERTICES,
)
from .output_enrichment import (
    enrich_nda_output,
    REFERENCE_DECAYS,
    LIFETIME_CONTEXT,
)

__all__ = [
    "EstimateDecayWidthNDATool",
    "EstimateDecayWidthFormulaNDATool",
    "EstimateBranchingRatioNDATool",
    "EstimatePhaseSpaceTool",
    "ComparePhaseSpaceTool",
    "EstimateMatrixElementTool",
    "validate_graph_theory_constraint",
    "validate_topology",
    "calculate_loop_number",
    "TOPOLOGIES",
    "Diagram",
    "parse_diagram",
    "Particle",
    "Vertex",
    "Propagator",
    # Symbolic diagram
    "SymbolicDiagram",
    "SymbolicParticle",
    "SymbolicVertex",
    "SymbolicPropagator",
    "parse_symbolic_diagram",
    "resolve_diagram",
    "get_particle_data",
    "infer_quantum_numbers",
    "SM_PARTICLES",
    "validate_quantum_numbers",
    "QuantumNumberViolation",
    # Summary formatting
    "format_decay_width_summary",
    "format_multi_diagram_summary",
    "format_cross_section_summary",
    # Lorentz validation
    "validate_vertex_spins",
    "validate_process_lorentz",
    "VALID_3PT_VERTICES",
    "VALID_4PT_VERTICES",
    # Output enrichment
    "enrich_nda_output",
    "REFERENCE_DECAYS",
    "LIFETIME_CONTEXT",
]
