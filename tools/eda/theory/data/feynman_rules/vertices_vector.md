# Vector and Axial-Vector Vertices

Node ID: `feynman_rules.vertices_vector`

## Overview

Vector (V) and axial-vector (A) interactions couple a spin-1 boson to a fermion-antifermion pair through $\gamma^\mu$ and $\gamma^\mu\gamma^5$ structures respectively. The electroweak Standard Model uses a V-A combination for charged currents (W boson) and a general V-A mixture for neutral currents (Z boson). QED is a pure vector interaction.

---

## Pure Vector Vertex: V-F-Fbar

**Lagrangian:**

$$\mathcal{L}_V = g_V\, \bar\psi \gamma^\mu \psi\, V_\mu$$

**Vertex factor:** $ig_V\gamma^\mu$

**FeynCalc amplitude for V(mu, q) -> F(p1) Fbar(p2):**

```mathematica
(* Vector vertex: V(mu) -> F Fbar, e.g. QED photon vertex *)
amp = SpinorUBar[p1, m1] . (I gV GAD[mu]) . SpinorV[p2, m2];
```

After spin-summing (fermions) and polarization-summing (vector boson):

```mathematica
(* |M|^2 summed over all spins and polarizations *)
ampSq = amp ComplexConjugate[amp];
ampSqSummed = FermionSpinSum[ampSq] // DiracSimplify;

(* For massive vector: polarization sum = -g^{mu nu} + q^mu q^nu / mV^2 *)
(* For massless vector: polarization sum = -g^{mu nu} (in Feynman gauge) *)

(* Massive vector polarization sum *)
ampSqPol = ampSqSummed /. {
  Pair[LorentzIndex[mu, D], LorentzIndex[nu, D]] ->
    -MTD[mu, nu] + FVD[q, mu] FVD[q, nu]/mV^2
};
```

The spin-summed trace for a pure vector vertex gives:

$$\mathrm{Tr}[\gamma^\mu(\not{p}_1+m_1)\gamma^\nu(\not{p}_2-m_2)] = 4\left[p_1^\mu p_2^\nu + p_1^\nu p_2^\mu - g^{\mu\nu}(p_1 \cdot p_2 - m_1 m_2)\right]$$

---

## Pure Axial-Vector Vertex: A-F-Fbar

**Lagrangian:**

$$\mathcal{L}_A = g_A\, \bar\psi \gamma^\mu\gamma^5 \psi\, V_\mu$$

**Vertex factor:** $ig_A\gamma^\mu\gamma^5$

**FeynCalc amplitude:**

```mathematica
(* Axial-vector vertex: V(mu) -> F Fbar *)
amp = SpinorUBar[p1, m1] . (I gA GAD[mu].GA[5]) . SpinorV[p2, m2];
```

The spin-summed trace for a pure axial-vector vertex gives:

$$\mathrm{Tr}[\gamma^\mu\gamma^5(\not{p}_1+m_1)\gamma^\nu\gamma^5(\not{p}_2-m_2)] = 4\left[p_1^\mu p_2^\nu + p_1^\nu p_2^\mu - g^{\mu\nu}(p_1 \cdot p_2 + m_1 m_2)\right]$$

Note the sign flip $-m_1 m_2 \to +m_1 m_2$ compared to the vector case, analogous to the scalar vs pseudoscalar distinction.

---

## V-A Vertex (Electroweak Neutral Current)

**Lagrangian (Z boson coupling):**

$$\mathcal{L}_Z = \frac{g}{\cos\theta_W}\, \bar\psi \gamma^\mu(g_V^f - g_A^f \gamma^5) \psi\, Z_\mu$$

**Vertex factor:** $i\frac{g}{\cos\theta_W}\gamma^\mu(g_V^f - g_A^f\gamma^5)$

**FeynCalc amplitude for Z(mu) -> f(p1) fbar(p2):**

```mathematica
(* Z boson vertex: Z(mu) -> f fbar with V-A structure *)
(* gVf and gAf are the vector and axial couplings for fermion f *)
amp = SpinorUBar[p1, mf] . (I gz GAD[mu].(gVf - gAf GA[5])) . SpinorV[p2, mf];
```

where `gz = g / cosThW`.

After spin sum, the squared amplitude contains three types of traces:

```mathematica
(* The V-A structure produces three trace contributions: *)
(* VV: gVf^2 * Tr[gamma^mu (p1+m) gamma^nu (p2-m)] *)
(* AA: gAf^2 * Tr[gamma^mu g5 (p1+m) gamma^nu g5 (p2-m)] *)
(* VA: -2 gVf gAf * Tr[gamma^mu g5 (p1+m) gamma^nu (p2-m)] *)
(* The VA cross-term involves Tr[gamma^mu gamma^nu gamma^rho gamma^sigma gamma^5] *)
(* which gives the Levi-Civita tensor *)
```

The full result contracted with the massive Z polarization sum:

$$|\mathcal{M}|^2 = \frac{g^2}{cos^2\theta_W}\left[(g_V^2 + g_A^2)(M_Z^2 + 2m_f^2) - 6 g_V g_A \cdot 0 + \ldots\right]$$

The VA interference term vanishes after angular integration in the total width but contributes to the forward-backward asymmetry.

---

## Chiral Vector Vertex: V-F-Fbar with $g_L P_L + g_R P_R$

The most general vector coupling to fermions has independent left- and right-handed couplings:

**Lagrangian:**

$$\mathcal{L}_{\text{chiral}} = \bar\psi \gamma^\mu(g_L P_L + g_R P_R) \psi\, V_\mu$$

**Vertex factor:** $i\gamma^\mu(g_L P_L + g_R P_R)$

**FeynCalc amplitude:**

```mathematica
(* Chiral vector vertex: V(mu) -> F Fbar with independent gL, gR *)
(* GA[7] = P_L = (1 - GA[5])/2, GA[6] = P_R = (1 + GA[5])/2 *)
amp = PolarizationVector[p, mu] *
      SpinorUBar[p1, m1] . (I GAD[mu] . (gL GA[7] + gR GA[6])) . SpinorV[p2, m2];
```

**Important FeynCalc convention:**
- `GA[7]` = $P_L$ = $(1-\gamma^5)/2$ (left-handed projector)
- `GA[6]` = $P_R$ = $(1+\gamma^5)/2$ (right-handed projector)

Always use the native FeynCalc projectors `GA[6]` and `GA[7]` instead of writing out `(1 ± GA[5])/2`. The native projectors are simplified more efficiently by FeynCalc internally.

For complex couplings ($g_L, g_R \in \mathbb{C}$), apply coupling conjugation as a separate replacement rule after `ComplexConjugate` handles spinor reversal:

```mathematica
(* Step 1: ComplexConjugate handles spinor chain reversal *)
ampCC = ComplexConjugate[amp];
(* Step 2: Manually conjugate coupling symbols *)
ampCC = ampCC /. {gL -> Conjugate[gL], gR -> Conjugate[gR]};
ampSq = amp ampCC;
```

This ensures $|\mathcal{M}|^2$ correctly contains $|g_L|^2$, $|g_R|^2$, and the $g_L g_R^*$ interference terms.

**Relation to V-A form:** The V-A parameterization $g_V - g_A\gamma^5$ maps to chiral couplings as $g_L = g_V + g_A$ and $g_R = g_V - g_A$.

---

## V-A Vertex (Electroweak Charged Current)

**W boson coupling (purely left-handed):**

$$\mathcal{L}_W = \frac{g}{\sqrt{2}}\, \bar\psi_u \gamma^\mu P_L \psi_d\, W_\mu^+$$

**Vertex factor:** $i\frac{g}{\sqrt{2}}\gamma^\mu P_L$

```mathematica
(* W boson vertex: W+(mu) -> u(p1) dbar(p2), purely left-handed *)
(* Use FeynCalc's native GA[7] for the left-handed projector P_L *)
amp = SpinorUBar[p1, mu] . (I gw/Sqrt[2] GAD[mu] . GA[7]) . SpinorV[p2, md];
```

Key point: `GA[7]` = $P_L = (1-\gamma^5)/2$ is the left-handed projector. The W boson couples only to left-handed fermions and right-handed antifermions.

```mathematica
(* FeynCalc chiral projector identities: *)
(* GA[7] = P_L = (1 - GA[5])/2 *)
(* GA[6] = P_R = (1 + GA[5])/2 *)
(* GA[7].GA[7] = GA[7], GA[6].GA[6] = GA[6], GA[7].GA[6] = 0 *)
(* GAD[mu].GA[7] = GA[6].GAD[mu]  -- chirality flip through gamma matrix *)
```

---

## SM Coupling Values

### QED

$$g_{\text{QED}} = e = \sqrt{4\pi\alpha} \approx 0.303$$

The QED vertex for a fermion of charge $Qe$ is $iQe\gamma^\mu$.

### Z Boson Couplings

The vector and axial couplings for fermion $f$ with weak isospin $T_3^f$ and charge $Q_f$:

$$g_V^f = \frac{T_3^f}{2} - Q_f \sin^2\theta_W, \qquad g_A^f = \frac{T_3^f}{2}$$

with overall coupling $g/\cos\theta_W$.

| Fermion | $T_3$ | $Q$ | $g_V^f$ | $g_A^f$ |
|---------|--------|-----|----------|----------|
| $\nu_e, \nu_\mu, \nu_\tau$ | $+1/2$ | $0$ | $+1/4$ | $+1/4$ |
| $e^-, \mu^-, \tau^-$ | $-1/2$ | $-1$ | $-1/4 + \sin^2\theta_W$ | $-1/4$ |
| $u, c, t$ | $+1/2$ | $+2/3$ | $+1/4 - 2\sin^2\theta_W/3$ | $+1/4$ |
| $d, s, b$ | $-1/2$ | $-1/3$ | $-1/4 + \sin^2\theta_W/3$ | $-1/4$ |

With $\sin^2\theta_W \approx 0.231$:
- Electron: $g_V^e \approx -0.019$, $g_A^e = -0.25$
- Up quark: $g_V^u \approx +0.096$, $g_A^u = +0.25$
- Down quark: $g_V^d \approx -0.173$, $g_A^d = -0.25$

### W Boson

$$g_W = g = \frac{e}{\sin\theta_W} \approx 0.653$$

The vertex includes $1/\sqrt{2}$ and the left-handed projector.

---

## Spin-Summed Traces Reference

For quick reference, the key traces appearing in vector/axial calculations:

```mathematica
(* Vector-Vector: *)
(* Tr[GAD[mu].(GSD[p1]+m1).GAD[nu].(GSD[p2]-m2)] *)
(* = 4(p1^mu p2^nu + p1^nu p2^mu - g^{mu nu}(p1.p2 - m1 m2)) *)

(* Axial-Axial: *)
(* Tr[GAD[mu].GA[5].(GSD[p1]+m1).GAD[nu].GA[5].(GSD[p2]-m2)] *)
(* = 4(p1^mu p2^nu + p1^nu p2^mu - g^{mu nu}(p1.p2 + m1 m2)) *)

(* Vector-Axial interference: *)
(* Tr[GAD[mu].(GSD[p1]+m1).GAD[nu].GA[5].(GSD[p2]-m2)] *)
(* = -4i eps^{mu p1 nu p2}  (only if both fermions are massive) *)
(* This vanishes when contracted with symmetric polarization sum *)
(* but contributes to angular distributions *)
```

---

## Complete FeynCalc Workflow: Z -> f fbar

```mathematica
(* Full calculation: Z(mZ) -> f(mf) fbar(mf) *)
<<FeynCalc`;

(* 1. Write amplitude with V-A vertex *)
amp = SpinorUBar[p1, mf] . (I gz GAD[mu].(gVf - gAf GA[5])) . SpinorV[p2, mf];

(* 2. Square and spin-sum fermions *)
ampSq = amp ComplexConjugate[amp];
ampSqSummed = FermionSpinSum[ampSq] // DiracSimplify;

(* 3. Contract with massive vector polarization sum *)
(* Sum over Z polarizations: -g^{mu nu} + q^mu q^nu / mZ^2 *)
polSum = -MTD[mu, nu] + FVD[q, mu] FVD[q, nu]/mZ^2;
(* Manual contraction or use FeynCalc's Contract *)
ampSqFull = Contract[ampSqSummed * polSum];

(* 4. Apply kinematics *)
kinRules = {
  ScalarProduct[p1, p1] -> mf^2,
  ScalarProduct[p2, p2] -> mf^2,
  ScalarProduct[p1, p2] -> (mZ^2 - 2 mf^2)/2,
  ScalarProduct[q, p1] -> mZ^2/2,
  ScalarProduct[q, p2] -> mZ^2/2,
  ScalarProduct[q, q] -> mZ^2
};
result = ampSqFull /. kinRules // Simplify;

(* Expected: gz^2 [(gVf^2 + gAf^2)(mZ^2 + 2 mf^2) - 12 gAf^2 mf^2] *)
(* = gz^2 [gVf^2 (mZ^2 + 2 mf^2) + gAf^2 (mZ^2 - 4 mf^2)] *)
```

---

## Pitfalls

1. **Use `GAD[mu]` not `GA[mu]` for the Lorentz-contracted gamma matrix.** `GAD[mu]` is D-dimensional and consistent with dimensional regularization. `GA[mu]` is strictly 4-dimensional and will cause inconsistencies in loop calculations.

2. **$\gamma^5$ is always 4-dimensional.** Use `GA[5]`, never `GAD[5]`. In dimensional regularization, $\gamma^5$ does not have a clean D-dimensional extension. FeynCalc uses the Breitenlohner-Maison-'t Hooft-Veltman scheme by default.

3. **The relative sign between $g_V$ and $g_A$ matters.** The convention $g_V - g_A\gamma^5$ vs $g_V + g_A\gamma^5$ changes the sign of the interference term. Check your convention against the SM Lagrangian.

4. **Massive vector polarization sum.** For massive vectors, $\sum_\lambda \epsilon^\mu_\lambda \epsilon^{*\nu}_\lambda = -g^{\mu\nu} + q^\mu q^\nu / M^2$. The $q^\mu q^\nu/M^2$ term gives contributions proportional to fermion masses when contracted with $\gamma^\mu$ via the equation of motion $\bar{u}\not{q}v = \bar{u}(\not{p}_1+\not{p}_2)v = (m_1-m_2)\bar{u}v$ (for the vector part).

5. **Massless vector polarization sum.** For photons, use $\sum_\lambda \epsilon^\mu_\lambda \epsilon^{*\nu}_\lambda = -g^{\mu\nu}$ in Feynman gauge. The unphysical longitudinal/timelike modes cancel by the Ward identity when coupled to conserved currents.

6. **Forward-backward asymmetry.** The V-A interference trace produces a term proportional to $\epsilon^{\mu\nu\rho\sigma}p_{1\rho}p_{2\sigma}$, which is odd under $p_1 \leftrightarrow p_2$ (i.e., $\cos\theta \to -\cos\theta$). This integrates to zero in the total width but produces $A_{FB} \propto g_V g_A$.

---

## Links

- `procedures.decay_width_1to2` -- How to go from |M|^2 to a decay width
- `procedures.cross_section_2to2` -- Cross section calculation for scattering processes
- `spin_sums.fermion_spin_sum` -- Fermion spin sum rules
- `spin_sums.vector_polarization_sum` -- Polarization sum for massive and massless vectors
- `feynman_rules.vertices_scalar` -- Scalar and pseudoscalar vertices for comparison
- `feyncalc_reference.spinors_and_traces` -- Spinor conventions and trace evaluation
- `worked_examples.z_to_ee` -- Complete worked example of Z -> e+e-
- `worked_examples.ee_to_mumu` -- Complete worked example of e+e- -> mu+mu-
