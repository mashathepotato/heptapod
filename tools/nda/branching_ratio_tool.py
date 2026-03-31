"""
# branching_ratio_tool.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Branching ratio estimation tool using NDA.

Computes NDA-level branching ratios for multiple diagram classes by
running EstimateDecayWidthNDA on each class and dividing by a reference
total width.
"""
import json
import os
from typing import Optional, Dict, Any, List

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .nda_tool import EstimateDecayWidthNDATool
from .simple_diagram import parse_diagram
from .summary_formatting import format_multi_diagram_summary


class EstimateBranchingRatioNDATool(BaseTool):
    """
    Estimates branching ratios using NDA for multiple diagram classes.

    Takes a list of diagram classes and a reference total width, computes the
    NDA partial width for each class, and returns branching ratios.

    Workflow:
      1. First compute the total width of the dominant decay channel using
         `EstimateDecayWidthNDA` (or use an experimental value).
      2. Call `EnumerateDiagrams` to get diagrams for the rare channel.
      3. Group diagrams by topology or propagator count into classes.
      4. Pass the diagram classes and reference width to this tool.

    Each diagram class needs:
      {"diagram": {...}, "n_diagrams": N}
    or by path:
      {"diagram_path": "path/to/diagram.json", "n_diagrams": N}

    The ``diagram_path`` accepts:
      - A JSON file (auto-unwraps EnumerateDiagrams' ``{"rank": N, "diagram": {...}}`` format)
      - A directory (auto-selects ``representative.json`` or the top-ranked file)

    ``EnumerateDiagrams`` with ``metadata_only=True`` returns a ``br_classes``
    array that can be passed directly as ``diagram_classes``.

    Input:
      diagram_classes: List of diagram class dicts, each with:
        - "diagram": diagram specification (same format as EstimateDecayWidthNDA)
          OR "diagram_path": path to a JSON file or directory
        - "n_diagrams": number of diagrams in this class (for incoherent sum)
        - "n_heavy": (optional) number of heavy propagators (for display)
      reference_width: Total width in GeV of the mother particle (e.g., from
        a prior NDA call on the dominant channel, or an experimental value)
      reference_label: Label for the reference (default: "Total width")
      process_label: Process label for the summary table

    Returns:
      {
        "status": "ok",
        "n_classes": 2,
        "n_diagrams_total": 15,
        "total_partial_width": 1.23e-20,
        "total_br": 4.56e-10,
        "reference_width": 3.00e-19,
        "class_results": [...],
        "summary_table": "..."
      }

    Note on widths: Each class_result contains "width_nda" which is the
    per-diagram width (not multiplied by n_diagrams). The "total_partial_width"
    is the incoherent sum: sum(width_nda * n_diagrams) over all classes.
    """

    # ======================== Runtime fields ======================== #
    diagram_classes: List[Dict[str, Any]] = RuntimeField(
        description=(
            "List of diagram class dicts for multi-class NDA analysis. Each dict should have: "
            "'diagram' (diagram spec dict) OR 'diagram_path' (path to a JSON file containing "
            "the diagram spec), plus 'n_diagrams' (count in class). "
            "When provided, computes NDA for each class and generates full summary table."
        )
    )
    reference_width: float = RuntimeField(
        description=(
            "Reference total width in GeV for BR calculation. This is the total width "
            "of the mother particle — either from a prior NDA call on the dominant "
            "decay channel, or an experimental value."
        )
    )
    reference_label: str = RuntimeField(
        description="Label for the reference width (default: 'Total width')",
        default="Total width"
    )
    process_label: Optional[str] = RuntimeField(
        description="Process label for summary (e.g., 'μ⁻ → e⁻e⁺e⁻ν̄ₑνμ')",
        default=None
    )
    include_summary: bool = RuntimeField(
        description="Include formatted markdown summary table in output (default: True)",
        default=True
    )
    # ================================================================ #

    # ========================= State fields ========================= #
    base_directory: str = StateField(
        description="Base sandbox directory for file operations"
    )
    # ================================================================ #

    def _setup(self):
        """Validate and initialize."""
        self.base_directory = os.path.abspath(self.base_directory)
        if not os.path.isdir(self.base_directory):
            raise ValueError(f"Base directory does not exist: {self.base_directory}")

    def _run(self) -> str:
        """
        Main execution method.

        Returns:
            JSON string with branching ratio results and summary table
        """
        try:
            self._setup()
        except Exception as e:
            return self.format_error(
                error="Setup Error",
                reason=str(e)
            )

        if not self.diagram_classes:
            return self.format_error(
                error="Empty diagram_classes",
                reason="diagram_classes list is empty",
                suggestion="Provide at least one diagram class"
            )

        if self.reference_width is None or self.reference_width <= 0:
            return self.format_error(
                error="Invalid reference_width",
                reason="reference_width must be a positive number (in GeV)",
                suggestion=(
                    "First compute the total width using EstimateDecayWidthNDA "
                    "on the dominant channel, then pass that as reference_width."
                )
            )

        # Process each diagram class
        all_results = []
        errors = []

        for i, dc in enumerate(self.diagram_classes):
            diagram = dc.get("diagram")
            diagram_path = dc.get("diagram_path")
            n_heavy = dc.get("n_heavy", 0)
            n_diagrams = dc.get("n_diagrams", 1)

            # Load diagram from file path if provided
            if diagram is None and diagram_path is not None:
                try:
                    resolved = os.path.expanduser(diagram_path)
                    if not os.path.isabs(resolved):
                        resolved = os.path.join(self.base_directory, resolved)

                    # If path is a directory, auto-select the representative diagram
                    if os.path.isdir(resolved):
                        # Prefer representative.json (created by EnumerateDiagrams)
                        rep_path = os.path.join(resolved, "representative.json")
                        if os.path.exists(rep_path):
                            resolved = rep_path
                        else:
                            import glob as glob_mod
                            candidates = sorted(glob_mod.glob(os.path.join(resolved, "diagram_*_rank*.json")))
                            if not candidates:
                                candidates = sorted(glob_mod.glob(os.path.join(resolved, "*.json")))
                            if not candidates:
                                errors.append(f"Class {i}: no diagram JSON files found in '{diagram_path}'")
                                continue
                            resolved = candidates[0]

                    with open(resolved, 'r') as f:
                        loaded = json.load(f)
                    # Unwrap EnumerateDiagrams output format if needed:
                    # Files from EnumerateDiagrams have {"rank": N, "diagram": {...}, ...}
                    # The BR tool needs the inner "diagram" dict.
                    if "diagram" in loaded and "initial" not in loaded:
                        diagram = loaded["diagram"]
                    else:
                        diagram = loaded
                except Exception as e:
                    errors.append(f"Class {i}: failed to load diagram from '{diagram_path}': {e}")
                    continue

            if diagram is None:
                errors.append(f"Class {i}: missing 'diagram' or 'diagram_path' key")
                continue

            # Unwrap EnumerateDiagrams output format if needed
            if "diagram" in diagram and "initial" not in diagram:
                diagram = diagram["diagram"]

            # Compute NDA for this diagram
            try:
                parsed = parse_diagram(diagram)
                is_valid, warnings = parsed.validate()
                if not is_valid:
                    errors.append(
                        f"Class {i} (n_heavy={n_heavy}): diagram validation failed: "
                        f"{'; '.join(warnings)}"
                    )
                    continue

                # Run single-diagram NDA
                single_tool = EstimateDecayWidthNDATool(
                    diagram=diagram,
                    include_summary=False,
                    base_directory=self.base_directory
                )
                result_json = single_tool._run()
                result = json.loads(result_json)

                if result.get("status") != "ok":
                    errors.append(f"Class {i}: {result.get('error', 'NDA failed')}")
                    continue

                width_nda = result.get("width_gev", 0)
                formula = result.get("formula", "-")

                # Get coupling info from vertices
                vertices = diagram.get("vertices", [])
                n_vertices = len(vertices)
                couplings_latex = f"g^{n_vertices}" if n_vertices > 0 else "-"

                all_results.append({
                    "n_heavy": n_heavy,
                    "n_diagrams": n_diagrams,
                    "width_per_diagram": width_nda,
                    "formula": formula,
                    "couplings_latex": couplings_latex
                })

            except Exception as e:
                errors.append(f"Class {i}: {str(e)}")
                continue

        if not all_results:
            return self.format_error(
                error="All Classes Failed",
                reason="; ".join(errors) if errors else "No valid results",
                suggestion="Check diagram_classes format"
            )

        # Calculate totals
        total_partial_width = sum(
            r["width_per_diagram"] * r["n_diagrams"] for r in all_results
        )
        total_diagrams = sum(r["n_diagrams"] for r in all_results)
        total_br = total_partial_width / self.reference_width if self.reference_width > 0 else 0

        # Build result
        result = {
            "status": "ok",
            "n_classes": len(all_results),
            "n_diagrams_total": total_diagrams,
            "partial_width_gev": total_partial_width,
            "branching_ratio": total_br,
            "reference_width_gev": self.reference_width,
            "reference_label": self.reference_label,
            "class_results": all_results,
        }

        if errors:
            result["warnings"] = errors

        # Generate summary table
        if self.include_summary:
            summary_table = format_multi_diagram_summary(
                results=all_results,
                process_label=self.process_label or "Multi-class NDA",
                reference_width=self.reference_width,
                include_formula=True,
                include_physics_note=True
            )
            result["summary_table"] = summary_table

            # Save summary to file
            if self.base_directory:
                process_safe = (self.process_label or "multi_class").replace(
                    " ", "_").replace("→", "to").replace("->", "to")
                summary_filename = f"nda_br_summary_{process_safe}.md"
                summary_filepath = os.path.join(self.base_directory, summary_filename)
                try:
                    with open(summary_filepath, 'w') as f:
                        f.write(summary_table)
                    result["summary_file"] = summary_filepath
                except Exception:
                    pass  # Non-critical if file save fails

        return json.dumps(result, separators=(",", ":"), ensure_ascii=False)
