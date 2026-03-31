"""
# __init__.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

FeynGraph integration for automatic Feynman diagram enumeration.

This module provides a HEPTAPOD interface to FeynGraph, a modern Rust-based
library for automatic generation of all topologically distinct Feynman diagrams
for a given process.

Key Features:
  - Automatic diagram enumeration for Standard Model processes
  - UFO model support for BSM physics
  - Conversion to HEPTAPOD Diagram format for NDA analysis
  - Physics-based ranking (NDA estimates + coupling power counting)
  - ~10^5 diagrams/second performance (Rust backend)

Main Components:
  - FeynGraphInterface: Wrapper for FeynGraph API
  - DiagramConverter: Convert FeynGraph diagrams to Diagram objects
  - DiagramRanker: Rank by NDA estimates and physics importance
  - EnumerateDiagramsTool: Orchestral BaseTool for LLM agents

Usage:
  See tools/feyngraph/docs/FEYNGRAPH_INTEGRATION_DESIGN.md for full documentation.
"""

from .model_mapping import (
    nda_to_feyngraph_label,
    feyngraph_to_nda_label,
    get_sm_coupling,
    get_particle_mass,
    SM_COUPLINGS,
    PARTICLE_LABEL_MAP
)

from .feyngraph_interface import (
    FeynGraphInterface,
    enumerate_sm_diagrams
)

from .diagram_converter import (
    DiagramConverter,
    convert_feyngraph_diagram,
    ConversionInfo
)

from .ranking import (
    DiagramRanker,
    rank_diagrams,
    RankedDiagram,
    RankingInfo
)

from .enumerate_and_rank import (
    enumerate_and_rank_diagrams,
    enumerate_and_rank_diagrams_simple,
    EnumerationResult,
    enumerate_simple
)

from .visualization import (
    draw_diagram_svg,
    draw_diagrams_svg,
    draw_diagram_tikz,
    save_diagram,
    display_diagram_inline
)

from .enumerate_tool import EnumerateDiagramsTool
from .visualize_tool import VisualizeDiagramsTool

__all__ = [
    # Model mapping
    "nda_to_feyngraph_label",
    "feyngraph_to_nda_label",
    "get_sm_coupling",
    "get_particle_mass",
    "SM_COUPLINGS",
    "PARTICLE_LABEL_MAP",

    # FeynGraph interface
    "FeynGraphInterface",
    "enumerate_sm_diagrams",

    # Diagram conversion
    "DiagramConverter",
    "convert_feyngraph_diagram",
    "ConversionInfo",

    # Ranking
    "DiagramRanker",
    "rank_diagrams",
    "RankedDiagram",
    "RankingInfo",

    # High-level enumeration and ranking
    "enumerate_and_rank_diagrams",
    "enumerate_and_rank_diagrams_simple",
    "EnumerationResult",
    "enumerate_simple",

    # Visualization
    "draw_diagram_svg",
    "draw_diagrams_svg",
    "draw_diagram_tikz",
    "save_diagram",
    "display_diagram_inline",

    # Agent-facing tools
    "EnumerateDiagramsTool",
    "VisualizeDiagramsTool",
]
