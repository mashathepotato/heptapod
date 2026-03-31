"""
# particle_database.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Standard Model particle database with quantum numbers.

This database provides quantum number lookup for common SM particles.
Used for automatic quantum number inference from particle labels.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ParticleData:
    """Complete particle data including all quantum numbers."""
    label: str
    name: str
    spin: float
    charge: float
    lepton_e: float = 0.0
    lepton_mu: float = 0.0
    lepton_tau: float = 0.0
    baryon_number: float = 0.0
    weak_isospin_3: float = 0.0
    color: Optional[str] = None
    mass: Optional[float] = None  # GeV
    pdg_code: Optional[int] = None
    antiparticle: Optional[str] = None


# Standard Model Particle Database
SM_PARTICLES: Dict[str, ParticleData] = {
    # ========================================================================
    # Leptons
    # ========================================================================
    "e": ParticleData("e", "electron", 0.5, -1.0, lepton_e=1.0,
                      mass=0.000511, pdg_code=11, antiparticle="e+"),
    "e+": ParticleData("e+", "positron", 0.5, 1.0, lepton_e=-1.0,
                       mass=0.000511, pdg_code=-11, antiparticle="e"),
    "nu_e": ParticleData("nu_e", "electron neutrino", 0.5, 0.0, lepton_e=1.0,
                          mass=0.0, pdg_code=12, antiparticle="nu_e_bar"),
    "nu_e_bar": ParticleData("nu_e_bar", "electron antineutrino", 0.5, 0.0,
                              lepton_e=-1.0, mass=0.0, pdg_code=-12,
                              antiparticle="nu_e"),

    "mu": ParticleData("mu", "muon", 0.5, -1.0, lepton_mu=1.0,
                       mass=0.1057, pdg_code=13, antiparticle="mu+"),
    "mu+": ParticleData("mu+", "antimuon", 0.5, 1.0, lepton_mu=-1.0,
                        mass=0.1057, pdg_code=-13, antiparticle="mu"),
    "nu_mu": ParticleData("nu_mu", "muon neutrino", 0.5, 0.0, lepton_mu=1.0,
                           mass=0.0, pdg_code=14, antiparticle="nu_mu_bar"),
    "nu_mu_bar": ParticleData("nu_mu_bar", "muon antineutrino", 0.5, 0.0,
                               lepton_mu=-1.0, mass=0.0, pdg_code=-14,
                               antiparticle="nu_mu"),

    "tau": ParticleData("tau", "tau", 0.5, -1.0, lepton_tau=1.0,
                        mass=1.777, pdg_code=15, antiparticle="tau+"),
    "tau+": ParticleData("tau+", "antitau", 0.5, 1.0, lepton_tau=-1.0,
                         mass=1.777, pdg_code=-15, antiparticle="tau"),
    "nu_tau": ParticleData("nu_tau", "tau neutrino", 0.5, 0.0, lepton_tau=1.0,
                            mass=0.0, pdg_code=16, antiparticle="nu_tau_bar"),
    "nu_tau_bar": ParticleData("nu_tau_bar", "tau antineutrino", 0.5, 0.0,
                                lepton_tau=-1.0, mass=0.0, pdg_code=-16,
                                antiparticle="nu_tau"),

    # ========================================================================
    # Quarks (up-type)
    # ========================================================================
    "u": ParticleData("u", "up quark", 0.5, 2/3, baryon_number=1/3,
                      color="triplet", mass=0.0023, pdg_code=2,
                      antiparticle="ubar"),
    "ubar": ParticleData("ubar", "up antiquark", 0.5, -2/3, baryon_number=-1/3,
                          color="antitriplet", mass=0.0023, pdg_code=-2,
                          antiparticle="u"),
    "c": ParticleData("c", "charm quark", 0.5, 2/3, baryon_number=1/3,
                      color="triplet", mass=1.28, pdg_code=4,
                      antiparticle="cbar"),
    "cbar": ParticleData("cbar", "charm antiquark", 0.5, -2/3,
                          baryon_number=-1/3, color="antitriplet",
                          mass=1.28, pdg_code=-4, antiparticle="c"),
    "t": ParticleData("t", "top quark", 0.5, 2/3, baryon_number=1/3,
                      color="triplet", mass=173.0, pdg_code=6,
                      antiparticle="tbar"),
    "tbar": ParticleData("tbar", "top antiquark", 0.5, -2/3,
                          baryon_number=-1/3, color="antitriplet",
                          mass=173.0, pdg_code=-6, antiparticle="t"),

    # ========================================================================
    # Quarks (down-type)
    # ========================================================================
    "d": ParticleData("d", "down quark", 0.5, -1/3, baryon_number=1/3,
                      color="triplet", mass=0.0048, pdg_code=1,
                      antiparticle="dbar"),
    "dbar": ParticleData("dbar", "down antiquark", 0.5, 1/3,
                          baryon_number=-1/3, color="antitriplet",
                          mass=0.0048, pdg_code=-1, antiparticle="d"),
    "s": ParticleData("s", "strange quark", 0.5, -1/3, baryon_number=1/3,
                      color="triplet", mass=0.095, pdg_code=3,
                      antiparticle="sbar"),
    "sbar": ParticleData("sbar", "strange antiquark", 0.5, 1/3,
                          baryon_number=-1/3, color="antitriplet",
                          mass=0.095, pdg_code=-3, antiparticle="s"),
    "b": ParticleData("b", "bottom quark", 0.5, -1/3, baryon_number=1/3,
                      color="triplet", mass=4.18, pdg_code=5,
                      antiparticle="bbar"),
    "bbar": ParticleData("bbar", "bottom antiquark", 0.5, 1/3,
                          baryon_number=-1/3, color="antitriplet",
                          mass=4.18, pdg_code=-5, antiparticle="b"),

    # ========================================================================
    # Gauge bosons
    # ========================================================================
    "gamma": ParticleData("gamma", "photon", 1.0, 0.0, mass=0.0,
                           pdg_code=22, antiparticle="gamma"),
    "g": ParticleData("g", "gluon", 1.0, 0.0, color="octet", mass=0.0,
                      pdg_code=21, antiparticle="g"),
    "Z": ParticleData("Z", "Z boson", 1.0, 0.0, mass=91.2, pdg_code=23,
                      antiparticle="Z"),
    "W+": ParticleData("W+", "W plus", 1.0, 1.0, mass=80.4, pdg_code=24,
                       antiparticle="W-"),
    "W-": ParticleData("W-", "W minus", 1.0, -1.0, mass=80.4, pdg_code=-24,
                       antiparticle="W+"),

    # ========================================================================
    # Higgs
    # ========================================================================
    "H": ParticleData("H", "Higgs boson", 0.0, 0.0, mass=125.0, pdg_code=25,
                      antiparticle="H"),

    # ========================================================================
    # Composite particles (baryons)
    # ========================================================================
    "p": ParticleData("p", "proton", 0.5, 1.0, baryon_number=1.0, mass=0.938,
                      pdg_code=2212, antiparticle="pbar"),
    "pbar": ParticleData("pbar", "antiproton", 0.5, -1.0, baryon_number=-1.0,
                          mass=0.938, pdg_code=-2212, antiparticle="p"),
    "n": ParticleData("n", "neutron", 0.5, 0.0, baryon_number=1.0, mass=0.940,
                      pdg_code=2112, antiparticle="nbar"),
    "nbar": ParticleData("nbar", "antineutron", 0.5, 0.0, baryon_number=-1.0,
                          mass=0.940, pdg_code=-2112, antiparticle="n"),
}


def get_particle_data(label: str) -> Optional[ParticleData]:
    """
    Get particle data from label.

    Handles common naming conventions:
    - Direct match: "e", "mu", "tau"
    - Bar notation: "ebar" -> "e+", "nuebar" -> "nu_e_bar"
    - Plus/minus: "e+", "mu-"
    - Compact neutrino notation: "numu" -> "nu_mu", "nue" -> "nu_e"
    - Anti prefix: "anti_nu_e" -> "nu_e_bar", "antinue" -> "nu_e_bar"
    - Reversed bar notation: "nubar_e" -> "nu_e_bar"

    Args:
        label: Particle label

    Returns:
        ParticleData if found, None otherwise
    """
    # Direct lookup
    if label in SM_PARTICLES:
        return SM_PARTICLES[label]

    # Normalize: remove spaces, convert to lowercase for matching
    normalized = label.lower().replace(" ", "").replace("-", "").replace("_", "")

    # Try common variations
    # "ebar" -> antiparticle of "e"
    if label.endswith("bar"):
        base = label[:-3]
        if base in SM_PARTICLES:
            antiparticle_label = SM_PARTICLES[base].antiparticle
            if antiparticle_label:
                return SM_PARTICLES.get(antiparticle_label)

        # Handle "nuebar" -> "nu_e_bar"
        # Try adding underscores: "nuebar" -> "nu_e_bar"
        if base.startswith("nu"):
            rest = base[2:]  # Remove "nu"
            # Remove leading underscore if present
            rest = rest.lstrip("_")
            canonical = f"nu_{rest}_bar"
            if canonical in SM_PARTICLES:
                return SM_PARTICLES[canonical]

    # Handle "e-" -> "e", "mu-" -> "mu", "tau-" -> "tau"
    if label.endswith("-"):
        base = label[:-1]
        if base in SM_PARTICLES:
            return SM_PARTICLES[base]

    # Handle compact neutrino notation: "numu" -> "nu_mu", "nue" -> "nu_e"
    if label.startswith("nu") and len(label) > 2:
        rest = label[2:]
        # Remove leading underscore if present
        rest = rest.lstrip("_")
        # Try with underscore
        canonical = f"nu_{rest}"
        if canonical in SM_PARTICLES:
            return SM_PARTICLES[canonical]

    # Handle "anti" prefix: "anti_nu_e", "antinue", "antinu_e" -> "nu_e_bar"
    if normalized.startswith("anti"):
        base = normalized[4:]  # Remove "anti"
        # Try to find the particle and return its antiparticle
        # Handle "antinue" -> "nue" -> "nu_e" -> "nu_e_bar"
        if base.startswith("nu"):
            flavor = base[2:]  # "e", "mu", "tau"
            canonical = f"nu_{flavor}_bar"
            if canonical in SM_PARTICLES:
                return SM_PARTICLES[canonical]
        # Handle other anti-particles
        for key, data in SM_PARTICLES.items():
            if key.replace("_", "") == base and data.antiparticle:
                return SM_PARTICLES.get(data.antiparticle)

    # Handle "nubar_e", "nubar_mu" -> "nu_e_bar", "nu_mu_bar"
    if "nubar" in normalized:
        # Extract flavor from "nubar_e", "nubare", "nu_bar_e"
        rest = normalized.replace("nubar", "").replace("_", "")
        if rest in ["e", "mu", "tau"]:
            canonical = f"nu_{rest}_bar"
            if canonical in SM_PARTICLES:
                return SM_PARTICLES[canonical]

    return None


def infer_quantum_numbers(particle):
    """
    Infer missing quantum numbers from particle label.

    If particle has a label but missing quantum numbers, look them up
    in the SM database and populate.

    Args:
        particle: Particle object (may have incomplete quantum numbers)

    Returns:
        Particle with inferred quantum numbers (modified in place)
    """
    if particle.label is None:
        return particle

    data = get_particle_data(particle.label)
    if data is None:
        return particle

    # Populate missing fields
    if particle.spin is None:
        particle.spin = data.spin
    if particle.mass is None and data.mass is not None:
        particle.mass = data.mass
    if particle.color is None:
        particle.color = data.color
    if particle.charge is None:
        particle.charge = data.charge
    if particle.lepton_e is None:
        particle.lepton_e = data.lepton_e
    if particle.lepton_mu is None:
        particle.lepton_mu = data.lepton_mu
    if particle.lepton_tau is None:
        particle.lepton_tau = data.lepton_tau
    if particle.baryon_number is None:
        particle.baryon_number = data.baryon_number

    return particle
