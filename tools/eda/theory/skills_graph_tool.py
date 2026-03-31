"""
# skills_graph_tool.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
"""
LookupTheory — BaseTool for navigating the QFT skills graph.
"""

import json
from typing import Optional

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .skills_graph import SkillsGraph


class LookupTheory(BaseTool):
    """
    Navigate the QFT theory knowledge base (Skills Graph).

    The knowledge base contains markdown documents covering Feynman rules,
    trace identities, spin sums, phase space formulas, and FeynCalc code
    examples. Documents link to related topics for guided navigation.

    Inputs (runtime):
        action: What to do — one of:
            'get'              — retrieve a document by key
            'search'           — full-text search across all documents
            'links'            — get linked node keys for navigation
            'list_procedures'  — list all procedure documents
            'list_all'         — list all nodes
            'list_category'    — list nodes by category
        key: Node key for 'get' and 'links' (e.g., "feynman_rules.vertices_scalar")
        query: Search text for 'search'
        category: Category for 'list_category' (procedure, feynman_rules,
                  spin_sums, trace_identities, phase_space,
                  feyncalc_reference, worked_example)

    Returns:
        JSON or markdown content depending on the action.
    """

    # --- Runtime fields ---
    action: str = RuntimeField(
        description="Action: 'get', 'search', 'links', 'list_procedures', 'list_all', 'list_category'"
    )
    key: Optional[str] = RuntimeField(
        default=None,
        description="Node key for 'get' and 'links' (e.g., 'procedures.decay_width_1to2')"
    )
    query: Optional[str] = RuntimeField(
        default=None,
        description="Search text for 'search' action"
    )
    category: Optional[str] = RuntimeField(
        default=None,
        description="Category for 'list_category'"
    )

    # --- State fields ---
    base_directory: str = StateField(
        description="Working directory"
    )

    def _run(self) -> str:
        graph = SkillsGraph()

        if self.action == "get":
            if not self.key:
                return self.format_error(
                    error="Missing Parameter",
                    reason="key is required for 'get' action"
                )
            content = graph.get(self.key)
            if content is None:
                # Try to suggest similar keys
                all_keys = [n["key"] for n in graph.list_all()]
                suggestions = [
                    k for k in all_keys
                    if any(part in k for part in self.key.split("."))
                ][:5]
                return self.format_error(
                    error="Not Found",
                    reason=f"No document found for key '{self.key}'",
                    suggestions=suggestions,
                )
            return content

        elif self.action == "search":
            if not self.query:
                return self.format_error(
                    error="Missing Parameter",
                    reason="query is required for 'search' action"
                )
            results = graph.search(self.query)
            return json.dumps({"results": results}, indent=2)

        elif self.action == "links":
            if not self.key:
                return self.format_error(
                    error="Missing Parameter",
                    reason="key is required for 'links' action"
                )
            linked = graph.links(self.key)
            if not linked:
                return json.dumps({"key": self.key, "links": [], "note": "No links found (key may not exist)"})
            # Include titles for each link
            all_nodes = {n["key"]: n["title"] for n in graph.list_all()}
            link_info = [
                {"key": k, "title": all_nodes.get(k, "")}
                for k in linked
            ]
            return json.dumps({"key": self.key, "links": link_info}, indent=2)

        elif self.action == "list_procedures":
            procs = graph.list_procedures()
            return json.dumps({"procedures": procs}, indent=2)

        elif self.action == "list_all":
            nodes = graph.list_all()
            return json.dumps({"nodes": nodes}, indent=2)

        elif self.action == "list_category":
            if not self.category:
                return self.format_error(
                    error="Missing Parameter",
                    reason="category is required for 'list_category' action"
                )
            nodes = graph.list_by_category(self.category)
            return json.dumps({"category": self.category, "nodes": nodes}, indent=2)

        else:
            return self.format_error(
                error="Invalid Action",
                reason=f"Unknown action '{self.action}'. "
                       f"Use: get, search, links, list_procedures, list_all, list_category"
            )
