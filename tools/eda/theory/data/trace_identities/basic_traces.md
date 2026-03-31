# Basic Dirac Trace Identities

## Fundamental traces

The trace of the identity matrix in spinor space:

$$\text{Tr}[\mathbf{1}] = 4$$

Trace of two gamma matrices:

$$\text{Tr}[\gamma^\mu \gamma^\nu] = 4 g^{\mu\nu}$$

Trace of four gamma matrices:

$$\text{Tr}[\gamma^\mu \gamma^\nu \gamma^\rho \gamma^\sigma] = 4(g^{\mu\nu}g^{\rho\sigma} - g^{\mu\rho}g^{\nu\sigma} + g^{\mu\sigma}g^{\nu\rho})$$

## With slashed momenta

$$\text{Tr}[\not{a}\not{b}] = 4\, a \cdot b$$

$$\text{Tr}[\not{a}\not{b}\not{c}\not{d}] = 4[(a \cdot b)(c \cdot d) - (a \cdot c)(b \cdot d) + (a \cdot d)(b \cdot c)]$$

## FeynCalc code

```mathematica
<< FeynCalc`

(* Trace of two slashed momenta *)
DiracTrace[GSD[p] . GSD[q]] // DiracSimplify
(* Result: 4 SP[p, q] *)

(* Trace of four slashed momenta *)
DiracTrace[GSD[a] . GSD[b] . GSD[c] . GSD[d]] // DiracSimplify
(* Result: 4 (SP[a,b] SP[c,d] - SP[a,c] SP[b,d] + SP[a,d] SP[b,c]) *)

(* Trace with mass terms: Tr[(p-slash + m)(q-slash - m)] *)
DiracTrace[(GSD[p] + m) . (GSD[q] - m)] // DiracSimplify
(* Result: 4 SP[p,q] - 4 m^2 *)
```

## General rule

- Trace of an even number 2n of gamma matrices: sum over all pairings with alternating signs.
- Each pairing contributes a product of n metric tensors.

## Pitfalls

- Use `DiracTrace[...]` not `Tr[...]` -- FeynCalc's DiracTrace knows about gamma matrix algebra.
- Always call `DiracSimplify` after `DiracTrace` to fully simplify.
- In D dimensions, Tr[1] = 4 (not D) by FeynCalc convention with standard settings.

## Links

- trace_identities.gamma5_traces
- trace_identities.trace_of_odd
- trace_identities.contraction_identities
- feyncalc_reference.spinors_and_traces
