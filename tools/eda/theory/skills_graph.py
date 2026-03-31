"""
# skills_graph.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
"""
Skills Graph — navigable QFT theory knowledge base.

Each node is a markdown document covering a specific QFT topic
(Feynman rules, trace identities, phase space, etc.) with linked
FeynCalc code examples. Nodes link to related topics for navigation.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class SkillsGraph:
    """Navigable graph of QFT theory documents with FeynCalc code."""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"

        self._data_dir = data_dir
        self._graph_path = data_dir / "graph.json"
        self._graph: Dict[str, Any] = {}
        self._nodes: Dict[str, Any] = {}

        if self._graph_path.exists():
            with open(self._graph_path) as f:
                self._graph = json.load(f)
            self._nodes = self._graph.get("nodes", {})

    def get(self, key: str) -> Optional[str]:
        """Return markdown content for a node.

        Args:
            key: Dot-notation node key (e.g., "feynman_rules.vertices_scalar")

        Returns:
            Markdown content string, or None if not found.
        """
        node = self._nodes.get(key)
        if node is None:
            return None

        file_path = self._data_dir / node["file"]
        if not file_path.exists():
            return None

        return file_path.read_text()

    def links(self, key: str) -> List[str]:
        """Return keys of nodes linked from the given node.

        Args:
            key: Node key.

        Returns:
            List of linked node keys.
        """
        node = self._nodes.get(key)
        if node is None:
            return []
        return node.get("links", [])

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Full-text search across all documents.

        Args:
            query: Search text (case-insensitive).
            max_results: Maximum results to return.

        Returns:
            List of dicts with keys: key, title, snippet.
        """
        query_lower = query.lower()
        results = []

        for key, node in self._nodes.items():
            # Search in title
            title = node.get("title", "")
            if query_lower in title.lower():
                results.append({
                    "key": key,
                    "title": title,
                    "match": "title",
                })
                if len(results) >= max_results:
                    break
                continue

            # Search in file content
            file_path = self._data_dir / node["file"]
            if file_path.exists():
                content = file_path.read_text()
                if query_lower in content.lower():
                    # Extract a snippet around the match
                    idx = content.lower().index(query_lower)
                    start = max(0, idx - 80)
                    end = min(len(content), idx + len(query) + 80)
                    snippet = content[start:end].strip()
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."

                    results.append({
                        "key": key,
                        "title": title,
                        "match": "content",
                        "snippet": snippet,
                    })
                    if len(results) >= max_results:
                        break

        return results

    def list_procedures(self) -> List[Dict[str, str]]:
        """List all procedure nodes.

        Returns:
            List of dicts with keys: key, title.
        """
        return [
            {"key": key, "title": node.get("title", "")}
            for key, node in self._nodes.items()
            if node.get("category") == "procedure"
        ]

    def list_all(self) -> List[Dict[str, str]]:
        """List all nodes with key, title, and category.

        Returns:
            List of dicts.
        """
        return [
            {
                "key": key,
                "title": node.get("title", ""),
                "category": node.get("category", ""),
            }
            for key, node in self._nodes.items()
        ]

    def list_by_category(self, category: str) -> List[Dict[str, str]]:
        """List nodes in a given category.

        Args:
            category: One of: procedure, feynman_rules, spin_sums,
                      trace_identities, phase_space, feyncalc_reference,
                      worked_example.

        Returns:
            List of dicts with keys: key, title.
        """
        return [
            {"key": key, "title": node.get("title", "")}
            for key, node in self._nodes.items()
            if node.get("category") == category
        ]
