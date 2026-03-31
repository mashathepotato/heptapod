"""
# ranking.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Rank Feynman diagrams by physics importance using NDA estimates.

This module provides functions to rank diagrams based on multiple physics
criteria including NDA width estimates, loop order, coupling power counting,
and propagator mass hierarchies.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import math

try:
    # Import HEPTAPOD NDA components
    import sys
    from pathlib import Path

    TOOL_DIR = Path(__file__).resolve().parent
    REPO_ROOT = TOOL_DIR.parent.parent
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from tools.nda.simple_diagram import Diagram
    from tools.nda.topology import calculate_loop_number
except ImportError as e:
    raise ImportError(
        f"Failed to import HEPTAPOD NDA components: {e}\n"
        f"Ensure you're running from the repository root."
    ) from e


@dataclass
class RankingInfo:
    """
    Information about a diagram's ranking.

    Attributes:
        loop_order: Number of loops (0=tree, 1=1-loop, etc.)
        coupling_power: Total power of coupling constants
        coupling_names: List of coupling constant names
        suppression_factors: List of suppression descriptions
        explanation: Human-readable explanation of ranking
        score: Numerical ranking score (higher = more important)
        n_heavy_propagators: Number of heavy propagators (mass > 10 GeV)
    """
    loop_order: int
    coupling_power: int
    coupling_names: List[str]
    suppression_factors: List[str]
    explanation: str
    score: float
    n_heavy_propagators: int = 0


@dataclass
class RankedDiagram:
    """
    A diagram with ranking information.

    Attributes:
        rank: Ranking position (1 = most important)
        diagram: The Diagram object
        width_gev: NDA width estimate in GeV (if calculated)
        width_latex: LaTeX formula for width scaling
        ranking_info: RankingInfo with detailed ranking criteria
    """
    rank: int
    diagram: Diagram
    width_gev: Optional[float]
    width_latex: Optional[str]
    ranking_info: RankingInfo

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "rank": self.rank,
            "diagram": self.diagram.to_dict(),
            "width_gev": self.width_gev,
            "width_latex": self.width_latex,
            "ranking_info": {
                "loop_order": self.ranking_info.loop_order,
                "coupling_power": self.ranking_info.coupling_power,
                "coupling_names": self.ranking_info.coupling_names,
                "suppression_factors": self.ranking_info.suppression_factors,
                "explanation": self.ranking_info.explanation,
                "score": self.ranking_info.score,
                "n_heavy_propagators": self.ranking_info.n_heavy_propagators,
            }
        }


class DiagramRanker:
    """
    Rank diagrams by physics importance.

    This class implements a multi-criteria ranking algorithm that considers:
      1. NDA width estimate (larger = more important)
      2. Loop order (tree > 1-loop > 2-loop)
      3. Coupling power (fewer couplings = less suppression)
      4. Propagator mass scales (lighter = less suppression)

    The ranking helps identify which diagrams contribute most to a process.

    Attributes:
        calculate_nda: Whether to calculate NDA estimates (requires NDA tool)
        explain: Whether to generate physics explanations

    Examples:
        >>> ranker = DiagramRanker()
        >>> ranked = ranker.rank(diagrams)
        >>> print(f"Top diagram: {ranked[0].diagram.topology}")
        >>> print(f"Explanation: {ranked[0].ranking_info.explanation}")
    """

    def __init__(
        self,
        calculate_nda: bool = True,
        explain: bool = True
    ):
        """
        Initialize diagram ranker.

        Args:
            calculate_nda: Calculate NDA width estimates (default: True)
            explain: Generate physics explanations (default: True)
        """
        self.calculate_nda = calculate_nda
        self.explain = explain

    def rank(self, diagrams: List[Diagram]) -> List[RankedDiagram]:
        """
        Rank diagrams by physics importance.

        Args:
            diagrams: List of Diagram objects to rank

        Returns:
            List of RankedDiagram objects, sorted by importance (most important first)

        Examples:
            >>> ranker = DiagramRanker()
            >>> ranked = ranker.rank(diagrams)
            >>> print(f"{len(ranked)} diagrams ranked")
            >>> print(f"Top: {ranked[0].ranking_info.explanation}")
        """
        if not diagrams:
            return []

        # Calculate ranking info for each diagram
        diagram_scores = []
        for diagram in diagrams:
            info = self._calculate_ranking_info(diagram)
            width_gev = self._estimate_width(diagram) if self.calculate_nda else None
            width_latex = self._generate_width_formula(diagram)

            diagram_scores.append({
                "diagram": diagram,
                "info": info,
                "width_gev": width_gev,
                "width_latex": width_latex,
                "score": info.score
            })

        # Sort by score (descending - highest score = most important)
        diagram_scores.sort(key=lambda x: x["score"], reverse=True)

        # Assign ranks
        ranked = []
        for rank, item in enumerate(diagram_scores, start=1):
            ranked.append(RankedDiagram(
                rank=rank,
                diagram=item["diagram"],
                width_gev=item["width_gev"],
                width_latex=item["width_latex"],
                ranking_info=item["info"]
            ))

        return ranked

    def _calculate_ranking_info(self, diagram: Diagram) -> RankingInfo:
        """
        Calculate ranking information for a diagram.

        Args:
            diagram: Diagram object

        Returns:
            RankingInfo with detailed ranking criteria
        """
        # 1. Loop order
        loop_order = self._get_loop_order(diagram)

        # 2. Coupling power
        coupling_power = self._count_coupling_power(diagram)
        coupling_names = list(diagram.couplings.keys()) if diagram.couplings else []

        # 3. Suppression factors
        suppression_factors = self._identify_suppressions(diagram)

        # 4. Calculate overall score (pass diagram for proper propagator mass weighting)
        score = self._calculate_score(loop_order, coupling_power, suppression_factors, diagram)

        # 5. Count heavy propagators (mass > 10 GeV, e.g., W, Z bosons)
        n_heavy_propagators = self._count_heavy_propagators(diagram)

        # 6. Generate explanation
        explanation = self._generate_explanation(
            diagram, loop_order, coupling_power, suppression_factors, n_heavy_propagators
        ) if self.explain else ""

        return RankingInfo(
            loop_order=loop_order,
            coupling_power=coupling_power,
            coupling_names=coupling_names,
            suppression_factors=suppression_factors,
            explanation=explanation,
            score=score,
            n_heavy_propagators=n_heavy_propagators
        )

    def _get_loop_order(self, diagram: Diagram) -> int:
        """
        Determine loop order from topology.

        Args:
            diagram: Diagram object

        Returns:
            Loop order (0=tree, 1=1-loop, etc.)
        """
        topology = diagram.topology.lower()

        if "tree" in topology:
            return 0
        elif "1loop" in topology or "loop_1" in topology:
            return 1
        elif "2loop" in topology or "loop_2" in topology:
            return 2
        else:
            # Try to extract from topology string
            if "loop_" in topology:
                parts = topology.split("_")
                for i, part in enumerate(parts):
                    if part == "loop" and i + 1 < len(parts):
                        try:
                            return int(parts[i + 1].replace("loop", ""))
                        except ValueError:
                            pass

        # Fallback: calculate from graph structure
        try:
            n_vertices = len(diagram.vertices)
            n_propagators = len(diagram.propagators) if diagram.propagators else 0
            n_external = len(diagram.initial) + len(diagram.final)
            loop_order = calculate_loop_number(n_vertices, n_propagators, n_external)
            return loop_order
        except:
            return 0  # Default to tree-level

    def _count_coupling_power(self, diagram: Diagram) -> int:
        """
        Count total power of coupling constants.

        Args:
            diagram: Diagram object

        Returns:
            Total coupling power (e.g., 2 for g² interaction)
        """
        # Each vertex contributes coupling powers
        # For now, assume each vertex = 1 coupling power
        # More sophisticated: parse vertex types and determine powers
        return len(diagram.vertices)

    def _identify_suppressions(self, diagram: Diagram) -> List[str]:
        """
        Identify suppression factors in the diagram.

        Args:
            diagram: Diagram object

        Returns:
            List of suppression factor descriptions
        """
        suppressions = []

        # Loop suppression
        loop_order = self._get_loop_order(diagram)
        if loop_order > 0:
            loop_supp = f"(1/16π²)^{loop_order} ≈ {(1/(16*math.pi**2))**loop_order:.2e}"
            suppressions.append(f"Loop suppression: {loop_supp}")

        # Heavy propagator suppression
        if diagram.propagators:
            for i, prop in enumerate(diagram.propagators):
                if hasattr(prop, 'mass') and prop.mass and prop.mass > 10.0:
                    # Heavy propagator (>10 GeV)
                    suppressions.append(
                        f"Heavy propagator: m = {prop.mass:.1f} GeV"
                    )

        # Coupling suppression
        if diagram.couplings:
            small_couplings = [
                (name, val) for name, val in diagram.couplings.items()
                if val < 0.1
            ]
            for name, val in small_couplings:
                suppressions.append(f"Small coupling: {name} = {val:.2e}")

        return suppressions

    def _count_heavy_propagators(self, diagram: Diagram) -> int:
        """
        Count heavy propagators (mass > 10 GeV, e.g., W, Z bosons).

        Heavy propagators introduce significant suppression factors in NDA
        estimates: each heavy propagator with mass M contributes ~(E/M)^4
        where E is the typical energy scale of the process.

        Args:
            diagram: Diagram object

        Returns:
            Number of heavy propagators
        """
        if not diagram.propagators:
            return 0
        return sum(
            1 for prop in diagram.propagators
            if hasattr(prop, 'mass') and prop.mass and prop.mass > 10.0
        )

    def _calculate_score(
        self,
        loop_order: int,
        coupling_power: int,
        suppressions: List[str],
        diagram: "Diagram" = None
    ) -> float:
        """
        Calculate overall ranking score based on perturbative order.

        Higher score = more important diagram.

        Ranking is by coupling order (standard in FeynGraph/MadGraph):
        - Loop order (tree > 1-loop > 2-loop)
        - Effective coupling factor (product of vertex couplings squared)
        - Heavy propagator count (major physics suppression)

        Args:
            loop_order: Number of loops
            coupling_power: Total coupling power (number of vertices)
            suppressions: List of suppression factors
            diagram: Diagram object (for propagator mass info)

        Returns:
            Ranking score (dimensionless)
        """
        # Start with base score
        score = 1000.0

        # Penalize loops (each loop divides by ~100)
        score /= (100.0 ** loop_order)

        # Calculate effective coupling factor from actual vertex couplings
        # |M|^2 ~ product of coupling^2 for each vertex
        if diagram is not None:
            coupling_factor = self._calculate_coupling_factor(diagram)
            score *= coupling_factor
        else:
            # Fallback: assume g^2 ~ 0.1 per vertex
            score /= (10.0 ** (coupling_power - 1))

        # Heavy propagator suppression: major physics effect
        # Each heavy propagator with mass M >> E contributes ~(E/M)^4
        # For M_W ~ 80 GeV and E ~ m_mu ~ 0.1 GeV: (0.1/80)^4 ~ 3e-12
        # We use 0.001 per heavy propagator to ensure n_heavy dominates over
        # coupling variations (which are typically only factors of a few)
        if diagram is not None:
            n_heavy = self._count_heavy_propagators(diagram)
            score *= (0.001 ** n_heavy)

        return score

    def _calculate_coupling_factor(self, diagram: Diagram) -> float:
        """
        Calculate effective coupling factor from vertex couplings.

        For amplitude M ~ g1 * g2 * ... * gn, the rate ~ |M|^2 ~ (g1*g2*...*gn)^2.
        This method returns the product of coupling values squared.

        Args:
            diagram: Diagram object

        Returns:
            Coupling factor (dimensionless)
        """
        if not diagram.vertices:
            return 1.0

        # Get coupling values from diagram
        coupling_values = diagram.couplings or {}

        # Calculate product of couplings squared
        factor = 1.0
        for vertex in diagram.vertices:
            coupling_name = vertex.coupling if hasattr(vertex, 'coupling') else None
            # Dict couplings (chiral vertices) — use first value or default
            if isinstance(coupling_name, dict):
                for k, v in coupling_name.items():
                    if isinstance(v, str) and v in coupling_values:
                        g = coupling_values[v]
                        factor *= g * g
                        break
                    elif isinstance(v, (int, float)):
                        factor *= v * v
                        break
                else:
                    factor *= 0.25
            elif coupling_name and coupling_name in coupling_values:
                g = coupling_values[coupling_name]
                factor *= g * g  # g^2 per vertex
            else:
                # Default coupling ~ 0.5
                factor *= 0.25

        return factor

    def _generate_explanation(
        self,
        diagram: Diagram,
        loop_order: int,
        coupling_power: int,
        suppressions: List[str],
        n_heavy_propagators: int = 0
    ) -> str:
        """
        Generate human-readable explanation of ranking.

        Args:
            diagram: Diagram object
            loop_order: Loop order
            coupling_power: Coupling power
            suppressions: Suppression factors
            n_heavy_propagators: Number of heavy propagators (mass > 10 GeV)

        Returns:
            Explanation string
        """
        parts = []

        # Loop order description
        if loop_order == 0:
            parts.append("Tree-level process")
        elif loop_order == 1:
            parts.append("1-loop correction (suppressed by 1/16π²)")
        else:
            parts.append(f"{loop_order}-loop (highly suppressed)")

        # Topology description
        if "2body" in diagram.topology:
            parts.append("2-body final state")
        elif "3body" in diagram.topology:
            parts.append("3-body final state (phase space suppressed)")
        elif "4body" in diagram.topology:
            parts.append("4-body final state (highly phase space suppressed)")

        # Heavy propagator info
        if n_heavy_propagators > 0:
            parts.append(f"{n_heavy_propagators} heavy propagator(s)")

        # Suppression summary
        n_other_supp = len([s for s in suppressions if "Heavy propagator" not in s])
        if n_other_supp > 0:
            parts.append(f"Additional suppressions: {n_other_supp}")
        else:
            if loop_order == 0 and coupling_power <= 2 and n_heavy_propagators == 0:
                parts.append("Dominant contribution")

        return ". ".join(parts) + "."

    def _estimate_width(self, diagram: Diagram) -> Optional[float]:
        """
        Estimate decay width using NDA tool.

        Args:
            diagram: Diagram object

        Returns:
            Width estimate in GeV, or None if calculation fails

        Note:
            This requires the EstimateDecayWidthNDATool to be available
            and will be implemented when full NDA integration is ready.
        """
        # TODO: Integrate with EstimateDecayWidthNDATool
        # For now, return None - will be implemented in enumerate_diagrams_tool.py
        return None

    def _generate_width_formula(self, diagram: Diagram) -> str:
        """
        Generate LaTeX formula for width scaling.

        Args:
            diagram: Diagram object

        Returns:
            LaTeX formula string
        """
        parts = [r"\Gamma \sim"]

        # Coupling factors
        if diagram.couplings:
            coupling_parts = []
            for name in sorted(diagram.couplings.keys()):
                # Count how many vertices use this coupling
                # For simplicity, use coupling^n_vertices for now
                n = len(diagram.vertices)
                if n == 1:
                    coupling_parts.append(name)
                else:
                    coupling_parts.append(f"{name}^{n}")
            parts.append(" ".join(coupling_parts))

        # Mass scale
        if diagram.initial:
            # Use first initial particle mass as scale
            init_particle = diagram.initial[0]
            if init_particle.label:
                parts.append(f"m_{{{init_particle.label}}}")

        # Loop suppression
        loop_order = self._get_loop_order(diagram)
        if loop_order > 0:
            if loop_order == 1:
                parts.append(r"\frac{1}{16\pi^2}")
            else:
                parts.append(rf"\left(\frac{{1}}{{16\pi^2}}\right)^{loop_order}")

        return " ".join(parts)


# Convenience function for quick ranking
def rank_diagrams(
    diagrams: List[Diagram],
    calculate_nda: bool = False
) -> List[RankedDiagram]:
    """
    Quick ranking of diagrams.

    Args:
        diagrams: List of Diagram objects
        calculate_nda: Whether to calculate NDA estimates (default: False)

    Returns:
        List of RankedDiagram objects, sorted by importance

    Examples:
        >>> ranked = rank_diagrams(diagrams)
        >>> print(f"Top diagram: rank {ranked[0].rank}")
        >>> print(ranked[0].ranking_info.explanation)
    """
    ranker = DiagramRanker(calculate_nda=calculate_nda)
    return ranker.rank(diagrams)
