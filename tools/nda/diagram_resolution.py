"""
# diagram_resolution.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Bridge from SymbolicDiagram to Diagram by resolving particle properties
and coupling constants from the Standard Model databases.

Usage:
    from tools.nda.symbolic_diagram import parse_symbolic_diagram
    from tools.nda.diagram_resolution import resolve_diagram

    sym = parse_symbolic_diagram({
        "initial": [{"label": "H"}],
        "final": [{"label": "b"}, {"label": "bbar"}],
        "vertices": [{"type": "yukawa", "coupling": "y_b"}],
    })
    diagram = resolve_diagram(sym)
    # diagram now has masses, spins, couplings filled in from SM data
"""

from typing import Dict, Optional

from .symbolic_diagram import SymbolicDiagram
from .simple_diagram import Diagram, Particle, Vertex, Propagator, infer_color_factor
from .particle_database import get_particle_data

# Import SM coupling/mass databases from feyngraph
try:
    from tools.feyngraph.model_mapping import SM_COUPLINGS, PARTICLE_MASSES
except ImportError:
    try:
        from ..feyngraph.model_mapping import SM_COUPLINGS, PARTICLE_MASSES
    except ImportError:
        SM_COUPLINGS = {}
        PARTICLE_MASSES = {}


def resolve_diagram(
    symbolic: SymbolicDiagram,
    model: str = "SM",
    mass_overrides: Optional[Dict[str, float]] = None,
    coupling_overrides: Optional[Dict[str, float]] = None,
) -> Diagram:
    """
    Resolve a SymbolicDiagram into a fully numerical Diagram.

    Resolution steps:
    1. For each particle label, look up mass + spin via particle_database
    2. For each coupling name, look up value via SM_COUPLINGS
    3. For propagators, look up mass via PARTICLE_MASSES
    4. Infer color_factor if not given
    5. Apply user overrides on top

    Args:
        symbolic: SymbolicDiagram to resolve
        model: Physics model (currently only "SM" supported)
        mass_overrides: Override masses by particle label, e.g. {"b": 4.5}
        coupling_overrides: Override couplings by name, e.g. {"y_b": 0.03}

    Returns:
        Fully populated Diagram

    Raises:
        ValueError: If a required coupling cannot be resolved
    """
    mass_overrides = mass_overrides or {}
    coupling_overrides = coupling_overrides or {}

    # Resolve particles
    initial = [_resolve_particle(p, mass_overrides) for p in symbolic.initial]
    final = [_resolve_particle(p, mass_overrides) for p in symbolic.final]

    # Resolve couplings dict
    couplings: Dict[str, float] = {}
    for v in symbolic.vertices:
        name = v.coupling
        if name in coupling_overrides:
            couplings[name] = coupling_overrides[name]
        elif name in SM_COUPLINGS:
            couplings[name] = SM_COUPLINGS[name]
        else:
            raise ValueError(
                f"Cannot resolve coupling '{name}': not found in SM_COUPLINGS "
                f"and no override provided. Available: {sorted(SM_COUPLINGS.keys())}"
            )

    # Resolve vertices (keep type, set coupling name for lookup)
    vertices = [
        Vertex(type=v.type, coupling=v.coupling)
        for v in symbolic.vertices
    ]

    # Resolve propagators
    propagators = [_resolve_propagator(p, mass_overrides) for p in symbolic.propagators]

    # Infer color factor
    if symbolic.color_factor is not None:
        color_factor = symbolic.color_factor
    else:
        color_factor = infer_color_factor(initial + final)

    return Diagram(
        topology=symbolic.topology,
        initial=initial,
        final=final,
        vertices=vertices,
        couplings=couplings,
        propagators=propagators,
        color_factor=color_factor,
    )


def _resolve_particle(sym_particle, mass_overrides: Dict[str, float]) -> Particle:
    """Resolve a SymbolicParticle into a Particle using the SM database."""
    label = sym_particle.label
    data = get_particle_data(label)

    # Start with values from SymbolicParticle (user-specified take priority)
    spin = sym_particle.spin
    mass = sym_particle.mass

    # Fill from database if not specified
    if data is not None:
        if spin is None:
            spin = data.spin
        if mass is None and data.mass is not None:
            mass = data.mass

    # Apply overrides
    if label in mass_overrides:
        mass = mass_overrides[label]

    particle = Particle(label=label, spin=spin, mass=mass)

    # Also fill quantum numbers from database for validation
    if data is not None:
        particle.color = data.color
        particle.charge = data.charge
        particle.lepton_e = data.lepton_e
        particle.lepton_mu = data.lepton_mu
        particle.lepton_tau = data.lepton_tau
        particle.baryon_number = data.baryon_number

    return particle


def _resolve_propagator(sym_prop, mass_overrides: Dict[str, float]) -> Propagator:
    """Resolve a SymbolicPropagator into a Propagator using SM databases."""
    label = sym_prop.label

    # Start with explicitly provided values
    spin = sym_prop.spin
    mass = sym_prop.mass

    # Look up from databases
    data = get_particle_data(label)
    if data is not None:
        if spin is None:
            spin = data.spin
        if mass is None and data.mass is not None:
            mass = data.mass
    elif mass is None and label in PARTICLE_MASSES:
        mass = PARTICLE_MASSES[label]

    # Apply overrides
    if label in mass_overrides:
        mass = mass_overrides[label]

    # Default mass to 0 if still unresolved (required by Propagator)
    if mass is None:
        mass = 0.0

    return Propagator(
        label=label,
        mass=mass,
        spin=spin,
        regime=sym_prop.regime,
    )
