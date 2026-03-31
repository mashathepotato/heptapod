# NDA (Naive Dimensional Analysis) Tool

Order-of-magnitude decay width estimates using dimensional analysis.

## Overview

The NDA tool provides quick estimates for particle decay widths without requiring full event generation. It uses **Naive Dimensional Analysis** - a power-counting scheme based on dimensional analysis and coupling hierarchies.

**Use cases:**
- Preliminary phenomenology studies
- BSM model exploration
- Quick cross-checks before detailed simulations
- Teaching and learning particle physics

**Not a replacement for:** Full event generation (MadGraph, Pythia). NDA provides estimates to 1-2 orders of magnitude accuracy.

## Quick Start

```python
from tools.nda import EstimateDecayWidthNDATool
import json

# Define decay process using simple diagram format
diagram = {
    "topology": "tree_2body",
    "initial": [{"label": "H", "spin": 0, "mass": 125.0}],
    "final": [
        {"label": "b", "spin": "1/2", "mass": 4.2},
        {"label": "bbar", "spin": "1/2", "mass": 4.2}
    ],
    "vertices": [{"type": "yukawa", "coupling": 0.03}],
    "color_factor": 3.0
}

# Create and run tool
tool = EstimateDecayWidthNDATool(
    diagram=diagram,
    base_directory="/path/to/working/dir"
)

tool._setup()
result_str = tool._run()
result = json.loads(result_str)

print(f"Γ(H→bb̄) ≈ {result['width_mev']:.1f} MeV")
# Output: Γ(H→bb̄) ≈ 26.9 MeV
```

## Tool Interface

### Inputs (RuntimeField)

**`diagram`** (Dict[str, Any], required)
- Diagram specification in simple format
- See [Diagram Format](#diagram-format) below

### State (StateField)

**`base_directory`** (str, required)
- Base sandbox directory for file operations
- All file paths are resolved relative to this directory

### Output (JSON)

```json
{
  "status": "ok",
  "width_gev": 0.02686,
  "width_mev": 26.86,
  "formula": "\\Gamma = \\frac{1}{16\\pi M} \\times y^2 M^2",
  "scaling": "\\Gamma \\sim \\frac{y^2 M}{16\\pi}",
  "diagram": {
    "topology": "tree_2body",
    "n_vertices": 1,
    "n_propagators": 0,
    "loop_order": 0
  },
  "phase_space": 0.0398,
  "matrix_element": 168.75,
  "coupling": "y",
  "interaction": "yukawa"
}
```

## Diagram Format

The diagram is specified as a dictionary with the following structure:

```python
diagram = {
    # Topology (optional - can be auto-inferred)
    "topology": "tree_2body",  # tree_2body, tree_3body, s_channel_1prop,
                               # triangle_loop, box_loop, three_loop

    # Initial state (required)
    "initial": [
        {"label": "H", "spin": 0, "mass": 125.0}
    ],

    # Final state (required)
    "final": [
        {"label": "b", "spin": "1/2", "mass": 4.2},
        {"label": "bbar", "spin": "1/2", "mass": 4.2}
    ],

    # Vertices (required)
    "vertices": [
        {"type": "yukawa", "coupling": 0.03}
    ],

    # Propagators (optional - for processes with intermediate particles)
    "propagators": [
        {"label": "W", "mass": 80.4, "width": 2.1, "regime": "heavy"}
    ],

    # Couplings (optional - for named couplings)
    "couplings": {
        "y_b": 0.03
    },

    # Color factor (optional - auto-inferred if not provided)
    "color_factor": 3.0,

    # Energy scale (optional - for generic processes without masses)
    "energy_scale": 100.0
}
```

### Supported Topologies

**Tree-level:**
- `tree_2body` - 1→2 decay
- `tree_3body` - 1→3 decay
- `tree_nbody` - 1→n decay (n ≥ 4)
- `s_channel_1prop` - Process with s-channel propagator

**Loop diagrams:**
- `triangle_loop` - 1-loop triangle
- `box_loop` / `two_loop` - 2-loop box
- `three_loop` / `hexagon_loop` - 3-loop hexagon

### Supported Vertex Types

- `yukawa` - Yukawa coupling (scalar-fermion-fermion)
- `gauge-vector` - Gauge boson coupling (vector)
- `gauge-axial` - Gauge boson coupling (axial)
- `scalar-4pt` - Scalar 4-point interaction
- `dim6-4fermion` - Dimension-6 four-fermion operator
- `dim8-4fermion` - Dimension-8 four-fermion operator

## Examples

### Example 1: Standard Model Higgs

```python
# H → bb̄
diagram = {
    "topology": "tree_2body",
    "initial": [{"label": "H", "spin": 0, "mass": 125.0}],
    "final": [
        {"label": "b", "spin": "1/2", "mass": 4.2},
        {"label": "bbar", "spin": "1/2", "mass": 4.2}
    ],
    "vertices": [{"type": "yukawa", "coupling": 0.03}],
    "color_factor": 3.0
}

tool = EstimateDecayWidthNDATool(diagram=diagram, base_directory="/tmp")
result = json.loads(tool._run())
# Γ ≈ 27 MeV (experimental: ~2.4 MeV)
```

### Example 2: Muon Decay (EFT)

```python
# μ → eνν̄ (4-fermion contact interaction)
diagram = {
    "topology": "tree_3body",
    "initial": [{"label": "mu", "spin": "1/2", "mass": 0.106}],
    "final": [
        {"label": "e", "spin": "1/2"},
        {"label": "nu_mu", "spin": "1/2"},
        {"label": "nu_e", "spin": "1/2"}
    ],
    "vertices": [{"type": "dim6-4fermion", "coupling": "G_F"}],
    "couplings": {"G_F": 1.166e-5}  # GeV^-2
}
```

### Example 3: Generic BSM Process

```python
# Generic scalar → fermion pair (no specific particle labels)
diagram = {
    "topology": "tree_2body",
    "initial": [{"spin": 0}],
    "final": [{"spin": "1/2"}, {"spin": "1/2"}],
    "vertices": [{"type": "yukawa", "coupling": 0.1}],
    "energy_scale": 100.0  # GeV
}
```

### Example 4: Loop Process

```python
# H → γγ via top quark loop
diagram = {
    "topology": "triangle_loop",
    "initial": [{"label": "H", "spin": 0, "mass": 125.0}],
    "final": [
        {"label": "gamma", "spin": 1},
        {"label": "gamma", "spin": 1}
    ],
    "vertices": [
        {"type": "yukawa", "coupling": 1.0},
        {"type": "gauge-vector", "coupling": 0.3},
        {"type": "gauge-vector", "coupling": 0.3}
    ],
    "propagators": [
        {"label": "t", "mass": 173.0, "is_loop_propagator": True},
        {"label": "t", "mass": 173.0, "is_loop_propagator": True},
        {"label": "t", "mass": 173.0, "is_loop_propagator": True}
    ]
}
# Includes 1/(16π²) loop suppression automatically
```

## Physics Methodology

NDA estimates decay widths using dimensional analysis:

**Tree-level 2-body:**
```
Γ ~ g² M / (16π)
```

**Tree-level 3-body:**
```
Γ ~ g² M³ / (64π³)
```

**1-loop suppression:**
```
Γ_loop ~ Γ_tree × 1/(16π²)
```

**Heavy propagator suppression:**
```
Factor ~ 1/M_X²  (for M_X >> E)
```

**Accuracy:** Typically 1-2 orders of magnitude. Not a replacement for full simulation.

## Testing

Run tests:
```bash
python tools/nda/test_nda.py
```

Run example calculations:
```bash
python examples/nda_decay_widths.py
```

## Files

- `nda_tool.py` - Main tool implementation (`EstimateDecayWidthNDATool`)
- `phase_space.py` - Phase space factor calculations
- `matrix_element.py` - Matrix element NDA estimation
- `topology.py` - Topology definitions
- `simple_diagram.py` - Diagram data structures
- `test_nda.py` - Test suite
- `__init__.py` - Package exports

## Dependencies

- Python 3.7+
- NumPy
- Orchestral AI framework (BaseTool)

## References

- NDA methodology: arXiv:1804.01954
- Phase space formulas: Peskin & Schroeder, "An Introduction to QFT"
- Decay width formulas: PDG (Particle Data Group)

## License

Part of the HEPTAPOD package.
Copyright (C) 2026 HEPTAPOD authors.
Licensed under GNU GPL v3 or later.
