"""
# visualization.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Feynman diagram visualization using FeynGraph's native drawing.

This module provides convenient wrappers around FeynGraph's drawing
functionality for visualizing diagrams.
"""

from typing import Optional, List, Union
from pathlib import Path


def draw_diagram_svg(
    fg_diagram,
    output_file: Optional[str] = None,
    return_svg: bool = False
) -> Optional[str]:
    """
    Draw a FeynGraph diagram as SVG using native FeynGraph drawing.

    Args:
        fg_diagram: FeynGraph diagram object
        output_file: If provided, save SVG to this file
        return_svg: If True, return the SVG string instead of saving

    Returns:
        SVG string if return_svg=True, otherwise None

    Examples:
        >>> from tools.feyngraph import FeynGraphInterface
        >>> interface = FeynGraphInterface("SM")
        >>> fg_diagrams = interface.enumerate_diagrams(["H"], ["b", "bbar"], 0)
        >>> draw_diagram_svg(fg_diagrams[0], "h_to_bb.svg")

        >>> # In Jupyter, diagrams display automatically:
        >>> fg_diagrams[0]  # Shows SVG visualization
    """
    try:
        # FeynGraph diagrams have draw_svg(file) method
        if hasattr(fg_diagram, 'draw_svg'):
            if output_file:
                # FeynGraph writes directly to file
                fg_diagram.draw_svg(output_file)
                print(f"Diagram saved to: {output_file}")

                if return_svg:
                    # Read back the file if SVG string requested
                    with open(output_file, 'r') as f:
                        return f.read()
                return None
            else:
                # Need a temporary file to get SVG data
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as tmp:
                    tmp_path = tmp.name

                fg_diagram.draw_svg(tmp_path)

                with open(tmp_path, 'r') as f:
                    svg_data = f.read()

                # Clean up temp file
                import os
                os.unlink(tmp_path)

                if return_svg:
                    return svg_data
                return None
        else:
            raise AttributeError(
                "FeynGraph diagram object does not have draw_svg() method. "
                "Make sure you're using a recent version of FeynGraph."
            )
    except Exception as e:
        raise RuntimeError(f"Failed to draw diagram: {e}") from e


def draw_diagrams_svg(
    fg_diagrams: List,
    output_file: Optional[str] = None,
    grid_layout: bool = True
) -> Optional[str]:
    """
    Draw multiple FeynGraph diagrams to SVG.

    Args:
        fg_diagrams: List of FeynGraph diagram objects or DiagramContainer
        output_file: Output SVG file path
        grid_layout: If True, arrange diagrams in a grid (default)
                    If False, create separate SVG files (numbered)

    Returns:
        SVG string if no output_file specified, otherwise None

    Examples:
        >>> # Draw all diagrams for a process
        >>> fg_diagrams = interface.enumerate_diagrams(["g", "g"], ["g", "g"], 1)
        >>> draw_diagrams_svg(fg_diagrams, "gg_to_gg_1loop.svg")

        >>> # Create separate files for each diagram
        >>> draw_diagrams_svg(fg_diagrams, "diagram", grid_layout=False)
        >>> # Creates: diagram_0.svg, diagram_1.svg, ...
    """
    if not fg_diagrams:
        raise ValueError("No diagrams to draw")

    # Check if it's a DiagramContainer (has draw_svg method)
    if hasattr(fg_diagrams, 'draw_svg'):
        # DiagramContainer can draw all diagrams at once
        svg_data = fg_diagrams.draw_svg(list(range(len(fg_diagrams))))

        if output_file:
            with open(output_file, 'w') as f:
                f.write(svg_data)
            print(f"Diagrams saved to: {output_file}")
        else:
            return svg_data

        return None

    # Otherwise, it's a list of diagrams
    if grid_layout:
        # For grid layout, we need to manually combine SVGs
        # This is a simplified version - FeynGraph's DiagramContainer does this better
        if output_file:
            print(f"Warning: Grid layout for lists not fully supported yet.")
            print(f"Drawing diagrams separately to {output_file}_*.svg")

        for i, diag in enumerate(fg_diagrams):
            if output_file:
                base = Path(output_file).stem
                ext = Path(output_file).suffix or '.svg'
                file_name = f"{base}_{i}{ext}"
                draw_diagram_svg(diag, file_name)
            else:
                # Just draw first diagram if no output
                return draw_diagram_svg(diag, return_svg=True)
    else:
        # Separate files
        if not output_file:
            raise ValueError("output_file required when grid_layout=False")

        base = Path(output_file).stem
        ext = Path(output_file).suffix or '.svg'

        for i, diag in enumerate(fg_diagrams):
            file_name = f"{base}_{i}{ext}"
            draw_diagram_svg(diag, file_name)

    return None


def draw_diagram_tikz(
    fg_diagram,
    output_file: str
) -> None:
    """
    Draw a FeynGraph diagram as TikZ/LaTeX.

    Args:
        fg_diagram: FeynGraph diagram object
        output_file: Output .tikz file path

    Examples:
        >>> draw_diagram_tikz(fg_diagrams[0], "h_to_bb.tikz")
        >>> # Can be included in LaTeX with \\input{h_to_bb.tikz}
    """
    try:
        if hasattr(fg_diagram, 'draw_tikz'):
            fg_diagram.draw_tikz(output_file)
            print(f"TikZ diagram saved to: {output_file}")
        else:
            raise AttributeError(
                "FeynGraph diagram does not support TikZ output. "
                "This may require a newer version of FeynGraph."
            )
    except Exception as e:
        raise RuntimeError(f"Failed to generate TikZ diagram: {e}") from e


def display_diagram_inline(fg_diagram):
    """
    Display a FeynGraph diagram inline (Jupyter notebooks).

    In Jupyter notebooks, FeynGraph diagrams are displayed automatically
    via the _repr_svg_() method. This function is provided for completeness
    but is usually not needed.

    Args:
        fg_diagram: FeynGraph diagram object

    Returns:
        IPython display object (in Jupyter) or None

    Examples:
        >>> # In Jupyter, these are equivalent:
        >>> fg_diagrams[0]
        >>> display_diagram_inline(fg_diagrams[0])
    """
    try:
        # Check if we're in Jupyter
        from IPython.display import SVG, display

        if hasattr(fg_diagram, '_repr_svg_'):
            svg_data = fg_diagram._repr_svg_()
            return display(SVG(svg_data))
        elif hasattr(fg_diagram, 'draw_svg'):
            svg_data = fg_diagram.draw_svg()
            return display(SVG(svg_data))
        else:
            print("Diagram object does not support SVG rendering")
            return None

    except ImportError:
        print("IPython not available. Use draw_diagram_svg() to save to file.")
        return None


def visualize_ranked_diagrams(
    ranked_diagrams: List,
    output_dir: str = ".",
    max_diagrams: Optional[int] = None,
    prefix: str = "diagram"
) -> None:
    """
    Visualize multiple ranked diagrams, saving them with rank information.

    Args:
        ranked_diagrams: List of RankedDiagram objects from ranking.py
        output_dir: Directory to save diagram files
        max_diagrams: Maximum number of diagrams to visualize (None = all)
        prefix: Prefix for output files

    Examples:
        >>> from tools.feyngraph import enumerate_and_rank_diagrams
        >>> result = enumerate_and_rank_diagrams(["H"], ["b", "bbar"])
        >>> visualize_ranked_diagrams(result.ranked_diagrams, "diagrams/")
        >>> # Creates: diagrams/diagram_rank1_score500.0.svg, etc.
    """
    from .feyngraph_interface import FeynGraphInterface
    from .diagram_converter import DiagramConverter

    # We need to get back the original FeynGraph diagrams
    # This is a bit tricky since we only have the converted Diagrams
    # For now, we'll document that users should save fg_diagrams separately
    # and match them with ranked results

    print("Note: visualize_ranked_diagrams requires original FeynGraph diagrams.")
    print("Recommended usage:")
    print("  1. Save fg_diagrams after enumerate_diagrams()")
    print("  2. Use draw_diagrams_svg(fg_diagrams, ...)")
    print("  3. Match diagram order with ranked_diagrams order")

    # TODO: Consider storing FeynGraph diagram reference in RankedDiagram
    # or creating a round-trip conversion method


# Convenience function for the most common use case
def save_diagram(
    fg_diagram,
    filename: str,
    format: str = "auto"
) -> None:
    """
    Save a diagram to file (convenience function).

    Args:
        fg_diagram: FeynGraph diagram object
        filename: Output filename (extension determines format if format='auto')
        format: Output format: 'svg', 'tikz', or 'auto' (default)

    Examples:
        >>> save_diagram(fg_diagrams[0], "my_diagram.svg")
        >>> save_diagram(fg_diagrams[0], "my_diagram.tikz", format="tikz")
    """
    if format == "auto":
        # Determine from filename
        if filename.endswith('.tikz'):
            format = 'tikz'
        else:
            format = 'svg'

    if format == 'svg':
        draw_diagram_svg(fg_diagram, filename)
    elif format == 'tikz':
        draw_diagram_tikz(fg_diagram, filename)
    else:
        raise ValueError(f"Unknown format: {format}. Use 'svg' or 'tikz'")


if __name__ == "__main__":
    print("FeynGraph diagram visualization module")
    print("\nUsage:")
    print("  draw_diagram_svg(fg_diagram, 'output.svg')  # Save diagram as SVG")
    print("  draw_diagrams_svg(fg_diagrams, 'output.svg')  # Save multiple diagrams")
    print("  save_diagram(fg_diagram, 'diagram.svg')  # Convenience function")
    print("\nIn Jupyter notebooks, diagrams display automatically:")
    print("  fg_diagram  # Automatically shows SVG visualization")
