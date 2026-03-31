"""
# feyngraph_interface.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

FeynGraph API wrapper for HEPTAPOD integration.

This module provides a clean interface to the FeynGraph library for
automatic Feynman diagram enumeration.
"""

from typing import List, Optional, Any, Dict
import os

try:
    from .model_mapping import nda_to_feyngraph_label, feyngraph_to_nda_label
except ImportError:
    from model_mapping import nda_to_feyngraph_label, feyngraph_to_nda_label


def _require_feyngraph() -> Any:
    """
    Ensure feyngraph is available, or raise ImportError.

    Returns:
        feyngraph module

    Raises:
        ImportError: If feyngraph is not installed with helpful message
    """
    try:
        import feyngraph
        return feyngraph
    except ImportError as e:
        raise ImportError(
            "FeynGraph is not installed. This module requires FeynGraph for "
            "automatic diagram enumeration.\n\n"
            "Install with:\n"
            "  pip install feyngraph\n\n"
            "Or add to requirements.txt:\n"
            "  feyngraph>=0.1.0\n\n"
            "Note: Manual Diagram specification does not require FeynGraph."
        ) from e


class FeynGraphInterface:
    """
    Wrapper for FeynGraph library to integrate with HEPTAPOD.

    This class provides a clean interface to FeynGraph for automatic
    Feynman diagram enumeration, handling particle label mappings and
    model loading.

    Attributes:
        model: Model name ("SM") or path to UFO model directory
        feyngraph: FeynGraph module (lazily loaded)
    """

    def __init__(self, model: str = "SM"):
        """
        Initialize FeynGraph interface.

        Args:
            model: Model to use. Options:
                  - "SM" (default): Standard Model (built-in)
                  - "/path/to/model_UFO": Path to UFO model directory

        Raises:
            ImportError: If FeynGraph is not installed
            ValueError: If model file not found
        """
        self.model = model
        self.feyngraph = None  # Lazy loading
        self._model_obj = None

    def _ensure_loaded(self):
        """Lazy load FeynGraph module."""
        if self.feyngraph is None:
            self.feyngraph = _require_feyngraph()
            self._load_model()

    def _load_model(self):
        """
        Load the specified model.

        Raises:
            ValueError: If model file not found or invalid
        """
        if self.model == "SM":
            # Standard Model is built-in to FeynGraph
            # No explicit loading needed
            self._model_obj = "SM"
        else:
            # Path to UFO model
            if not os.path.exists(self.model):
                raise ValueError(
                    f"UFO model directory not found: {self.model}\n"
                    f"Specify 'SM' for Standard Model or provide valid path to UFO directory."
                )

            if not os.path.isdir(self.model):
                raise ValueError(
                    f"Model path must be a directory: {self.model}\n"
                    f"UFO models are directories containing particles.py, vertices.py, etc."
                )

            # Load UFO model (FeynGraph API will handle this)
            # Note: Actual FeynGraph API might differ, this is a placeholder
            # TODO: Update when FeynGraph UFO loading API is confirmed
            self._model_obj = self.model

    def enumerate_diagrams(
        self,
        initial_particles: List[str],
        final_particles: List[str],
        max_loop_order: int = 0,
        **kwargs
    ) -> List[Any]:
        """
        Generate all Feynman diagrams for the specified process.

        Args:
            initial_particles: Initial state particle labels (HEPTAPOD notation)
                             e.g., ["H"], ["mu-"], ["e+", "e-"]
            final_particles: Final state particle labels (HEPTAPOD notation)
                           e.g., ["b", "bbar"], ["e-", "gamma"]
            max_loop_order: Maximum loop order (0=tree, 1=1-loop, 2=2-loop)
            **kwargs: Additional arguments passed to FeynGraph

        Returns:
            List of FeynGraph diagram objects

        Raises:
            ImportError: If FeynGraph not installed
            ValueError: If particles invalid or model not loaded

        Examples:
            >>> interface = FeynGraphInterface("SM")
            >>> diagrams = interface.enumerate_diagrams(
            ...     initial_particles=["H"],
            ...     final_particles=["b", "bbar"],
            ...     max_loop_order=0
            ... )
            >>> len(diagrams)
            1  # One tree-level diagram for H → bb̄
        """
        self._ensure_loaded()

        # Map HEPTAPOD labels to FeynGraph notation
        try:
            fg_initial = [nda_to_feyngraph_label(p) for p in initial_particles]
            fg_final = [nda_to_feyngraph_label(p) for p in final_particles]
        except ValueError as e:
            raise ValueError(
                f"Invalid particle label in diagram specification: {e}\n"
                f"Initial: {initial_particles}\n"
                f"Final: {final_particles}"
            ) from e

        # Call FeynGraph API
        try:
            # Generate diagrams using FeynGraph
            diagram_container = self.feyngraph.generate_diagrams(
                fg_initial,
                fg_final,
                max_loop_order,
                **kwargs
            )

            # Convert DiagramContainer to list
            diagrams = [diagram_container[i] for i in range(len(diagram_container))]

            return diagrams

        except Exception as e:
            raise RuntimeError(
                f"FeynGraph diagram generation failed: {e}\n"
                f"Initial: {initial_particles} ({fg_initial})\n"
                f"Final: {final_particles} ({fg_final})\n"
                f"Loop order: {max_loop_order}"
            ) from e

    def get_diagram_info(self, diagram: Any) -> Dict[str, Any]:
        """
        Extract information from a FeynGraph diagram object.

        Args:
            diagram: FeynGraph diagram object

        Returns:
            Dictionary with diagram information:
              {
                "n_vertices": int,
                "n_propagators": int,
                "n_initial": int,
                "n_final": int,
                "symmetry_factor": float,
                "sign": int,
                "particles": {
                  "initial": List[str],  # HEPTAPOD labels
                  "final": List[str],
                  "propagators": List[str]
                }
              }

        Raises:
            ValueError: If diagram is invalid
        """
        self._ensure_loaded()

        try:
            # Extract basic properties
            vertices = diagram.vertices()
            propagators = diagram.propagators()
            incoming = diagram.incoming()
            outgoing = diagram.outgoing()

            # Get particle names (convert to HEPTAPOD notation)
            initial_particles = [
                feyngraph_to_nda_label(leg.particle().name())
                for leg in incoming
            ]
            final_particles = [
                feyngraph_to_nda_label(leg.particle().name())
                for leg in outgoing
            ]
            propagator_particles = [
                feyngraph_to_nda_label(prop.particle().name())
                for prop in propagators
            ]

            return {
                "n_vertices": len(vertices),
                "n_propagators": len(propagators),
                "n_initial": len(incoming),
                "n_final": len(outgoing),
                "symmetry_factor": diagram.symmetry_factor(),
                "sign": diagram.sign(),
                "particles": {
                    "initial": initial_particles,
                    "final": final_particles,
                    "propagators": propagator_particles
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to extract diagram info: {e}") from e


# Convenience function for quick enumeration
def enumerate_sm_diagrams(
    initial: List[str],
    final: List[str],
    max_loops: int = 0
) -> List[Any]:
    """
    Quick enumeration of Standard Model diagrams.

    Args:
        initial: Initial state particles (HEPTAPOD labels)
        final: Final state particles (HEPTAPOD labels)
        max_loops: Maximum loop order

    Returns:
        List of FeynGraph diagram objects

    Examples:
        >>> diagrams = enumerate_sm_diagrams(["H"], ["b", "bbar"])
        >>> len(diagrams)
        1
    """
    interface = FeynGraphInterface("SM")
    return interface.enumerate_diagrams(initial, final, max_loops)
