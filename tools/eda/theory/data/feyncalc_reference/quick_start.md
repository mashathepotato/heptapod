# FeynCalc Quick Start

## Loading FeynCalc

```mathematica
(* Load FeynCalc — ALWAYS do this first *)
<< FeynCalc`

(* Suppress startup banner if desired *)
$FeynCalcStartupMessages = False;
<< FeynCalc`
```

## Basic workflow for a decay width calculation

```mathematica
<< FeynCalc`

(* Step 1: Write the amplitude *)
amp = SpinorUBar[p1, m1] . (vertexFactor) . SpinorV[p2, m2];

(* Step 2: Complex conjugate *)
ampCC = ComplexConjugate[amp];

(* Step 3: Square and apply spin sums *)
ampSq = amp * ampCC // FermionSpinSum;

(* Step 4: Evaluate traces *)
ampSq = ampSq // DiracSimplify;

(* Step 5: Contract Lorentz indices (if any) *)
ampSq = Contract[ampSq];

(* Step 6: Apply kinematics *)
ampSq = ampSq /. {
  SP[p1, p2] -> (M^2 - m1^2 - m2^2)/2,
  SP[p, p1] -> (M^2 + m1^2 - m2^2)/2,
  SP[p, p2] -> (M^2 + m2^2 - m1^2)/2
};

(* Step 7: Compute decay width *)
pMag = Sqrt[M^4 - 2 M^2 (m1^2 + m2^2) + (m1^2 - m2^2)^2] / (2 M);
width = pMag / (8 Pi M^2) * ampSq / spinAvgFactor;

(* Step 8: Numerical evaluation *)
widthNum = width /. {M -> 125.0, m1 -> 4.2, m2 -> 4.2, g -> 0.024};
Print["NUMERICAL_RESULT[width_GeV]: ", N[widthNum]]
```

## Key conventions

- Use `GSD[p]` for D-dimensional slashed momentum (not `GS[p]` which is 4D)
- Use `GAD[mu]` for D-dimensional gamma^mu
- Use `GA[5]` for gamma5 (always 4-dimensional)
- Use `SPD[p,q]` for D-dimensional scalar products in intermediate steps
- Use `SP[p,q]` for 4-dimensional scalar products in final results
- Use `FVD[p,mu]` for D-dimensional four-vectors
- Use `MTD[mu,nu]` for D-dimensional metric tensor

## Links

- feyncalc_reference.spinors_and_traces
- feyncalc_reference.momentum_and_indices
- feyncalc_reference.output_patterns
