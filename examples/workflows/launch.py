"""
# launch.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""

"""Launch a coding agent on the BSM event-generation pipeline (the MCP counterpart to hep_bsm_demo.py).

Usage:
    python examples/workflows/launch.py --harness claude-code
    python examples/workflows/launch.py --harness codex
    python examples/workflows/launch.py --harness opencode
"""

# Setup repository path for imports
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'shared'))

from harness_launch import main

main(
    example='hep_bsm',
    bundles=['feynrules', 'mg5', 'event_gen', 'analysis'],
    prompt_path=REPO_ROOT / 'prompts/examples/hep_bsm/system/hep_bsm_evt_gen_explorer_prompt.md',
    sandbox_dir=REPO_ROOT / 'examples' / 'hep_bsm_sandbox',
    mode='explorer',
    config_keys=['feynrules_path', 'mg5_path', 'wolframscript_path'],
)
