# EDA (Exact Diagrammatic Analysis) Example

Exact tree-level calculations via FeynCalc code generation and Mathematica.

## What this toolkit does

The EDA toolkit computes **exact symbolic partial decay widths and squared
amplitudes** for tree-level processes. It generates FeynCalc/Mathematica
scripts from a diagram specification, executes them via `wolframscript`, and
converts results to Python callables.

**Requires:** Mathematica with FeynCalc installed.

## Quick start

### 1. Set up the MCP server

#### Claude Code

```bash
# Create a working directory
mkdir my_eda_session && cd my_eda_session

# Copy the system prompt and MCP config
cp /path/to/heptapod/prompts/examples/eda/system/eda_system_prompt.md CLAUDE.md
cp /path/to/heptapod/examples/eda/mcp.json .mcp.json

# Edit .mcp.json: replace /path/to/python with your Python executable
# Then launch
claude
```

Or register the MCP server globally:

```bash
claude mcp add heptapod-eda -- /path/to/python examples/mcp/heptapod_server_stdio.py --groups eda_study
```

#### OpenAI Codex

```bash
# Create a working directory
mkdir my_eda_session && cd my_eda_session

# Copy the system prompt (Codex uses AGENTS.md)
cp /path/to/heptapod/prompts/examples/eda/system/eda_system_prompt.md AGENTS.md

# Register MCP server via Codex CLI
codex mcp add heptapod-eda -- /path/to/python examples/mcp/heptapod_server_stdio.py --groups eda_study
```

#### Orchestral

```python
from examples.mcp.heptapod_tools import get_tools
tools = get_tools("eda_study")

# Load system prompt
system_prompt = open("prompts/examples/eda/system/eda_system_prompt.md").read()
```

## Tool group: `eda_study`

The `eda_study` group bundles the EDA symbolic tools with NDA cross-checks
and PDG reference values:

| Tool | Purpose |
|------|---------|
| ComputeSymbolicAmplitude | Generate FeynCalc script from diagram spec |
| RunWolframScript | Execute a Mathematica script |
| RunWolframScriptBatch | Execute multiple scripts concurrently |
| SimplifyResult | Apply substitutions, limits, simplifications |
| SimplifyResultBatch | Batch simplification |
| ConvertToPython | Convert symbolic result to Python callable |
| EstimateDecayWidthNDA | NDA cross-check |
| EstimateDecayWidthFormulaNDA | NDA formula cross-check |
| PDGDatabase | Reference experimental values |

## Worked example

See `task_prompt.md` for the prompt and `transcripts/` for the full
conversation and agent outputs. The system prompt used is at
`prompts/examples/eda/system/eda_system_prompt.md`.

**Task:** Systematically compute all tree-level 1->2 decay widths across
spins {0, 1/2, 1}, all vertex types, both coupling bases (vector-axial
and chiral), with SM validation.

**Deliverables** (in `transcripts/sandbox/`):
- `summary/decay_catalog.pdf` -- Complete reference table of decay-width formulas
- `scripts/` -- 40 Wolfram scripts + result sidecars for each process
- `scripts/*.py` -- Python figure-generation scripts
- SM validation figures

**Session stats:** 73 minutes, 28.6 min LLM inference time.
