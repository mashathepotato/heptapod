# Tensor Bilinear Vertices

Node ID: `feynman_rules.vertices_tensor`

## Overview

The tensor bilinear $\bar\psi\sigma^{\mu\nu}\psi$ couples a fermion pair to a rank-2 tensor field (or an antisymmetric combination of two vector indices). Tensor interactions are dimension-5 operators in 4D and are therefore non-renormalizable, appearing in effective field theories (EFTs) such as anomalous magnetic moment operators and dipole transitions.

---

## Definition of sigma^{mu nu}

$$\sigma^{\mu\nu} = \frac{i}{2}[\gamma^\mu, \gamma^\nu] = \frac{i}{2}(\gamma^\mu\gamma^\nu - \gamma^\nu\gamma^\mu)$$

**FeynCalc representation:**

```mathematica
(* sigma^{mu nu} in FeynCalc *)
DiracSigma[GAD[mu], GAD[nu]]
```

`DiracSigma[GAD[mu], GAD[nu]]` is automatically antisymmetric: `DiracSigma[GAD[nu], GAD[mu]]` = `-DiracSigma[GAD[mu], GAD[nu]]`.

Note: Do not write `I/2 (GAD[mu].GAD[nu] - GAD[nu].GAD[mu])` manually. Use `DiracSigma` so that FeynCalc can apply simplification rules.

---

## Tensor Vertex: T-F-Fbar

**Lagrangian:**

$$\mathcal{L}_T = g_T\, \bar\psi\, \sigma^{\mu\nu}\, \psi\, T_{\mu\nu}$$

**Vertex factor:** $ig_T\sigma^{\mu\nu}$

**FeynCalc amplitude:**

```mathematica
(* Tensor bilinear vertex: T(mu,nu) -> F(p1) Fbar(p2) *)
amp = SpinorUBar[p1, m1] . (I gT DiracSigma[GAD[mu], GAD[nu]]) . SpinorV[p2, m2];
```

---

## Magnetic Dipole Operator

The most common physical application is the electromagnetic dipole operator:

$$\mathcal{L}_{\text{dipole}} = \frac{e}{4m}\, a_f\, \bar\psi\, \sigma^{\mu\nu}\, \psi\, F_{\mu\nu}$$

where $a_f$ is the anomalous magnetic moment and $F_{\mu\nu}$ is the electromagnetic field strength tensor.

For a photon with momentum $q$ and polarization $\epsilon$, $F_{\mu\nu} \to i(q_\mu\epsilon_\nu - q_\nu\epsilon_\mu)$:

```mathematica
(* Magnetic dipole interaction with on-shell photon *)
(* F_{mu nu} -> I (q_mu eps_nu - q_nu eps_mu) *)
Fmunu = I (FVD[q, mu] FVD[eps, nu] - FVD[q, nu] FVD[eps, mu]);

(* Effective vertex *)
vertexDipole = (I e af / (4 m)) DiracSigma[GAD[mu], GAD[nu]] * Fmunu;
```

---

## Tensor Vertex with gamma^5

The pseudotensor (electric dipole) operator:

$$\mathcal{L}_{\text{EDM}} = \frac{i}{2}\, d_f\, \bar\psi\, \sigma^{\mu\nu}\gamma^5\, \psi\, F_{\mu\nu}$$

```mathematica
(* Electric dipole moment operator *)
amp = SpinorUBar[p1, m1] . (I df/2 DiracSigma[GAD[mu], GAD[nu]].GA[5]) . SpinorV[p2, m2];
```

This operator violates CP symmetry and is tightly constrained experimentally.

---

## Trace Identities for sigma^{mu nu}

### Trace of sigma alone

$$\mathrm{Tr}[\sigma^{\mu\nu}] = 0$$

```mathematica
(* Verify: *)
DiracTrace[DiracSigma[GAD[mu], GAD[nu]]] // DiracSimplify
(* Result: 0 *)
```

### Trace with two gamma matrices

$$\mathrm{Tr}[\sigma^{\mu\nu}\gamma^\rho\gamma^\sigma] = 4i(g^{\mu\rho}g^{\nu\sigma} - g^{\mu\sigma}g^{\nu\rho})$$

```mathematica
(* Verify: *)
DiracTrace[DiracSigma[GAD[mu], GAD[nu]].GAD[rho].GAD[sigma]] // DiracSimplify
(* Result: 4I (MTD[mu,rho] MTD[nu,sigma] - MTD[mu,sigma] MTD[nu,rho]) *)
```

### Trace of two sigma matrices

$$\mathrm{Tr}[\sigma^{\mu\nu}\sigma^{\rho\sigma}] = 4(g^{\mu\rho}g^{\nu\sigma} - g^{\mu\sigma}g^{\nu\rho})$$

```mathematica
(* Verify: *)
DiracTrace[DiracSigma[GAD[mu], GAD[nu]].DiracSigma[GAD[rho], GAD[sigma]]] // DiracSimplify
(* Result: 4 (MTD[mu,rho] MTD[nu,sigma] - MTD[mu,sigma] MTD[nu,rho]) *)
```

### Trace with gamma^5

$$\mathrm{Tr}[\sigma^{\mu\nu}\gamma^5] = 0$$

$$\mathrm{Tr}[\sigma^{\mu\nu}\sigma^{\rho\sigma}\gamma^5] = -4i\,\epsilon^{\mu\nu\rho\sigma}$$

```mathematica
(* Verify: *)
DiracTrace[DiracSigma[GAD[mu], GAD[nu]].DiracSigma[GAD[rho], GAD[sigma]].GA[5]] // DiracSimplify
(* Result: -4I Eps[LorentzIndex[mu], LorentzIndex[nu], LorentzIndex[rho], LorentzIndex[sigma]] *)
```

---

## Spin-Summed Squared Amplitude

For the tensor vertex $T \to F\bar{F}$:

```mathematica
(* Spin-sum for tensor vertex *)
amp = SpinorUBar[p1, m1] . (I gT DiracSigma[GAD[mu], GAD[nu]]) . SpinorV[p2, m2];
ampSq = amp ComplexConjugate[amp];
ampSqSummed = FermionSpinSum[ampSq] // DiracSimplify;

(* Result involves: *)
(* Tr[DiracSigma[mu,nu].(GSD[p1]+m1).DiracSigma[rho,sigma].(GSD[p2]-m2)] *)
(* which produces terms with metric tensors and momenta *)
```

The contracted result (summing over tensor polarizations if applicable) depends on the specific tensor field. For the dipole operator contracted with $F_{\mu\nu}$, the result simplifies considerably using the on-shell photon conditions.

---

## Dimensional Analysis

The tensor bilinear $\bar\psi\sigma^{\mu\nu}\psi$ has mass dimension 3 in 4D (each fermion field has dimension 3/2). For a coupling to a dimension-2 field strength $F_{\mu\nu}$, the interaction $\bar\psi\sigma^{\mu\nu}\psi F_{\mu\nu}$ has dimension 5, requiring a dimensionful coupling:

$$[\text{coupling}] = \text{mass}^{-1}$$

This confirms the non-renormalizable nature of tensor interactions in 4D. They arise as:
- Loop-induced effective vertices (anomalous magnetic moments)
- Higher-dimensional operators in EFT (dimension-6 SMEFT operators)
- BSM physics at scale $\Lambda$: coupling $\sim 1/\Lambda$

---

## Gordon Identity

The tensor bilinear is related to the vector bilinear via the Gordon identity:

$$\bar{u}(p')\gamma^\mu u(p) = \bar{u}(p')\left[\frac{(p'+p)^\mu}{2m} + \frac{i\sigma^{\mu\nu}(p'-p)_\nu}{2m}\right]u(p)$$

This allows rewriting magnetic moment interactions in terms of form factors:

```mathematica
(* Gordon decomposition: the vertex gamma^mu can be split into *)
(* a "convection current" (p'+p)^mu/(2m) piece and *)
(* a "spin current" sigma^{mu nu} q_nu/(2m) piece *)
(* where q = p' - p is the momentum transfer *)
```

---

## Pitfalls

1. **Use `DiracSigma`, not manual construction.** Writing `I/2 (GAD[mu].GAD[nu] - GAD[nu].GAD[mu])` will not be recognized by FeynCalc's simplification routines. Always use `DiracSigma[GAD[mu], GAD[nu]]`.

2. **Antisymmetry.** $\sigma^{\mu\nu} = -\sigma^{\nu\mu}$, so the tensor field it couples to must also be antisymmetric. Contracting $\sigma^{\mu\nu}$ with a symmetric tensor gives zero.

3. **Non-renormalizability.** Tensor interactions require a mass scale $\Lambda$ in the denominator of the coupling. When computing loop corrections, new counterterms at each order are needed; the theory is predictive only as an EFT below $\Lambda$.

4. **gamma^5 scheme dependence.** The pseudotensor $\sigma^{\mu\nu}\gamma^5$ involves $\gamma^5$ and is sensitive to the dimensional regularization scheme. In the BMHV scheme (FeynCalc default), be careful with D-dimensional vs 4-dimensional components when $\gamma^5$ appears with $\sigma^{\mu\nu}$.

5. **Relation to $[\gamma^\mu, \gamma^\nu]$.** Some references define $\sigma^{\mu\nu} = (i/2)[\gamma^\mu, \gamma^\nu]$ while others use $\sigma^{\mu\nu} = -(i/2)[\gamma^\mu, \gamma^\nu]$. FeynCalc uses $\sigma^{\mu\nu} = (i/2)(\gamma^\mu\gamma^\nu - \gamma^\nu\gamma^\mu)$. Check sign conventions when comparing with literature.

---

## Links

- `feynman_rules.vertices_scalar` -- Scalar and pseudoscalar vertices (simpler Lorentz structure)
- `feynman_rules.vertices_vector` -- Vector and axial-vector vertices (dimension-4 interactions)
- `trace_identities.basic_traces` -- Basic Dirac trace identities used in tensor calculations
- `feyncalc_reference.spinors_and_traces` -- FeynCalc spinor and trace evaluation functions
