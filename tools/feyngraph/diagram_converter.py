"""
# diagram_converter.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Convert FeynGraph diagram objects to HEPTAPOD Diagram format.

This module provides the DiagramConverter class which takes FeynGraph diagram
objects (topology + particle assignments) and converts them to HEPTAPOD's
Diagram dataclass format for NDA calculations.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

try:
    # Import HEPTAPOD NDA components
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    TOOL_DIR = Path(__file__).resolve().parent
    REPO_ROOT = TOOL_DIR.parent.parent
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from tools.nda.simple_diagram import Diagram, Particle, Vertex, Propagator
    from tools.nda.particle_database import infer_quantum_numbers
    from tools.nda.topology import TOPOLOGIES, calculate_loop_number
except ImportError as e:
    raise ImportError(
        f"Failed to import HEPTAPOD NDA components: {e}\n"
        f"Ensure you're running from the repository root."
    ) from e

try:
    from .model_mapping import (
        feyngraph_to_nda_label,
        get_sm_coupling,
        get_particle_mass
    )
except ImportError:
    from model_mapping import (
        feyngraph_to_nda_label,
        get_sm_coupling,
        get_particle_mass
    )


@dataclass
class ConversionInfo:
    """
    Metadata about diagram conversion.

    Tracks information useful for debugging and validation.
    """
    topology_inferred: str
    n_vertices: int
    n_propagators: int
    n_loops: int
    particle_labels: List[str]
    warnings: List[str]


class DiagramConverter:
    """
    Convert FeynGraph diagrams to HEPTAPOD Diagram format.

    This class handles the conversion of FeynGraph diagram objects (which
    represent topology and particle assignments) into HEPTAPOD's Diagram
    dataclass format suitable for NDA calculations.

    The conversion process:
      1. Extract topology structure (vertices, edges, loops)
      2. Map FeynGraph particle labels to HEPTAPOD notation
      3. Identify interaction types at each vertex
      4. Extract propagator information (particles, masses, loop flags)
      5. Infer quantum numbers from particle database
      6. Calculate color factors
      7. Populate Diagram dataclass

    Attributes:
        strict_mode: If True, raise errors on ambiguous conversions.
                    If False, make best-effort conversions with warnings.
        auto_infer_qn: If True, automatically infer quantum numbers from
                      particle labels using particle_database.

    Examples:
        >>> converter = DiagramConverter()
        >>> diagram = converter.convert(fg_diagram)
        >>> print(diagram.topology)
        "tree_2body"
    """

    def __init__(
        self,
        strict_mode: bool = False,
        auto_infer_qn: bool = True
    ):
        """
        Initialize diagram converter.

        Args:
            strict_mode: Raise errors on ambiguous conversions (default: False)
            auto_infer_qn: Auto-infer quantum numbers (default: True)
        """
        self.strict_mode = strict_mode
        self.auto_infer_qn = auto_infer_qn
        self.conversion_info: Optional[ConversionInfo] = None

    def convert(self, fg_diagram: Any) -> Diagram:
        """
        Convert a FeynGraph diagram to HEPTAPOD Diagram format.

        Args:
            fg_diagram: FeynGraph diagram object

        Returns:
            Diagram object ready for NDA calculations

        Raises:
            ValueError: If diagram structure is invalid or ambiguous

        Examples:
            >>> converter = DiagramConverter()
            >>> diagram = converter.convert(fg_diagram)
            >>> is_valid, warnings = diagram.validate()
        """
        # Clear previous conversion info
        self.conversion_info = None
        warnings = []

        # Extract particles from FeynGraph diagram
        initial_particles, final_particles, propagators = self._extract_particles(fg_diagram)

        # Extract vertices
        vertices = self._extract_vertices(fg_diagram)

        # Infer topology
        n_vertices = len(vertices)
        n_propagators = len(propagators)
        n_initial = len(initial_particles)
        n_final = len(final_particles)
        n_loops = self._calculate_loops(n_vertices, n_propagators)

        topology = self._infer_topology(
            n_vertices, n_propagators, n_initial, n_final, n_loops
        )

        # Infer coupling values
        couplings = self._infer_coupling_values(vertices)

        # Calculate color factor
        color_factor = self._calculate_color_factor(
            initial_particles, final_particles, propagators
        )

        # Store conversion info
        all_labels = ([p.label for p in initial_particles if p.label] +
                     [p.label for p in final_particles if p.label])
        self.conversion_info = ConversionInfo(
            topology_inferred=topology,
            n_vertices=n_vertices,
            n_propagators=n_propagators,
            n_loops=n_loops,
            particle_labels=all_labels,
            warnings=warnings
        )

        # Create Diagram object
        return Diagram(
            topology=topology,
            initial=initial_particles,
            final=final_particles,
            vertices=vertices,
            couplings=couplings,
            propagators=propagators if propagators else None,
            color_factor=color_factor,
            energy_scale=None  # User can override
        )

    def _calculate_loops(self, n_vertices: int, n_propagators: int) -> int:
        """
        Calculate number of loops using graph theory.

        L = I - V + 1, where I = internal lines, V = vertices

        Args:
            n_vertices: Number of vertices
            n_propagators: Number of internal propagators

        Returns:
            Number of loops
        """
        if n_propagators == 0:
            return 0
        return n_propagators - n_vertices + 1

    def _infer_topology(
        self,
        n_vertices: int,
        n_propagators: int,
        n_initial: int,
        n_final: int,
        n_loops: int
    ) -> str:
        """
        Infer HEPTAPOD topology string from diagram structure.

        Args:
            n_vertices: Number of vertices
            n_propagators: Number of internal propagators
            n_initial: Number of initial state particles
            n_final: Number of final state particles
            n_loops: Number of loops

        Returns:
            Topology string (e.g., "tree_2body", "tree_3body_1prop")

        Raises:
            ValueError: If topology cannot be determined

        Examples:
            >>> converter._infer_topology(1, 0, 1, 2, 0)
            "tree_2body"
            >>> converter._infer_topology(2, 1, 1, 3, 0)
            "tree_3body_1prop"
        """
        # Tree-level topologies (L = 0)
        if n_loops == 0:
            # No propagators: effective operator / direct vertex
            if n_propagators == 0:
                if n_final == 2:
                    return "tree_2body"
                elif n_final == 3:
                    return "tree_3body"
                else:
                    return "tree_nbody"
            # Single propagator: renormalizable with mediator
            elif n_propagators == 1:
                if n_final == 2:
                    return "tree_2body_1prop"
                elif n_final == 3:
                    return "tree_3body_1prop"
                else:
                    return "tree_nbody_1prop"
            # Multiple propagators: cascade / chain topology
            else:
                return "tree_nbody_nprop"

        # Loop topologies (L >= 1)
        elif n_loops == 1:
            if n_final == 2 and n_vertices == 3:
                return "loop_2body_triangle"
            elif n_final == 2 and n_vertices == 4:
                return "loop_2body_box"
            else:
                return "loop_nbody_1loop"

        elif n_loops == 2:
            return f"loop_2loop_{n_propagators}prop"

        else:
            return f"loop_{n_loops}loop_{n_propagators}prop"

    def _extract_particles(
        self,
        fg_diagram: Any
    ) -> Tuple[List[Particle], List[Particle], List[Propagator]]:
        """
        Extract particles from FeynGraph diagram.

        Args:
            fg_diagram: FeynGraph diagram object

        Returns:
            (initial_particles, final_particles, propagators)

        Raises:
            ValueError: If particle labels invalid
        """
        initial_particles = []
        final_particles = []
        propagators = []

        # Extract initial state particles
        for leg in fg_diagram.incoming():
            fg_particle = leg.particle()
            particle = self._map_particle(fg_particle.name())
            initial_particles.append(particle)

        # Extract final state particles
        for leg in fg_diagram.outgoing():
            fg_particle = leg.particle()
            particle = self._map_particle(fg_particle.name())
            final_particles.append(particle)

        # Extract internal propagators
        for fg_prop in fg_diagram.propagators():
            fg_particle = fg_prop.particle()
            particle = self._map_particle(fg_particle.name())

            # Create Propagator object
            propagator = Propagator(
                label=particle.label if particle.label else "unknown",
                mass=particle.mass,
                is_loop_propagator=False  # Will be set based on topology
            )
            propagators.append(propagator)

        return initial_particles, final_particles, propagators

    def _map_particle(self, fg_label: str) -> Particle:
        """
        Map FeynGraph particle label to HEPTAPOD Particle object.

        Args:
            fg_label: FeynGraph particle label (e.g., "b~", "a", "vm")

        Returns:
            Particle object with quantum numbers inferred

        Examples:
            >>> converter._map_particle("b~")
            Particle(label="bbar", spin=0.5, mass=4.18, ...)
        """
        # Convert label
        try:
            nda_label = feyngraph_to_nda_label(fg_label)
        except ValueError as e:
            if self.strict_mode:
                raise
            # Fallback: use FeynGraph label as-is with warning
            nda_label = fg_label

        # Get particle properties
        try:
            mass = get_particle_mass(nda_label)
        except ValueError:
            mass = None  # Unknown particle, mass must be specified

        # Create Particle object
        particle = Particle(
            label=nda_label,
            spin=None,  # Will be inferred or specified
            mass=mass
        )

        # Infer quantum numbers if enabled
        if self.auto_infer_qn:
            particle = infer_quantum_numbers(particle)

        return particle

    def _extract_vertices(self, fg_diagram: Any) -> List[Vertex]:
        """
        Extract vertex information from FeynGraph diagram.

        Args:
            fg_diagram: FeynGraph diagram object

        Returns:
            List of Vertex objects with interaction types

        Raises:
            ValueError: If vertex types cannot be determined
        """
        vertices = []

        for fg_vertex in fg_diagram.vertices():
            # Get particles at this vertex
            fg_particles = fg_vertex.particles_ordered()
            particle_names = [p.name() for p in fg_particles]

            # Determine vertex valence (number of legs)
            valence = len(particle_names)

            # Infer interaction type from particle content
            interaction_type = self._infer_interaction_type(particle_names)

            # Always include valence in type string for validation
            # Format: "type-Npt" where N is the valence (e.g., "weak-3pt", "gauge-4pt")
            # This allows topology validation to correctly calculate half-edges
            interaction_type = f"{interaction_type}-{valence}pt"

            # Determine coupling name (use base type without valence suffix)
            base_type = self._infer_interaction_type(particle_names)
            coupling_name = self._infer_coupling_name(base_type, particle_names)

            # Create Vertex object
            vertex = Vertex(
                type=interaction_type,
                coupling=coupling_name
            )
            vertices.append(vertex)

        return vertices

    def _infer_interaction_type(self, particles: List[str]) -> str:
        """
        Infer interaction type from particle content at vertex.

        Returns Lorentz structure names rather than SM-specific identifiers:
          - photon/gluon + fermions -> "vector"
          - W boson + fermions      -> "left-handed"
          - Z boson + fermions      -> "chiral"
          - Higgs + fermions        -> "scalar"

        Args:
            particles: List of particle names at vertex

        Returns:
            Interaction type string encoding the Lorentz structure
        """
        has_higgs = "H" in particles
        has_fermion = any(p in ["e-", "e+", "mu-", "mu+", "tau-", "tau+",
                                "u", "u~", "d", "d~", "s", "s~",
                                "c", "c~", "b", "b~", "t", "t~"] for p in particles)
        has_w = any(p in ["W+", "W-"] for p in particles)
        has_z = "Z" in particles
        has_photon = "a" in particles
        has_gluon = "g" in particles

        # Higgs + fermion pair -> scalar Yukawa
        if has_higgs and has_fermion:
            return "scalar"

        # W boson + fermions -> left-handed (V-A)
        if has_w and has_fermion:
            return "left-handed"

        # Z boson + fermions -> chiral (gL P_L + gR P_R)
        if has_z and has_fermion:
            return "chiral"

        # Photon + fermions -> pure vector
        if has_photon and has_fermion:
            return "vector"

        # Gluon + quarks -> pure vector (in QCD)
        if has_gluon and has_fermion:
            return "vector"

        # Bosonic vertices (W/Z without fermions, photon self-couplings, etc.)
        if has_w or has_z:
            return "gauge"

        if has_photon:
            return "vector"

        if has_gluon:
            return "vector"

        # Default
        return "gauge"

    def _infer_coupling_name(self, interaction_type: str, particles: List[str]):
        """
        Infer coupling constant name from interaction type.

        Args:
            interaction_type: Lorentz structure type
            particles: Particles at vertex

        Returns:
            Coupling constant name (str), or a dict for chiral vertices
        """
        if interaction_type == "scalar":
            # Yukawa coupling
            quarks = ["u", "u~", "d", "d~", "s", "s~", "c", "c~", "b", "b~", "t", "t~"]
            for q in quarks:
                if q in particles:
                    base_quark = q.replace("~", "")
                    return f"y_{base_quark}"
            leptons = ["e-", "e+", "mu-", "mu+", "tau-", "tau+"]
            for l in leptons:
                if l in particles:
                    lepton_name = l.replace("-", "").replace("+", "")
                    return f"y_{lepton_name}"
            return "y"

        elif interaction_type == "left-handed":
            return "g_w"

        elif interaction_type == "chiral":
            # Z boson: return dict with gL/gR for each fermion flavor
            fermion_label = None
            quarks = ["u", "u~", "d", "d~", "s", "s~", "c", "c~", "b", "b~", "t", "t~"]
            leptons = ["e-", "e+", "mu-", "mu+", "tau-", "tau+"]
            for q in quarks:
                if q in particles:
                    fermion_label = q.replace("~", "")
                    break
            if fermion_label is None:
                for l in leptons:
                    if l in particles:
                        fermion_label = l.replace("-", "").replace("+", "")
                        break
            if fermion_label is None:
                fermion_label = "f"
            return {"gL": f"gL_{fermion_label}", "gR": f"gR_{fermion_label}"}

        elif interaction_type == "vector":
            # Could be QED (photon) or QCD (gluon)
            has_gluon = "g" in particles
            if has_gluon:
                return "g_s"
            return "e"

        else:
            return "g"  # Generic coupling

    def _infer_coupling_values(
        self,
        vertices: List[Vertex]
    ) -> Dict[str, float]:
        """
        Infer coupling constant values from vertex types.

        Handles both simple string couplings and dict couplings (chiral).

        Args:
            vertices: List of Vertex objects

        Returns:
            Dictionary mapping coupling names to values

        Examples:
            >>> vertices = [Vertex(type="scalar", coupling="y_b")]
            >>> converter._infer_coupling_values(vertices)
            {"y_b": 0.0242}
        """
        couplings = {}

        for vertex in vertices:
            coupling = vertex.coupling
            if isinstance(coupling, dict):
                # Chiral vertex: resolve each value in the dict
                for key, val in coupling.items():
                    if isinstance(val, str) and val not in couplings:
                        try:
                            couplings[val] = get_sm_coupling(val)
                        except ValueError:
                            couplings[val] = 1.0
            elif isinstance(coupling, str) and coupling not in couplings:
                try:
                    couplings[coupling] = get_sm_coupling(coupling)
                except ValueError:
                    couplings[coupling] = 1.0

        return couplings

    def _calculate_color_factor(
        self,
        initial: List[Particle],
        final: List[Particle],
        propagators: List[Propagator]
    ) -> float:
        """
        Calculate color factor for the diagram.

        Args:
            initial: Initial state particles
            final: Final state particles
            propagators: Internal propagators

        Returns:
            Color factor (dimensionless)

        Notes:
            - For colorless particles: 1.0
            - For qq̄ pair: 3.0 (color triplet)
            - For gluons: 8.0 (color octet)
            - For complex diagrams: product of color factors
        """
        # Count colored particles
        all_particles = initial + final + [p for p in propagators if hasattr(p, 'particle')]

        color_factor = 1.0

        # Simple heuristic: if any quarks, multiply by 3
        has_quarks = any(
            p.label in ['u', 'd', 's', 'c', 'b', 't',
                       'ubar', 'dbar', 'sbar', 'cbar', 'bbar', 'tbar']
            for p in all_particles
            if hasattr(p, 'label') and p.label
        )

        if has_quarks:
            color_factor *= 3.0

        # If gluons present, additional factor
        has_gluons = any(
            p.label == 'g'
            for p in all_particles
            if hasattr(p, 'label') and p.label
        )

        if has_gluons:
            color_factor *= 8.0

        return color_factor

    def get_conversion_info(self) -> Optional[ConversionInfo]:
        """
        Get metadata about the last conversion.

        Returns:
            ConversionInfo object with conversion details, or None if
            no conversion has been performed yet.

        Examples:
            >>> converter.convert(fg_diagram)
            >>> info = converter.get_conversion_info()
            >>> print(f"Topology: {info.topology_inferred}")
            >>> print(f"Warnings: {len(info.warnings)}")
        """
        return self.conversion_info


# Convenience function for quick conversion
def convert_feyngraph_diagram(fg_diagram: Any, strict: bool = False) -> Diagram:
    """
    Quick conversion of FeynGraph diagram to HEPTAPOD format.

    Args:
        fg_diagram: FeynGraph diagram object
        strict: If True, raise errors on ambiguous conversions

    Returns:
        Diagram object ready for NDA calculations

    Examples:
        >>> diagram = convert_feyngraph_diagram(fg_diagram)
        >>> is_valid, warnings = diagram.validate()
    """
    converter = DiagramConverter(strict_mode=strict)
    return converter.convert(fg_diagram)
