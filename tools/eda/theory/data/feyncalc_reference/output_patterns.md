# Output Formatting for Parsing

When writing FeynCalc scripts for RunWolframScript, use structured Print markers so the tool can parse results.

## Marker format

```mathematica
(* Symbolic result -- for algebraic expressions *)
Print["SYMBOLIC_RESULT[name]: ", expr]

(* Numerical result -- for numbers *)
Print["NUMERICAL_RESULT[name]: ", N[expr]]

(* LaTeX result -- for paper-ready formulas *)
Print["LATEX_RESULT[name]: ", ToString[TeXForm[expr]]]

(* Status marker *)
Print["STATUS: complete"]
```

**Important:** For LaTeX output, always use `ToString[TeXForm[expr]]`, not bare `TeXForm[expr]`. Without `ToString`, Mathematica prints the wrapper `TeXForm[...]` literally instead of the actual LaTeX string.

## Example: complete script with markers

```mathematica
<< FeynCalc`

(* Compute H -> bb amplitude squared *)
amp = SpinorUBar[p1, mb] . (I yb) . SpinorV[p2, mb];
ampSq = amp ComplexConjugate[amp] // FermionSpinSum // DiracSimplify;
Print["SYMBOLIC_RESULT[ampSq_symbolic]: ", ampSq]

(* Apply kinematics *)
ampSqKin = ampSq /. {SP[p1, p2] -> (MH^2 - 2 mb^2)/2};
Print["SYMBOLIC_RESULT[ampSq_kinematic]: ", ampSqKin]

(* Numerical evaluation *)
ampSqNum = ampSqKin /. {MH -> 125.0, mb -> 4.18, yb -> 0.024};
Print["NUMERICAL_RESULT[ampSq_numerical]: ", N[ampSqNum]]

(* Decay width *)
pMag = Sqrt[MH^4 - 4 MH^2 mb^2] / (2 MH) /. {MH -> 125, mb -> 4.18};
Nc = 3;  (* color factor — use integer, not 3.0 *)
width = pMag / (8 Pi 125^2) * ampSqNum * Nc;
Print["NUMERICAL_RESULT[width_GeV]: ", N[width]]

(* LaTeX output *)
Print["LATEX_RESULT[width]: ", ToString[TeXForm[width]]]

Print["STATUS: complete"]
```

## Parsed output

The RunWolframScript tool parses these markers and returns them in the JSON response:

```json
{
  "symbolic_results": {
    "ampSq_symbolic": "4 yb^2 (SP[p1,p2] - mb^2)",
    "ampSq_kinematic": "2 yb^2 (MH^2 - 4 mb^2)"
  },
  "numerical_results": {
    "ampSq_numerical": 0.01788,
    "width_GeV": 0.00234
  },
  "status": "complete"
}
```

## Best practices

- Use descriptive names in brackets: `ampSq`, `width_GeV`, `crossSection_pb`
- Print intermediate results for debugging (the LLM can inspect them)
- Always end with `Print["STATUS: complete"]` to confirm the script ran fully
- For very long expressions, use `Short[expr, 5]` inside Print to truncate
- Use integer constants (e.g., `3` not `3.0`) to avoid contaminating symbolic results with machine-precision floats. Mathematica treats `3.0` as approximate, which makes all downstream expressions approximate too (e.g., `1/(24*Pi)` becomes `0.013262...`)

## Pitfalls

- Mathematica may print extra messages (FeynCalc banner, warnings) -- the parser only looks for marker lines
- Use `N[expr]` for numerical results to get floating-point output
- Complex expressions may have line breaks -- the parser reads to end of line
- **TeXForm wrapper:** `Print["...", TeXForm[expr]]` outputs `TeXForm[...]` literally. Always wrap: `Print["...", ToString[TeXForm[expr]]]`
- **Float contamination:** `1.0 * symbolic_expr` forces machine precision. Use `1` not `1.0` for constants like color factors, spin averaging denominators, etc.

## Links

- feyncalc_reference.quick_start
