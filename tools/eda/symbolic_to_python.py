"""
# symbolic_to_python.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Convert Mathematica symbolic expressions to Python callables.

After running FeynCalc via wolframscript, the SYMBOLIC_RESULT markers contain
Mathematica InputForm strings like:

    (3*yb^2*Sqrt[MH^2 - 4*mb^2]*(MH^2 - 4*mb^2))/(16*Pi*MH^2)

This module converts them into:
    1. sympy expressions (for further symbolic manipulation)
    2. Python callables (for fast numerical evaluation without Mathematica)

Typical usage::

    from tools.eda.symbolic_to_python import mathematica_to_callable

    result = runner.run_script("symbolic_width.wl")
    width_expr = result.parsed_results["symbolic"]["width"]

    width_fn = mathematica_to_callable(width_expr, ["MH", "mb", "yb"])
    print(width_fn(125.0, 4.18, 0.017))  # -> 0.00214 GeV
"""

from typing import Dict, List, Optional, Tuple, Union, Callable

import sympy
from sympy.parsing.mathematica import parse_mathematica


def _preprocess_conjugate(expr: sympy.Expr) -> sympy.Expr:
    """Rewrite Mathematica's Conjugate(x) into forms lambdify can handle.

    Mathematica's ``parse_mathematica`` produces an uppercase ``Conjugate``
    Function that neither ``pycode()`` nor ``lambdify(..., 'math')`` support
    natively.

    This function rewrites:
      - x * Conjugate(x)  →  Abs(x)**2   (the |g|² pattern from |M|²)
      - standalone Conjugate(x)  →  conjugate(x)  (sympy built-in)

    The ``mathematica_to_callable`` and ``mathematica_to_python_source``
    functions inject a ``conjugate`` implementation so the result evaluates
    correctly for complex coupling values.
    """
    # Identify the Conjugate function class from Mathematica parsing
    # (it's an uppercase sympy.Function, not sympy.conjugate)
    conj_atoms = [a for a in expr.atoms(sympy.Function)
                  if a.func.__name__ == "Conjugate" and len(a.args) == 1]
    if not conj_atoms:
        return expr

    for ca in conj_atoms:
        inner = ca.args[0]
        if inner.is_Symbol:
            # x * Conjugate(x) → Abs(x)**2
            expr = expr.subs(inner * ca, sympy.Abs(inner)**2)
            # Remaining unpaired Conjugate(x) → conjugate(x) [sympy built-in]
            expr = expr.subs(ca, sympy.conjugate(inner))
    return expr


def mathematica_to_sympy(
    expr_str: str,
) -> sympy.Expr:
    """Parse a Mathematica InputForm string into a sympy expression.

    Args:
        expr_str: Mathematica InputForm string from a SYMBOLIC_RESULT marker.

    Returns:
        sympy expression.

    Raises:
        ValueError: If the expression cannot be parsed.

    Examples::

        >>> mathematica_to_sympy("3*yb^2*MH/(16*Pi)")
        3*MH*yb**2/(16*pi)

        >>> mathematica_to_sympy("Sqrt[MH^2 - 4*mb^2]")
        sqrt(MH**2 - 4*mb**2)
    """
    cleaned = expr_str.strip()
    if not cleaned:
        raise ValueError("Empty expression string")

    try:
        return parse_mathematica(cleaned)
    except Exception as e:
        raise ValueError(
            f"Failed to parse Mathematica expression: {cleaned!r}\n"
            f"Error: {e}"
        ) from e


def mathematica_to_callable(
    expr_str: str,
    variables: List[str],
    modules: str = "math",
) -> Callable:
    """Convert a Mathematica expression to a Python callable.

    The returned function takes positional arguments in the order specified
    by ``variables`` and returns a float.

    Args:
        expr_str: Mathematica InputForm string.
        variables: Ordered list of variable names that become function
            arguments.  Must match symbols in the expression.
        modules: Numeric backend for ``sympy.lambdify``.  Default ``"math"``
            (stdlib).  Use ``"numpy"`` for vectorised evaluation.

    Returns:
        A Python callable ``f(*args) -> float``.

    Raises:
        ValueError: If parsing fails or a requested variable is not found
            in the expression.

    Examples::

        >>> fn = mathematica_to_callable(
        ...     "(3*yb^2*Sqrt[MH^2 - 4*mb^2]*(MH^2 - 4*mb^2))/(16*Pi*MH^2)",
        ...     ["MH", "mb", "yb"],
        ... )
        >>> fn(125.0, 4.18, 0.017)
        0.00214...
    """
    expr = mathematica_to_sympy(expr_str)
    expr = _preprocess_conjugate(expr)
    sym_vars = [sympy.Symbol(v) for v in variables]

    # Validate that all requested variables appear in the expression
    expr_symbols = expr.free_symbols
    expr_symbol_names = {str(s) for s in expr_symbols}
    missing = [v for v in variables if v not in expr_symbol_names]
    if missing:
        raise ValueError(
            f"Variables {missing} not found in expression. "
            f"Expression contains: {sorted(expr_symbol_names)}"
        )

    # If the expression contains conjugate after preprocessing, inject a
    # Python-level implementation so lambdify works with any backend.
    if expr.has(sympy.conjugate):
        extra = {"conjugate": lambda x: complex(x).conjugate()}
        return sympy.lambdify(sym_vars, expr, modules=[extra, modules])

    return sympy.lambdify(sym_vars, expr, modules=modules)


def mathematica_to_python_source(
    expr_str: str,
    variables: List[str],
    function_name: str = "f",
    dimension_comment: bool = False,
) -> str:
    """Convert a Mathematica expression to a Python function source string.

    Useful when you want to inspect or save the generated code rather than
    getting an opaque callable.

    Args:
        expr_str: Mathematica InputForm string.
        variables: Ordered list of variable names.
        function_name: Name for the generated function.
        dimension_comment: If True, include a ``# Dimensions:`` comment
            with inferred mass dimensions above the function definition.

    Returns:
        Python source code defining the function.

    Examples::

        >>> print(mathematica_to_python_source(
        ...     "g^2*M/(48*Pi)", ["M", "g"], "width_Zff"
        ... ))
        import math
        <BLANKLINE>
        def width_Zff(M, g):
            return (1/48)*M*g**2/math.pi
    """
    expr = mathematica_to_sympy(expr_str)
    expr = _preprocess_conjugate(expr)
    sym_vars = [sympy.Symbol(v) for v in variables]

    has_conj = expr.has(sympy.conjugate)

    # pycode() emits math.pi, math.sqrt, etc.  It does not support
    # sympy.conjugate, so we use strict=False and strip comment lines.
    py_expr = sympy.pycode(expr, strict=not has_conj)
    if has_conj:
        py_expr = "\n".join(
            l for l in py_expr.splitlines() if not l.strip().startswith("#")
        )

    args = ", ".join(variables)
    lines = ["import math"]
    if has_conj:
        lines.append("")
        lines.append("conjugate = lambda x: complex(x).conjugate()")

    # Dimensional annotation (optional)
    if dimension_comment:
        try:
            from .dim_analysis import format_dimension_comment
            comment = format_dimension_comment(variables, expr, function_name)
            if comment:
                lines.append("")
                lines.append(comment)
        except Exception:
            pass  # best-effort — don't break code generation

    lines += [
        "",
        f"def {function_name}({args}):",
        f"    return {py_expr}",
    ]
    return "\n".join(lines)


def extract_variables(expr_str: str) -> List[str]:
    """Extract free variable names from a Mathematica expression.

    Useful when you have a symbolic result but don't know which parameters
    appear in it.

    Args:
        expr_str: Mathematica InputForm string.

    Returns:
        Sorted list of variable names (strings).

    Examples::

        >>> extract_variables("3*yb^2*MH/(16*Pi)")
        ['MH', 'yb']
    """
    expr = mathematica_to_sympy(expr_str)
    return sorted(str(s) for s in expr.free_symbols)
