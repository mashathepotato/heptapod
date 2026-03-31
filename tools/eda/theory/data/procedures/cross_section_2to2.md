# 2->2 Cross Section Procedure

**Node ID:** `procedures.cross_section_2to2`
**Category:** procedure

## Overview

This document gives the complete step-by-step recipe for computing the differential and total cross section for a $2 \to 2$ scattering process $1 + 2 \to 3 + 4$. The result is expressed in terms of Mandelstam variables $s$, $t$, $u$. Each step includes the corresponding FeynCalc Mathematica code.

---

## Master Formulas

### Differential Cross Section (CM Frame)

$$
\frac{d\sigma}{d\Omega}\bigg|_{\text{CM}} = \frac{1}{64\pi^2 s} \frac{|\mathbf{p}_f|}{|\mathbf{p}_i|} \cdot \frac{1}{n_1 n_2} \sum_{\text{spins}} |\mathcal{M}|^2
$$

where:
- $s = (p_1 + p_2)^2$ is the CM energy squared
- $|\mathbf{p}_i|$ and $|\mathbf{p}_f|$ are the initial and final CM 3-momenta
- $n_1$, $n_2$ are the spin/polarization degeneracies of the initial-state particles
- $\sum_{\text{spins}} |\mathcal{M}|^2$ is summed (not averaged) over all spins

For **equal initial and final masses** ($m_1 = m_2 = m_3 = m_4 \equiv m$), this simplifies to:

$$
\frac{d\sigma}{d\Omega}\bigg|_{\text{CM}} = \frac{1}{64\pi^2 s} \cdot \frac{1}{n_1 n_2} \sum_{\text{spins}} |\mathcal{M}|^2
$$

### Differential Cross Section in Mandelstam $t$

$$
\frac{d\sigma}{dt} = \frac{1}{16\pi \lambda(s, m_1^2, m_2^2)} \cdot \frac{1}{n_1 n_2} \sum_{\text{spins}} |\mathcal{M}|^2
$$

where $\lambda(a,b,c) = a^2 + b^2 + c^2 - 2ab - 2ac - 2bc$ is the Kallen function.

### Total Cross Section

$$
\sigma = \int \frac{d\sigma}{d\Omega} \, d\Omega = \int_{t_-}^{t_+} \frac{d\sigma}{dt} \, dt
$$

where $t_\pm$ are the kinematic limits of $t$ determined by the scattering angle $\cos\theta = \pm 1$.

---

## Mandelstam Variables

### Definitions

$$
s = (p_1 + p_2)^2 = (p_3 + p_4)^2
$$

$$
t = (p_1 - p_3)^2 = (p_2 - p_4)^2
$$

$$
u = (p_1 - p_4)^2 = (p_2 - p_3)^2
$$

### Constraint

$$
s + t + u = m_1^2 + m_2^2 + m_3^2 + m_4^2
$$

This means only two of the three variables are independent.

### CM Frame Relations (Equal Masses)

For the case $m_1 = m_2 = m_3 = m_4 \equiv m$:

$$
t = -\frac{1}{2}(s - 4m^2)(1 - \cos\theta)
$$

$$
u = -\frac{1}{2}(s - 4m^2)(1 + \cos\theta)
$$

where $\theta$ is the CM scattering angle.

### CM Frame Relations (General Masses)

$$
t = m_1^2 + m_3^2 - \frac{1}{2s}\big[(s + m_1^2 - m_2^2)(s + m_3^2 - m_4^2) - \lambda^{1/2}(s,m_1^2,m_2^2)\,\lambda^{1/2}(s,m_3^2,m_4^2)\cos\theta\big]
$$

### Kinematic Limits of $t$

$$
t_{\pm} = m_1^2 + m_3^2 - \frac{1}{2s}\big[(s + m_1^2 - m_2^2)(s + m_3^2 - m_4^2) \mp \lambda^{1/2}(s,m_1^2,m_2^2)\,\lambda^{1/2}(s,m_3^2,m_4^2)\big]
$$

---

## Step 1: Write the Amplitude from Feynman Rules

Identify all contributing Feynman diagrams (s-channel, t-channel, u-channel, contact terms) and write the total amplitude as their sum:

$$
\mathcal{M} = \mathcal{M}_s + \mathcal{M}_t + \mathcal{M}_u + \cdots
$$

Each diagram contributes a vertex factor, propagator(s), and external-line factors.

### Example: $e^+e^- \to \mu^+\mu^-$ via s-channel photon

$$
i\mathcal{M} = \bar{v}(p_2)(-ie\gamma^\mu)u(p_1) \cdot \frac{-ig_{\mu\nu}}{s} \cdot \bar{u}(p_3)(-ie\gamma^\nu)v(p_4)
$$

### FeynCalc Code

```mathematica
(* === Step 1: Define the amplitude === *)

(* Example: e+e- -> mu+mu- via s-channel photon *)
(* Fermion flow: vbar(p2) . vertex . u(p1) for the electron line *)
(*               ubar(p3) . vertex . v(p4) for the muon line     *)

amp = SpinorVBar[p2, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
      (-I MTD[mu, nu] / SP[p1 + p2, p1 + p2]) *
      SpinorUBar[p3, mmu] . (-I e GAD[nu]) . SpinorV[p4, mmu];

(* For multiple diagrams, define each separately and sum *)
(* ampTotal = ampS + ampT + ampU; *)
```

**Pitfall:** Pay careful attention to fermion flow direction. For an incoming particle, use `SpinorU`; for an incoming antiparticle, use `SpinorVBar`. For an outgoing particle, use `SpinorUBar`; for an outgoing antiparticle, use `SpinorV`.

**See:** [feynman_rules.propagators], [feynman_rules.vertices_vector]

---

## Step 2: Square the Amplitude and Sum over Spins

### FeynCalc Code

```mathematica
(* === Step 2: Square and spin-sum === *)

ampCC = ComplexConjugate[amp];
ampSq = amp * ampCC;

(* Apply spin sums for ALL external fermions *)
ampSqSummed = FermionSpinSum[ampSq];

(* If external vector bosons are present, apply polarization sums *)
(* ampSqSummed = DoPolarizationSums[ampSqSummed, k, 0]; *)
```

**See:** [spin_sums.fermion_spin_sum]

---

## Step 3: Evaluate Traces

After spin sums, the expression is a product of Dirac traces. For a $2 \to 2$ fermion process, there are typically two independent fermion lines, yielding two traces.

### FeynCalc Code

```mathematica
(* === Step 3: Evaluate Dirac traces === *)

ampSqTraced = DiracSimplify[ampSqSummed] // Contract;

(* The result is now a Lorentz scalar in terms of *)
(* Pair[Momentum[pi], Momentum[pj]] dot products   *)
```

**Pitfall:** For processes with two separate fermion lines (like $e^+e^- \to \mu^+\mu^-$), `DiracSimplify` will produce a product of two traces. If they share Lorentz indices (from a propagator), use `Contract` afterward to contract them.

**See:** [feyncalc_reference.spinors_and_traces]

---

## Step 4: Express in Mandelstam Variables

Replace all momentum dot products with Mandelstam variables. This makes the result manifestly Lorentz-invariant and suitable for integration.

### Momentum Dot Products in Terms of Mandelstam Variables

From the definitions $s = (p_1+p_2)^2$, $t = (p_1-p_3)^2$, $u = (p_1-p_4)^2$:

$$
p_1 \cdot p_2 = \frac{s - m_1^2 - m_2^2}{2}
$$

$$
p_1 \cdot p_3 = \frac{m_1^2 + m_3^2 - t}{2}
$$

$$
p_1 \cdot p_4 = \frac{m_1^2 + m_4^2 - u}{2}
$$

$$
p_2 \cdot p_3 = \frac{m_2^2 + m_3^2 - u}{2}
$$

$$
p_2 \cdot p_4 = \frac{m_2^2 + m_4^2 - t}{2}
$$

$$
p_3 \cdot p_4 = \frac{s - m_3^2 - m_4^2}{2}
$$

### FeynCalc Code

```mathematica
(* === Step 4: Replace dot products with Mandelstam variables === *)

(* Define Mandelstam variables *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, m1, m2, m3, m4];

(* FeynCalc's SetMandelstam automatically creates replacement rules. *)
(* Apply them: *)
ampSqMandel = TrickMandelstam[ampSqTraced, {s, t, u, m1^2 + m2^2 + m3^2 + m4^2}] // Simplify;

(* Alternative: manual replacement if SetMandelstam is not used *)
mandelRules = {
  Pair[Momentum[p1], Momentum[p2]] -> (s - m1^2 - m2^2)/2,
  Pair[Momentum[p1], Momentum[p3]] -> (m1^2 + m3^2 - t)/2,
  Pair[Momentum[p1], Momentum[p4]] -> (m1^2 + m4^2 - u)/2,
  Pair[Momentum[p2], Momentum[p3]] -> (m2^2 + m3^2 - u)/2,
  Pair[Momentum[p2], Momentum[p4]] -> (m2^2 + m4^2 - t)/2,
  Pair[Momentum[p3], Momentum[p4]] -> (s - m3^2 - m4^2)/2,
  Pair[Momentum[p1], Momentum[p1]] -> m1^2,
  Pair[Momentum[p2], Momentum[p2]] -> m2^2,
  Pair[Momentum[p3], Momentum[p3]] -> m3^2,
  Pair[Momentum[p4], Momentum[p4]] -> m4^2
};
ampSqMandel = ampSqTraced /. mandelRules // Simplify;
```

**Pitfall:** The sign convention for outgoing momenta in `SetMandelstam` is crucial. Outgoing momenta get a minus sign: `SetMandelstam[s, t, u, p1, p2, -p3, -p4, ...]`. Getting this wrong produces incorrect Mandelstam substitutions.

**See:** [phase_space.mandelstam]

---

## Step 5: Crossing Relations (Optional)

If you have computed the amplitude for one channel (e.g., s-channel), you can obtain the amplitude for a crossed channel by relabeling momenta and Mandelstam variables.

### Crossing Substitutions

| Original ($s$-channel) | $t$-channel | $u$-channel |
|---|---|---|
| $s \to t$ | $s \to u$ | |
| $t \to s$ | $u \to s$ | |
| $u \to u$ | $t \to t$ | |

Specifically, for $1 + 2 \to 3 + 4$ in the $s$-channel:
- **$t$-channel** ($1 + \bar{3} \to \bar{2} + 4$): interchange $s \leftrightarrow t$
- **$u$-channel** ($1 + \bar{4} \to 3 + \bar{2}$): interchange $s \leftrightarrow u$

### FeynCalc Code

```mathematica
(* === Step 5: Crossing relations === *)

(* t-channel from s-channel by s <-> t *)
ampSqTchannel = ampSqMandel /. {s -> tTemp, t -> s} /. tTemp -> t;

(* u-channel from s-channel by s <-> u *)
ampSqUchannel = ampSqMandel /. {s -> uTemp, u -> s} /. uTemp -> u;
```

**Pitfall:** When crossing, external particle types change (particle $\leftrightarrow$ antiparticle). Make sure the crossed amplitude corresponds to a physically allowed process. Crossing also introduces additional signs for fermions.

---

## Step 6: Compute the Differential Cross Section

### FeynCalc Code

```mathematica
(* === Step 6: Differential cross section === *)

(* Kallen function *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;

(* Initial and final CM momenta *)
pInit = Sqrt[Kallen[s, m1^2, m2^2]] / (2 Sqrt[s]);
pFinal = Sqrt[Kallen[s, m3^2, m4^2]] / (2 Sqrt[s]);

(* Number of initial spin states *)
n1 = 2; (* fermion *)
n2 = 2; (* fermion *)

(* Differential cross section dSigma/dOmega *)
dsigmaDOmega = (1/(64 Pi^2 s)) * (pFinal/pInit) * (1/(n1 n2)) * ampSqMandel;

(* Differential cross section dSigma/dt *)
(* Using dOmega = (2 Pi / (pInit * pFinal)) * dt in the CM frame *)
dsigmaDt = 1/(16 Pi Kallen[s, m1^2, m2^2]) * (1/(n1 n2)) * ampSqMandel;
```

---

## Step 7: Compute the Total Cross Section

Integrate over the full solid angle (or equivalently over $t$).

### FeynCalc Code

```mathematica
(* === Step 7: Total cross section === *)

(* Kinematic limits of t *)
tPlus = m1^2 + m3^2 - (1/(2 s)) * (
  (s + m1^2 - m2^2)(s + m3^2 - m4^2) -
  Sqrt[Kallen[s, m1^2, m2^2]] Sqrt[Kallen[s, m3^2, m4^2]]
);

tMinus = m1^2 + m3^2 - (1/(2 s)) * (
  (s + m1^2 - m2^2)(s + m3^2 - m4^2) +
  Sqrt[Kallen[s, m1^2, m2^2]] Sqrt[Kallen[s, m3^2, m4^2]]
);

(* Integrate *)
sigmaTot = Integrate[dsigmaDt, {t, tMinus, tPlus}] // Simplify;

(* For equal masses (massless limit m -> 0): *)
(* sigmaTot = Integrate[dsigmaDt /. {m1->0, m2->0, m3->0, m4->0}, *)
(*                       {t, -s, 0}] // Simplify;                  *)

Print["Total cross section: sigma = ", sigmaTot];
```

**Pitfall:** For identical particles in the final state ($3 = 4$), include an additional factor of $1/2$ in the total cross section to avoid double-counting. See [procedures.identical_particles].

---

## Complete FeynCalc Workflow (Copy-Paste Template)

Below is the full workflow for $e^+e^- \to \mu^+\mu^-$ via s-channel photon exchange, in the massless limit.

```mathematica
(* ================================================ *)
(* Complete 2->2 Cross Section: e+e- -> mu+mu-      *)
(* s-channel photon, massless limit                  *)
(* ================================================ *)

<< FeynCalc`

(* Step 1: Amplitude *)
amp = SpinorVBar[p2, 0] . (-I e GAD[mu]) . SpinorU[p1, 0] *
      (-I MTD[mu, nu] / SP[p1 + p2, p1 + p2]) *
      SpinorUBar[p3, 0] . (-I e GAD[nu]) . SpinorV[p4, 0];

(* Step 2: Square and spin-sum *)
ampCC = ComplexConjugate[amp];
ampSq = amp * ampCC;
ampSqSummed = FermionSpinSum[ampSq];

(* Step 3: Traces *)
ampSqTraced = DiracSimplify[ampSqSummed] // Contract;

(* Step 4: Mandelstam variables (massless) *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, 0, 0, 0, 0];
ampSqMandel = ampSqTraced // TrickMandelstam[#, {s, t, u, 0}] & // Simplify;

(* Expected result: 8 e^4 (t^2 + u^2) / s^2 *)
(* Using u = -s - t: 8 e^4 (t^2 + (s+t)^2) / s^2 *)

Print["Spin-summed |M|^2 = ", ampSqMandel];

(* Step 6: Differential cross section (massless, equal masses) *)
n1 = 2; n2 = 2;
dsigmaDOmega = (1 / (64 Pi^2 s)) * (1/(n1 n2)) * ampSqMandel;

(* Replace t = -(s/2)(1 - cos(theta)) for equal massless particles *)
dsigmaDOmegaTheta = dsigmaDOmega /. {t -> -(s/2)(1 - ct), u -> -(s/2)(1 + ct)};
Print["dsigma/dOmega = ", dsigmaDOmegaTheta // Simplify];
(* Expected: (alpha^2 / (4s)) * (1 + cos^2(theta)) where alpha = e^2/(4 Pi) *)

(* Step 7: Total cross section *)
(* Integrate over solid angle: 2 Pi integral over cos(theta) from -1 to 1 *)
sigmaTot = 2 Pi * Integrate[dsigmaDOmegaTheta * 2 Pi Sin[theta],
                              {theta, 0, Pi}] // Simplify;
(* Or more simply, integrate dsigma/dt over t from -s to 0 *)
dsigmaDt = 1/(16 Pi s^2) * (1/(n1 n2)) * ampSqMandel;
sigmaTot = Integrate[dsigmaDt /. u -> -s - t, {t, -s, 0}] // Simplify;
Print["sigma_total = ", sigmaTot];
(* Expected: sigma = 4 Pi alpha^2 / (3 s) *)
```

---

## Common Pitfalls

1. **Sign convention for outgoing momenta.** In `SetMandelstam`, outgoing momenta require a minus sign. The convention is all-incoming: $p_1 + p_2 + (-p_3) + (-p_4) = 0$.

2. **Propagator denominator.** The photon propagator denominator is $q^2 = (p_1+p_2)^2 = s$ in the s-channel. Do not confuse $q^2$ with $s - M_V^2$ (which applies for massive propagators: $1/(q^2 - M_V^2)$).

3. **Massless limit subtleties.** In the massless limit ($m \to 0$), the Kallen function simplifies: $\lambda(s, 0, 0) = s^2$, so $|\mathbf{p}_i| = |\mathbf{p}_f| = \sqrt{s}/2$ and the prefactor ratio $|\mathbf{p}_f|/|\mathbf{p}_i| = 1$.

4. **Double-counting with `TrickMandelstam`.** The function `TrickMandelstam` uses the constraint $s + t + u = \sum m^2$ to simplify. It may eliminate one variable. Verify which variable was eliminated before performing further substitutions.

5. **Flux factor.** The factor $1/(64\pi^2 s)$ in the CM frame already contains the correct flux factor $1/(4|\mathbf{p}_i|\sqrt{s})$ combined with the phase-space factor. Do not add an additional flux factor.

6. **Color factors for QCD processes.** For quark scattering, color factors must be computed separately (trace over color generators). FeynCalc handles Dirac algebra but not SU(3) color algebra by default. Use `SUNSimplify` for color traces if using FeynCalc's color objects, or compute color factors analytically.

---

## Related Documents

- [feynman_rules.propagators] -- Propagator Feynman rules for all particle types
- [feynman_rules.vertices_vector] -- QED and electroweak vector vertices
- [spin_sums.fermion_spin_sum] -- Fermion spin completeness relations
- [phase_space.mandelstam] -- Mandelstam variable definitions and identities
- [feyncalc_reference.spinors_and_traces] -- FeynCalc spinor and trace functions
- [procedures.interference] -- Handling interference between diagrams
- [procedures.identical_particles] -- Symmetry factors for identical final-state particles
