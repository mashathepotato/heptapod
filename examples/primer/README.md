# Primer: Building Your First Tool

Start here if you have never written a tool for an LLM agent.

[`building_your_first_tool.ipynb`](building_your_first_tool.ipynb) is a
self-contained tutorial. It assumes only that you can write a Python function,
and it ends with two working tools served to a coding agent through
[toolbase](https://github.com/alexr314/toolbase).

## What it covers

1. **What a tool is** from the agent's point of view: a name, a docstring, and
   typed arguments
2. **Template A**, `@define_tool`, which turns a plain function into a tool
3. **Template B**, subclassing `BaseTool`, which every HEPTAPOD tool uses
4. **A realistic workflow**: pull events from a database, hand them to external
   physics code, get observables back
5. **Packaging**: writing a `toolkit.yaml` so toolbase can install, configure,
   and serve your tools over MCP, plus the skills that carry what does not fit
   in a docstring

## The worked example

A toy dimuon analysis, built to have the same shape as a columnar CMS analysis:

| In the notebook | In a typical CMS analysis |
| --- | --- |
| query a SQLite database | locate the dataset (Rucio), open its NanoAOD files with `uproot` |
| events written to JSON, one array per field | events as `awkward` arrays via `coffea`'s `NanoEvents` |
| `dimuon_lib.compute_observables()` | a `coffea` processor |
| the histogram at the end | `hist` objects the processor fills |

The database is a SQLite file the notebook fabricates, with NanoAOD-style column
names (`run`, `event`, `nMuon`, `Muon_pt`, ...). The external physics code is a
small vectorized module the notebook writes to disk, standing in for the
analysis library your group already maintains. The point of the exercise is the
split: **physics lives in the library, and the tool is a thin adapter around
it.**

The output is a dimuon invariant-mass spectrum with a $Z$ peak at 91 GeV.

## Running it

```bash
conda activate heptapod
jupyter lab building_your_first_tool.ipynb
```

Almost all of it runs with **no API key**. Only Section 4.6, where the two tools
are handed to a live agent, needs one (`OPENAI_API_KEY` or another provider's
key in `.env` at the repository root). Section 5 needs `pip install toolbase`.

Everything the notebook creates lands in `sandbox/` and `cms_dimuon/` next to
it. Both are gitignored, and the last cell deletes them.

## Next

- [`../orchestral/orchestral_setup_basics.ipynb`](../orchestral/orchestral_setup_basics.ipynb):
  agents, providers, hooks, and the web UI
- [`../sim/s1_lq_rr/s1_lq_rr_tutorial.ipynb`](../sim/s1_lq_rr/s1_lq_rr_tutorial.ipynb):
  a full BSM workflow (FeynRules, MadGraph, Pythia, analysis)
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md): the checklist for
  contributing a tool to HEPTAPOD itself
