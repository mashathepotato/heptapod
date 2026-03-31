# Momenta, Indices, and Contractions in FeynCalc

## Momentum objects

| FeynCalc | Physics | Description |
|----------|---------|-------------|
| `GSD[p]` | gamma dot p (D-dim) | Slashed momentum, D-dimensional |
| `GS[p]` | gamma dot p (4-dim) | Slashed momentum, 4-dimensional |
| `FVD[p, mu]` | p^mu (D-dim) | Four-vector component |
| `FV[p, mu]` | p^mu (4-dim) | Four-vector component |
| `SPD[p, q]` | p dot q (D-dim) | Scalar product |
| `SP[p, q]` | p dot q (4-dim) | Scalar product |
| `MTD[mu, nu]` | g^{mu nu} (D-dim) | Metric tensor |
| `MT[mu, nu]` | g^{mu nu} (4-dim) | Metric tensor |

## Gamma matrices

| FeynCalc | Physics | Description |
|----------|---------|-------------|
| `GAD[mu]` | gamma^mu (D-dim) | Gamma matrix with Lorentz index |
| `GA[mu]` | gamma^mu (4-dim) | Gamma matrix with Lorentz index |
| `GA[5]` | gamma5 | Always 4-dimensional |
| `DiracSigma[GAD[mu], GAD[nu]]` | sigma^{mu nu} | Tensor: (i/2)[gamma^mu, gamma^nu] |

## Feynman Amplitude Denominators

```mathematica
(* Scalar propagator denominator: i/(p^2 - m^2) *)
FAD[{p, m}]

(* Massless: i/p^2 *)
FAD[p]

(* Product of propagators *)
FAD[{q, m1}, {q - p, m2}]  (* = i/(q^2 - m1^2) * i/((q-p)^2 - m2^2) *)
```

## Contract

```mathematica
(* Contract all matching Lorentz indices *)
Contract[expr]

(* Examples *)
Contract[FVD[p, mu] FVD[q, mu]]       (* -> SPD[p, q] *)
Contract[MTD[mu, nu] GAD[mu]]          (* -> GAD[nu] *)
Contract[FVD[p, mu] GAD[mu]]           (* -> GSD[p] *)
```

## SetMandelstam -- for 2->2 scattering

```mathematica
(* Define Mandelstam variables for p1 + p2 -> p3 + p4 *)
(* Note: outgoing momenta get minus signs *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, m1, m2, m3, m4];

(* This automatically sets all scalar products *)
(* SP[p1,p2] -> (s - m1^2 - m2^2)/2 *)
(* SP[p1,p3] -> (m1^2 + m3^2 - t)/2 *)
(* etc. *)
```

## TrickMandelstam -- simplify using s+t+u constraint

```mathematica
TrickMandelstam[expr, {s, t, u, m1^2 + m2^2 + m3^2 + m4^2}]
```

## FCE and FCI -- notation conversion

```mathematica
(* Convert internal -> external (human-readable) *)
FCE[Pair[Momentum[p, D], Momentum[q, D]]]  (* -> SPD[p, q] *)

(* Convert external -> internal *)
FCI[SPD[p, q]]  (* -> Pair[Momentum[p, D], Momentum[q, D]] *)
```

## Pitfalls

- Use D-dimensional objects (`GSD`, `GAD`, `SPD`, `FVD`, `MTD`) for consistency
- `SP` vs `SPD`: after all traces are evaluated and you're ready for numerics, 4D `SP` is fine
- `Contract` contracts ALL pairs of matching indices -- be careful with multiple dummy indices
- `SetMandelstam` with minus signs on outgoing momenta: `SetMandelstam[s, t, u, p1, p2, -p3, -p4, ...]`

## Links

- feyncalc_reference.quick_start
- feyncalc_reference.spinors_and_traces
- trace_identities.contraction_identities
