"""
# dim_analysis.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

Dimensional analysis for Mathematica-to-Python converted expressions.

Infers the mass dimension of variables from naming conventions used by
FeynCalc code generation (feyncalc_codegen.py) and computes the overall
mass dimension of a sympy expression tree.

Naming conventions:
    mX, MX        -> mass^1  (particle masses)
    gX, yX, e     -> mass^0  (dimensionless couplings in 4D)
    GF, G_F       -> mass^-2 (Fermi constant)
    s, t, u       -> mass^2  (Mandelstam variables)
    v, vev        -> mass^1  (Higgs VEV)
    Lambda        -> mass^1  (energy scale)
"""

import re
from fractions import Fraction
from typing import Dict, List, Optional, Union

import sympy


# --- Exact-match table (highest priority) ---
_EXACT_DIMS: Dict[str, int] = {
    "GF": -2,
    "G_F": -2,
    "s": 2,
    "t": 2,
    "u": 2,
    "v": 1,
    "vev": 1,
    "Lambda": 1,
    "LambdaQCD": 1,
}

# Patterns checked in order after exact match fails.
# Each entry: (compiled regex, mass dimension)
_PATTERN_DIMS: list[tuple[re.Pattern, int]] = [
    # Masses: m followed by uppercase letter (mS, mH, mV, mf1, mfbar, ...)
    (re.compile(r"^m[A-Z]"), 1),
    # Masses: m followed by lowercase then more chars (mf, mfbar, mprop0, ...)
    (re.compile(r"^m[a-z]"), 1),
    # Masses: M alone or M followed by uppercase (M, MH, MZ, MW, ...)
    (re.compile(r"^M[A-Z_]"), 1),
    (re.compile(r"^M$"), 1),
    # Propagator masses: mProp0, etc.
    (re.compile(r"^mProp"), 1),
    # Couplings: g alone or g followed by uppercase (g, gV, gA, gL, gR, gS, gP)
    (re.compile(r"^g[A-Z]"), 0),
    (re.compile(r"^g$"), 0),
    # Yukawa couplings: y alone or y followed by lowercase (y, yb, yt, ye)
    (re.compile(r"^y[a-z]?$"), 0),
    # Electric charge and fine-structure constants
    (re.compile(r"^e$"), 0),
    (re.compile(r"^alpha"), 0),
]


def infer_mass_dimension(var_name: str) -> Optional[int]:
    """Infer the mass dimension of a variable from its name.

    Returns:
        Integer mass dimension, or None if the variable cannot be classified.

    Examples::
        >>> infer_mass_dimension("mH")
        1
        >>> infer_mass_dimension("gV")
        0
        >>> infer_mass_dimension("GF")
        -2
        >>> infer_mass_dimension("unknown_x")  # returns None
    """
    # 1. Exact match
    if var_name in _EXACT_DIMS:
        return _EXACT_DIMS[var_name]

    # 2. Pattern match (first match wins)
    for pattern, dim in _PATTERN_DIMS:
        if pattern.match(var_name):
            return dim

    return None


def compute_expression_dimension(
    expr: sympy.Expr,
    var_dims: Dict[str, Optional[int]],
) -> Optional[Fraction]:
    """Compute the mass dimension of a sympy expression.

    Walks the expression tree and combines dimensions according to:
      - Symbol(x)     -> var_dims[x]
      - Number        -> 0
      - Mul(a, b)     -> dim(a) + dim(b)
      - Pow(a, n)     -> dim(a) * n
      - Add(a, b)     -> dim(a) if dim(a) == dim(b), else None
      - Abs(x)        -> dim(x)
      - conjugate(x)  -> dim(x)
      - pi            -> 0

    Returns:
        Mass dimension as a Fraction, or None if it cannot be determined.
    """
    return _dim_of(expr, var_dims)


def _dim_of(
    expr: sympy.Expr,
    var_dims: Dict[str, Optional[int]],
) -> Optional[Fraction]:
    """Recursive dimension walker."""

    # --- Numeric constants ---
    if expr.is_Number:
        return Fraction(0)

    # --- pi ---
    if expr is sympy.pi:
        return Fraction(0)

    # --- Symbol ---
    if expr.is_Symbol:
        name = str(expr)
        d = var_dims.get(name)
        if d is None:
            return None
        return Fraction(d)

    # --- Abs ---
    if isinstance(expr, sympy.Abs):
        return _dim_of(expr.args[0], var_dims)

    # --- conjugate ---
    if isinstance(expr, sympy.conjugate):
        return _dim_of(expr.args[0], var_dims)

    # --- Mul: sum of dimensions ---
    if expr.is_Mul:
        total = Fraction(0)
        for arg in expr.args:
            d = _dim_of(arg, var_dims)
            if d is None:
                return None
            total += d
        return total

    # --- Pow: dim(base) * exponent ---
    if expr.is_Pow:
        base, exp = expr.args
        d_base = _dim_of(base, var_dims)
        if d_base is None:
            return None
        # Exponent must be a number for dimensional analysis
        if exp.is_Number:
            return d_base * Fraction(exp).limit_denominator(100)
        # Symbolic exponent (e.g., x^n) — can't determine dimension
        return None

    # --- Add: all terms must have same dimension ---
    if expr.is_Add:
        dims = []
        for arg in expr.args:
            d = _dim_of(arg, var_dims)
            if d is None:
                return None
            dims.append(d)
        if len(set(dims)) == 1:
            return dims[0]
        # Dimensional mismatch (may indicate inference error, not physics error)
        return None

    # --- Functions (sqrt is Pow(x, 1/2), already handled) ---
    # For any unrecognized function, return None
    return None


def _format_dim(d: Fraction) -> str:
    """Format a dimension value for display."""
    if d == 0:
        return "dimensionless"
    if d == 1:
        return "mass"
    if d.denominator == 1:
        return f"mass^{d.numerator}"
    return f"mass^({d})"


def format_dimension_comment(
    var_list: List[str],
    expr: sympy.Expr,
    function_name: str = "result",
) -> Optional[str]:
    """Build a dimensional annotation comment for generated Python code.

    Returns:
        A comment string like:
          # Dimensions: [width] = mass, [g] = dimensionless, [mV] = mass
        or None if dimensions cannot be determined.
    """
    # Infer variable dimensions
    var_dims: Dict[str, Optional[int]] = {}
    for v in var_list:
        var_dims[v] = infer_mass_dimension(v)

    # Check if any variables are unknown
    unknowns = [v for v in var_list if var_dims[v] is None]

    # Compute expression dimension
    expr_dim = compute_expression_dimension(expr, var_dims)

    # Build comment parts
    parts = []

    # Result dimension
    if expr_dim is not None:
        parts.append(f"[{function_name}] = {_format_dim(expr_dim)}")
    elif unknowns:
        parts.append(
            f"[{function_name}] = unknown "
            f"(variable{'s' if len(unknowns) > 1 else ''} "
            f"{', '.join(repr(u) for u in unknowns)} "
            f"ha{'ve' if len(unknowns) > 1 else 's'} unknown dimension)"
        )
    else:
        parts.append(f"[{function_name}] = unknown")

    # Variable dimensions
    for v in var_list:
        d = var_dims[v]
        if d is not None:
            parts.append(f"[{v}] = {_format_dim(Fraction(d))}")
        else:
            parts.append(f"[{v}] = unknown")

    return f"# Dimensions: {', '.join(parts)}"
