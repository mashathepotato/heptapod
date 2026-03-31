# Traces with gamma-5

## Key identities

$$\text{Tr}[\gamma^5] = 0$$

$$\text{Tr}[\gamma^\mu \gamma^\nu \gamma^5] = 0$$

$$\text{Tr}[\gamma^\mu \gamma^\nu \gamma^\rho \gamma^\sigma \gamma^5] = -4i\,\varepsilon^{\mu\nu\rho\sigma}$$

## With slashed momenta

$$\text{Tr}[\not{a}\not{b}\gamma^5] = 0$$

$$\text{Tr}[\not{a}\not{b}\not{c}\not{d}\gamma^5] = -4i\,\varepsilon^{\mu\nu\rho\sigma} a_\mu b_\nu c_\rho d_\sigma$$

## Properties of gamma-5

- $(\gamma^5)^2 = 1$
- $\{\gamma^5, \gamma^\mu\} = 0$ (anticommutes with all gamma matrices)
- $\gamma^5 = i\gamma^0\gamma^1\gamma^2\gamma^3$

## FeynCalc code

```mathematica
<< FeynCalc`

(* Trace with gamma5 - vanishes for less than 4 gammas *)
DiracTrace[GSD[a] . GSD[b] . GA[5]] // DiracSimplify
(* Result: 0 *)

(* Trace of 4 gammas with gamma5 *)
DiracTrace[GSD[a] . GSD[b] . GSD[c] . GSD[d] . GA[5]] // DiracSimplify
(* Result: -4 I Eps[Momentum[a], Momentum[b], Momentum[c], Momentum[d]] *)

(* V-A structure common in electroweak: Tr[(gV - gA gamma5) gamma^mu (p-slash + m1) gamma^nu (q-slash - m2)] *)
DiracTrace[(gV - gA GA[5]) . GAD[mu] . (GSD[p] + m1) . GAD[nu] . (GSD[q] - m2)] // DiracSimplify
```

## Useful combined traces for V-A vertices

For $Z \to f\bar{f}$ type calculations with vertex $ig\gamma^\mu(g_V - g_A\gamma^5)$:

$$\text{Tr}[(g_V - g_A\gamma^5)\gamma^\mu(\not{p_1}+m)\gamma^\nu(\not{p_2}-m)]$$

This decomposes as follows:

- The pure V part ($g_V^2$ trace) gives the standard vector coupling result.
- The pure A part ($g_A^2$ trace) gives the same form as the vector result, because $(\gamma^5)^2 = 1$.
- The V x A cross term is proportional to the Levi-Civita tensor and vanishes when contracted with a symmetric polarization sum.

## Pitfalls

- gamma-5 is intrinsically 4-dimensional. In D-dimensional regularization, use FeynCalc's `GA[5]` (always 4D).
- Never use `GAD[5]` -- it does not exist. gamma-5 is always `GA[5]`.
- The Levi-Civita tensor in FeynCalc is `Eps[LorentzIndex[mu], LorentzIndex[nu], LorentzIndex[rho], LorentzIndex[sigma]]`.
- Sign conventions for the Levi-Civita tensor vary between textbooks.

## Links

- trace_identities.basic_traces
- feynman_rules.vertices_vector
- feyncalc_reference.spinors_and_traces
