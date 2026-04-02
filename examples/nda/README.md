# NDA (Naive Dimensional Analysis) Example

Order-of-magnitude decay width and branching ratio estimation with automatic
diagram enumeration.

## What this toolkit does

The NDA toolkit provides **fast order-of-magnitude estimates** of partial
decay widths and cross sections using dimensional analysis and phase space
scaling. Combined with FeynGraph diagram enumeration, it can systematically
survey multi-body decay channels and rank them by importance.

**No external software required** -- runs with Python only.

## Quick start

### 1. Set up the MCP server

#### Claude Code

```bash
# Create a working directory
mkdir my_nda_session && cd my_nda_session

# Copy the system prompt and MCP config
cp /path/to/heptapod/prompts/examples/nda/system/nda_system_prompt.md CLAUDE.md
cp /path/to/heptapod/examples/nda/mcp.json .mcp.json

# Edit .mcp.json: replace /path/to/python with your Python executable
# Then launch
claude
```

Or register the MCP server globally:

```bash
claude mcp add heptapod-nda -- /path/to/python mcp/heptapod_server_stdio.py --groups nda_toolkit
```

#### OpenAI Codex

```bash
# Create a working directory
mkdir my_nda_session && cd my_nda_session

# Copy the system prompt (Codex uses AGENTS.md)
cp /path/to/heptapod/prompts/examples/nda/system/nda_system_prompt.md AGENTS.md

# Register MCP server via Codex CLI
codex mcp add heptapod-nda -- /path/to/python mcp/heptapod_server_stdio.py --groups nda_toolkit
```

#### Orchestral

```python
from mcp.heptapod_tools import get_tools
tools = get_tools("nda_toolkit")

# Load system prompt
system_prompt = open("prompts/examples/nda/system/nda_system_prompt.md").read()
```

## Tool group: `nda_toolkit`

The `nda_toolkit` group bundles NDA estimation with diagram enumeration, PDG
reference values, and optional MadGraph cross-checks:

| Tool | Purpose |
|------|---------|
| EstimateDecayWidthNDA | NDA width from a numerical diagram |
| EstimateDecayWidthFormulaNDA | NDA scaling formula (no numerics) |
| EstimateBranchingRatioNDA | Branching ratios from diagram classes |
| EstimatePhaseSpace | n-body phase space volume |
| EnumerateDiagrams | Auto-enumerate Feynman diagrams |
| VisualizeDiagrams | SVG/TikZ diagram rendering |
| PDGDatabase | Reference experimental values |
| PDGSearch | Search for particles by name |
| MadGraphFromRunCard | Exact cross-check (requires MadGraph) |

## Worked example

See `task_prompt.md` for the prompt and `transcripts/` for the full
conversation and agent outputs. The system prompt used is at
`prompts/examples/nda/system/nda_system_prompt.md`.

**Task:** Determine the maximum number of $e^+e^-$ pairs in muon decay
observable at current/planned experiments, using diagram enumeration + NDA
scaling + MadGraph validation.

**Deliverables** (in `transcripts/sandbox/`):
- `summary/multipair_muon_decay.pdf` -- Complete analysis report
- `scripts/plot_*.py` -- Figure generation scripts
- `nda_br_summary_*.md` -- NDA branching ratio estimates per multiplicity
- `diagrams_*/` -- Representative diagrams per channel
- Figure PDFs: branching ratio scaling, diagram metadata, suppression analysis

**Session stats:** 64 minutes, 37.7 min LLM inference time.
