# FeynGraph Integration for HEPTAPOD

Automatic Feynman diagram enumeration using FeynGraph with HEPTAPOD's NDA tools.

## Overview

This module provides HEPTAPOD integration with [FeynGraph](https://github.com/andrewfowlie/feyngraph), a modern Rust-based library for automatic generation of all topologically distinct Feynman diagrams.

**Key Features:**
- 🚀 **Fast**: ~10^5 diagrams/second (Rust backend)
- 🎯 **Complete**: Enumerates ALL topologically distinct diagrams
- 🔬 **Physics-aware**: Ranks by NDA estimates + coupling power counting
- 🔌 **Modular**: Optional dependency, seamlessly integrates with existing workflow
- 📊 **Informative**: Provides physics explanations for each diagram's importance

## Installation

### Requirements

```bash
# Install FeynGraph (optional - only needed for automatic enumeration)
pip install feyngraph

# Or add to requirements.txt
echo "feyngraph>=0.1.0" >> requirements.txt
```

### Without FeynGraph

If FeynGraph is not installed, the tools will provide helpful error messages with installation instructions. Manual `Diagram` specification still works perfectly.

## Quick Start

### Example: Enumerate H → X + Y diagrams

```python
from tools.feyngraph import EnumerateDiagramsTool

tool = EnumerateDiagramsTool(
    initial_state=[{"label": "H", "spin": 0, "mass": 125.0}],
    final_state=[
        {"label": "b", "spin": 0.5, "mass": 4.2},
        {"label": "bbar", "spin": 0.5, "mass": 4.2}
    ],
    max_loop_order=0,
    max_diagrams=10,
    model="SM",
    base_directory="/path/to/workspace"
)

result = tool._run()
# Returns JSON with ranked diagrams and NDA estimates
```

## Module Structure

```
tools/feyngraph/
├── __init__.py                      # Main exports
├── model_mapping.py                 # Particle labels & SM couplings
├── feyngraph_interface.py           # FeynGraph API wrapper
├── diagram_converter.py             # FeynGraph → Diagram conversion
├── ranking.py                       # NDA-based ranking
├── enumerate_diagrams_tool.py       # Main Orchestral BaseTool
├── test_feyngraph.py                # Tests
├── README.md                        # This file
└── docs/
    └── FEYNGRAPH_INTEGRATION_DESIGN.md  # Detailed design
```

## Components

### 1. Model Mapping (`model_mapping.py`)

Particle label conversions and Standard Model parameters.

```python
from tools.feyngraph import nda_to_feyngraph_label, get_sm_coupling

# Convert particle labels
fg_label = nda_to_feyngraph_label("gamma")  # Returns "a"

# Get SM couplings
alpha_em = get_sm_coupling("alpha_em")      # Returns 1/137
```

### 2. FeynGraph Interface (`feyngraph_interface.py`)

Wrapper for FeynGraph API.

```python
from tools.feyngraph.feyngraph_interface import FeynGraphInterface

interface = FeynGraphInterface(model="SM")
diagrams = interface.enumerate_diagrams(
    initial_particles=["H"],
    final_particles=["b", "bbar"],
    max_loop_order=0
)
```

### 3. Diagram Converter (`diagram_converter.py`)

Convert FeynGraph diagrams to HEPTAPOD `Diagram` format.

```python
from tools.feyngraph.diagram_converter import DiagramConverter

converter = DiagramConverter()
nda_diagram = converter.convert(fg_diagram)  # Returns Diagram object
```

### 4. Ranking (`ranking.py`)

Rank diagrams by physics importance.

```python
from tools.feyngraph.ranking import rank_diagrams

ranked = rank_diagrams(diagrams)
# Returns sorted list with NDA estimates and explanations
```

### 5. Main Tool (`enumerate_diagrams_tool.py`)

Orchestral `BaseTool` for LLM agents.

## Usage Scenarios

### Scenario 1: Find dominant Higgs decay modes

```python
tool = EnumerateDiagramsTool(
    initial_state=[{"label": "H", "spin": 0}],
    final_state=[{"label": "?", "spin": "?"}],  # Enumerate all possible
    max_loop_order=0,
    max_diagrams=20
)
```

### Scenario 2: Compare 1-loop vs tree-level

```python
# Tree-level
tool_tree = EnumerateDiagramsTool(..., max_loop_order=0)

# 1-loop
tool_loop = EnumerateDiagramsTool(..., max_loop_order=1)

# Compare suppression factors
```

### Scenario 3: BSM with UFO model

```python
tool = EnumerateDiagramsTool(
    initial_state=[{"label": "chi0", "spin": 0.5, "mass": 500.0}],
    final_state=[{"label": "e+", "spin": 0.5}, {"label": "e-", "spin": 0.5}],
    max_loop_order=1,
    model="/path/to/my_bsm_model_UFO"
)
```

## Output Format

```json
{
  "status": "ok",
  "schema": "feyngraph-enumerate-1.0",
  "n_diagrams_total": 247,
  "n_diagrams_returned": 10,
  "diagrams": [
    {
      "rank": 1,
      "width_gev": 2.68e-3,
      "diagram": {
        "topology": "tree_2body",
        "initial": [...],
        "final": [...],
        "vertices": [...],
        "couplings": {...}
      },
      "ranking_info": {
        "loop_order": 0,
        "coupling_power": 2,
        "explanation": "Tree-level Yukawa coupling. Dominant contribution."
      }
    }
  ]
}
```

## Design Principles

1. **Preserve existing workflow**: Manual `Diagram` specification remains primary
2. **Optional**: FeynGraph is opt-in for complex processes
3. **Seamless**: Diagrams convert to standard format
4. **Physics-based**: Ranking explains importance

## Limitations

- Requires FeynGraph installation (`pip install feyngraph`)
- Best performance with Standard Model
- UFO model support depends on FeynGraph capabilities
- NDA estimates only (no full amplitude calculations)
- Diagrams treated independently (no interference)

## Documentation

- [Design Document](docs/FEYNGRAPH_INTEGRATION_DESIGN.md) - Full architecture and API specs
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - General tool development guide
- [FeynGraph GitHub](https://github.com/andrewfowlie/feyngraph) - Upstream library

## Testing

```bash
# Run tests
python tools/feyngraph/test_feyngraph.py

# Or via test runner
python test_runner.py --only feyngraph
```

## Future Enhancements

- Amplitude caching for repeated processes
- Parallel NDA calculation for large diagram sets
- Integration with diagram visualizer
- Pre-computed process database for common SM processes
- Smart filtering using quantum number conservation

## License

Part of the HEPTAPOD package. See [LICENSE](../../LICENSE) for details.
