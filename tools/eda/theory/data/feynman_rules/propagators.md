# Propagators

Node ID: `feynman_rules.propagators`

## Overview

Propagators describe the free propagation of particles between interaction vertices. In FeynCalc, the denominator factor `i/(p^2 - m^2)` is represented by `FAD[{p, m}]` (FeynAmpDenominator), but the **numerator structure must be written separately** for fermions and massive vectors.

---

## Scalar Propagator

**Feynman rule:**

$$\frac{i}{p^2 - m^2}$$

**FeynCalc code:**

```mathematica
(* Scalar propagator: i/(p^2 - m^2) *)
scalarProp = FAD[{p, m}];
```

`FAD[{p, m}]` represents `i/(p^2 - m^2)`. After `FeynAmpDenominator` expansion via `FCI`, this becomes `FeynAmpDenominator[PropagatorDenominator[Momentum[p, D], m]]`.

For a massless scalar:

```mathematica
(* Massless scalar propagator: i/p^2 *)
scalarPropMassless = FAD[p];
```

---

## Fermion Propagator

**Feynman rule:**

$$\frac{i(\not{p} + m)}{p^2 - m^2}$$

**FeynCalc code:**

```mathematica
(* Fermion propagator: i(p-slash + m)/(p^2 - m^2) *)
fermionProp = (GSD[p] + m) FAD[{p, m}];
```

Key points:
- `GSD[p]` is the D-dimensional Feynman slash: $\gamma^\mu p_\mu$ in D dimensions.
- `FAD[{p, m}]` provides only the denominator $i/(p^2 - m^2)$. The numerator $(\not{p} + m)$ must be written explicitly.
- The `i` factor is included inside `FAD` by convention.

For a massless fermion:

```mathematica
(* Massless fermion propagator: i * p-slash / p^2 *)
fermionPropMassless = GSD[p] FAD[p];
```

---

## Massive Vector Propagator

**Feynman rule (unitary gauge):**

$$\frac{-i\left(g^{\mu\nu} - \frac{p^\mu p^\nu}{m^2}\right)}{p^2 - m^2}$$

**FeynCalc code:**

```mathematica
(* Massive vector propagator (unitary gauge) *)
massiveVectorProp = (-MTD[mu, nu] + FVD[p, mu] FVD[p, nu]/mV^2) FAD[{p, mV}];
```

Key points:
- `MTD[mu, nu]` is the D-dimensional metric tensor $g^{\mu\nu}$.
- `FVD[p, mu]` is the D-dimensional four-vector component $p^\mu$.
- The $p^\mu p^\nu / m^2$ term is essential for gauge invariance checks. Dropping it is only valid when the vector couples to conserved currents (Ward identity satisfied).

---

## Massless Vector Propagator (Feynman Gauge)

**Feynman rule:**

$$\frac{-i g^{\mu\nu}}{p^2}$$

**FeynCalc code:**

```mathematica
(* Massless vector propagator in Feynman gauge (xi = 1) *)
masslessVectorProp = -MTD[mu, nu] FAD[p];
```

In a general R_xi gauge, the propagator is:

$$\frac{-i}{p^2}\left(g^{\mu\nu} - (1 - \xi)\frac{p^\mu p^\nu}{p^2}\right)$$

```mathematica
(* General R_xi gauge *)
masslessVectorPropGeneral = (-MTD[mu, nu] + (1 - xi) FVD[p, mu] FVD[p, nu] FAD[p]) FAD[p];
```

Feynman gauge ($\xi = 1$) eliminates the longitudinal piece and is the simplest for calculations.

---

## Multiple Propagators in a Loop

For loop integrals with multiple propagators, chain them inside `FAD`:

```mathematica
(* Two propagators: i^2 / [(k^2 - m1^2)((k-p)^2 - m2^2)] *)
loopDenom = FAD[{k, m1}, {k - p, m2}];
```

This is equivalent to `FeynAmpDenominator[PropagatorDenominator[Momentum[k,D], m1], PropagatorDenominator[Momentum[k-p,D], m2]]`.

---

## Pitfalls

1. **FAD only gives the denominator.** For fermions and massive vectors, you must write the numerator structure (Dirac slashes, metric tensors, momentum vectors) explicitly. `FAD[{p, m}]` is $i/(p^2 - m^2)$, not the full propagator.

2. **Massive vector $p^\mu p^\nu / m^2$ term.** This term is physically important:
   - It enforces the correct number of polarization degrees of freedom (3 for massive, 2 for massless).
   - Dropping it gives wrong results unless the vector couples to exactly conserved currents.
   - For W/Z bosons decaying to fermions, the $p^\mu p^\nu$ term contributes terms proportional to fermion masses.

3. **FCE and FCI notation conversion.** FeynCalc has two notations:
   - **FCI** (FeynCalcInternal): verbose form, e.g., `FeynAmpDenominator[PropagatorDenominator[...]]`
   - **FCE** (FeynCalcExternal): shorthand, e.g., `FAD[{p, m}]`
   - Use `FCE[expr]` to convert internal to shorthand (readable).
   - Use `FCI[expr]` to convert shorthand to internal (for manipulation).
   - Pattern matching in FeynCalc works on FCI form. If matching fails, apply `FCI` first.

4. **Sign conventions.** The metric signature is $(+,-,-,-)$ in FeynCalc. The propagator denominator is $p^2 - m^2$, not $m^2 - p^2$. Wick rotation to Euclidean space flips the sign.

5. **Dimensional regularization.** Use `GSD`, `MTD`, `FVD` (D-dimensional) rather than `GS`, `MT`, `FV` (4-dimensional) to ensure consistent dimensional regularization.

---

## Links

- `feynman_rules.vertices_scalar` -- Scalar and pseudoscalar interaction vertices
- `feynman_rules.vertices_vector` -- Vector and axial-vector interaction vertices
- `feyncalc_reference.momentum_and_indices` -- Momenta, indices, and contractions in FeynCalc
