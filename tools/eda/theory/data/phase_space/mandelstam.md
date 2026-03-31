# Mandelstam Variables

**Node ID:** `phase_space.mandelstam`
**Category:** phase_space

## Overview

This document defines the Mandelstam variables $s$, $t$, $u$ for $2 \to 2$ scattering processes and gives all relevant kinematic relations, differential and total cross section formulas, and the corresponding FeynCalc Mathematica code. The Mandelstam variables provide a Lorentz-invariant parametrization of the kinematics, making them the natural language for expressing scattering amplitudes and cross sections.

---

## Definitions

For the process $p_1 + p_2 \to p_3 + p_4$:

$$
s = (p_1 + p_2)^2 = (p_3 + p_4)^2
$$

$$
t = (p_1 - p_3)^2 = (p_2 - p_4)^2
$$

$$
u = (p_1 - p_4)^2 = (p_2 - p_3)^2
$$

**Physical interpretation:**
- $s$ is the squared center-of-mass energy
- $t$ is the squared 4-momentum transfer between particles 1 and 3
- $u$ is the squared 4-momentum transfer between particles 1 and 4

---

## Constraint

The three Mandelstam variables are not independent. They satisfy:

$$
s + t + u = m_1^2 + m_2^2 + m_3^2 + m_4^2
$$

This means only two of the three variables are independent. Typically $s$ and $t$ are chosen as independent, with $u$ determined from the constraint.

---

## Momentum Dot Products in Terms of Mandelstam Variables

From the definitions and on-shell conditions $p_i^2 = m_i^2$:

$$
p_1 \cdot p_2 = \frac{s - m_1^2 - m_2^2}{2}
$$

$$
p_3 \cdot p_4 = \frac{s - m_3^2 - m_4^2}{2}
$$

$$
p_1 \cdot p_3 = \frac{m_1^2 + m_3^2 - t}{2}
$$

$$
p_2 \cdot p_4 = \frac{m_2^2 + m_4^2 - t}{2}
$$

$$
p_1 \cdot p_4 = \frac{m_1^2 + m_4^2 - u}{2}
$$

$$
p_2 \cdot p_3 = \frac{m_2^2 + m_3^2 - u}{2}
$$

---

## Center-of-Mass Frame

### General masses

In the CM frame, $\mathbf{p}_1 + \mathbf{p}_2 = \mathbf{0}$ and $\mathbf{p}_3 + \mathbf{p}_4 = \mathbf{0}$. The initial and final 3-momenta are:

$$
|\mathbf{p}_i| = \frac{\lambda^{1/2}(s, m_1^2, m_2^2)}{2\sqrt{s}}, \qquad |\mathbf{p}_f| = \frac{\lambda^{1/2}(s, m_3^2, m_4^2)}{2\sqrt{s}}
$$

where $\lambda(a,b,c) = a^2 + b^2 + c^2 - 2ab - 2ac - 2bc$ is the Kallen function.

The relation between $t$ and the CM scattering angle $\theta$ is:

$$
t = m_1^2 + m_3^2 - \frac{1}{2s}\left[(s + m_1^2 - m_2^2)(s + m_3^2 - m_4^2) - \lambda^{1/2}(s,m_1^2,m_2^2)\,\lambda^{1/2}(s,m_3^2,m_4^2)\cos\theta\right]
$$

### Equal masses ($m_1 = m_2 = m_3 = m_4 = m$)

The Mandelstam variables simplify to:

$$
s = 4(|\mathbf{p}|^2 + m^2) = E_{\text{cm}}^2
$$

$$
t = -2|\mathbf{p}|^2(1 - \cos\theta) = -\frac{s - 4m^2}{2}(1 - \cos\theta)
$$

$$
u = -2|\mathbf{p}|^2(1 + \cos\theta) = -\frac{s - 4m^2}{2}(1 + \cos\theta)
$$

The kinematic limits of $t$ are:

$$
t_{\min} = -(s - 4m^2), \qquad t_{\max} = 0
$$

corresponding to $\cos\theta = -1$ and $\cos\theta = +1$, respectively.

---

## Differential Cross Section

### In terms of solid angle

$$
\frac{d\sigma}{d\Omega} = \frac{1}{64\pi^2 s} \frac{|\mathbf{p}_f|}{|\mathbf{p}_i|} \overline{|\mathcal{M}|^2}
$$

For equal-mass scattering ($|\mathbf{p}_f| = |\mathbf{p}_i|$):

$$
\frac{d\sigma}{d\Omega} = \frac{\overline{|\mathcal{M}|^2}}{64\pi^2 s}
$$

### In terms of $t$

$$
\frac{d\sigma}{dt} = \frac{1}{16\pi\lambda(s, m_1^2, m_2^2)} \overline{|\mathcal{M}|^2}
$$

The relation between the two forms uses $d\Omega = 2\pi\, d(\cos\theta)$ and $dt = |\mathbf{p}_i||\mathbf{p}_f|\, d(\cos\theta) \cdot 2/\sqrt{s}$... more precisely:

$$
\frac{d\sigma}{dt} = \frac{\pi}{|\mathbf{p}_i|^2} \frac{d\sigma}{d\Omega}
$$

---

## Total Cross Section

$$
\sigma = \int \frac{d\sigma}{d\Omega}\, d\Omega = \int_0^\pi \frac{d\sigma}{d\Omega}\, 2\pi \sin\theta\, d\theta
$$

In terms of $t$:

$$
\sigma = \frac{1}{16\pi s} \frac{1}{|\mathbf{p}_i|^2} \int_{t_{\min}}^{t_{\max}} \overline{|\mathcal{M}|^2}\, dt
$$

For equal masses: $t_{\min} = -(s - 4m^2)$, $t_{\max} = 0$.

For the massless limit: $t_{\min} = -s$, $t_{\max} = 0$.

---

## FeynCalc: Expressing Results in Mandelstam Variables

### Using SetMandelstam

```mathematica
<< FeynCalc`

(* Define Mandelstam variables *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, m1, m2, m3, m4];

(* This sets up: *)
(* SP[p1,p2] = (s - m1^2 - m2^2)/2 *)
(* SP[p1,p3] = (m1^2 + m3^2 - t)/2 *)
(* SP[p1,p4] = (m1^2 + m4^2 - u)/2 *)
(* SP[p2,p3] = (m2^2 + m3^2 - u)/2 *)
(* SP[p2,p4] = (m2^2 + m4^2 - t)/2 *)
(* SP[p3,p4] = (s - m3^2 - m4^2)/2 *)

(* After computing |M|^2, simplify using Mandelstam *)
ampSqSimplified = TrickMandelstam[ampSq, {s, t, u, m1^2 + m2^2 + m3^2 + m4^2}];
```

**Pitfall:** The sign convention for outgoing momenta in `SetMandelstam` is crucial. Outgoing momenta require a minus sign: `SetMandelstam[s, t, u, p1, p2, -p3, -p4, ...]`. The convention is all-incoming: $p_1 + p_2 + (-p_3) + (-p_4) = 0$.

### Manual Replacement Rules

If `SetMandelstam` is not used, apply replacements directly:

```mathematica
(* Manual Mandelstam replacement rules *)
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

(* Optionally eliminate u using the constraint *)
ampSqMandel = ampSqMandel /. u -> m1^2 + m2^2 + m3^2 + m4^2 - s - t // Simplify;
```

---

## Mathematica Code for Numerical Cross Section

```mathematica
(* Kallen function *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;

(* Total cross section for equal-mass 2->2 scattering *)
(* ampSqFn[s, t] is the spin-averaged |M|^2 as a function of s and t *)
TotalCrossSection[sqrtS_, m_, ampSqFn_] := Module[{s, pMag, tMin, tMax},
  s = sqrtS^2;
  pMag = Sqrt[s/4 - m^2];
  tMin = -(s - 4 m^2);
  tMax = 0;
  1/(16 Pi s pMag^2) * NIntegrate[ampSqFn[s, t], {t, tMin, tMax}]
];

(* Total cross section for general-mass 2->2 scattering *)
TotalCrossSectionGeneral[sqrtS_, m1_, m2_, m3_, m4_, ampSqFn_] :=
  Module[{s, lambdaI, tPlus, tMinus},
  s = sqrtS^2;
  lambdaI = Kallen[s, m1^2, m2^2];
  tPlus = m1^2 + m3^2 - (1/(2 s)) * (
    (s + m1^2 - m2^2)(s + m3^2 - m4^2) -
    Sqrt[Kallen[s, m1^2, m2^2]] Sqrt[Kallen[s, m3^2, m4^2]]
  );
  tMinus = m1^2 + m3^2 - (1/(2 s)) * (
    (s + m1^2 - m2^2)(s + m3^2 - m4^2) +
    Sqrt[Kallen[s, m1^2, m2^2]] Sqrt[Kallen[s, m3^2, m4^2]]
  );
  1/(16 Pi lambdaI) * NIntegrate[ampSqFn[s, t], {t, tMinus, tPlus}]
];

(* Differential cross section as a function of cos(theta) for equal masses *)
DSigmaDCosTheta[sqrtS_, m_, ampSqFn_] := Module[{s, tOfCosTheta},
  s = sqrtS^2;
  tOfCosTheta[ct_] := -(s - 4 m^2)/2 * (1 - ct);
  Function[ct,
    ampSqFn[s, tOfCosTheta[ct]] / (32 Pi s)
  ]
];
```

---

## Crossing Symmetry

The same Feynman diagram amplitude $\mathcal{M}(s,t,u)$ describes physically distinct processes in different kinematic regions:

- **s-channel** ($s > 0$, $t < 0$, $u < 0$): particle + antiparticle annihilation, e.g., $e^+e^- \to \mu^+\mu^-$
- **t-channel** ($t > 0$, $s < 0$, $u < 0$): particle-particle scattering via exchange, e.g., $e^-\mu^- \to e^-\mu^-$
- **u-channel** ($u > 0$, $s < 0$, $t < 0$): related by exchanging final-state particles

### Crossing Relations

To obtain a $t$-channel amplitude from an $s$-channel one: interchange $s \leftrightarrow t$.
To obtain a $u$-channel amplitude from an $s$-channel one: interchange $s \leftrightarrow u$.

### FeynCalc Code

```mathematica
(* t-channel from s-channel by s <-> t *)
ampSqTchannel = ampSqMandel /. {s -> tTemp, t -> s} /. tTemp -> t;

(* u-channel from s-channel by s <-> u *)
ampSqUchannel = ampSqMandel /. {s -> uTemp, u -> s} /. uTemp -> u;
```

**Pitfall:** When crossing, external particle types change (particle $\leftrightarrow$ antiparticle). Verify that the crossed amplitude corresponds to a physically allowed process. Crossing also introduces additional signs for fermion amplitudes.

---

## Physical Regions

The physical scattering region for $2 \to 2$ with equal masses is:

$$
s \geq 4m^2, \qquad -(s - 4m^2) \leq t \leq 0, \qquad u = 4m^2 - s - t
$$

The physical region is bounded by the curves:

$$
t = 0, \qquad u = 0, \qquad s = 4m^2
$$

forming a triangular region in the $(s, t)$ plane (or equivalently the Mandelstam triangle in $(s, t, u)$ space).

---

## Pitfalls

1. **Sign convention in `SetMandelstam`.** Outgoing momenta get a minus sign. The convention is all-incoming: $p_1 + p_2 - p_3 - p_4 = 0$. Getting this wrong produces incorrect Mandelstam substitutions.

2. **`TrickMandelstam` variable elimination.** `TrickMandelstam[expr, {s, t, u, sumMasses}]` uses the constraint $s + t + u = \sum m^2$ to simplify. It may eliminate one variable. Verify which variable was eliminated before performing further substitutions.

3. **Forward singularities.** Many amplitudes diverge as $t \to 0$ (Coulomb singularity) or have propagator poles at $t = M_{\text{exchanged}}^2$. These require regularization or careful treatment when integrating for the total cross section.

4. **Flux factor.** The factor $1/(64\pi^2 s)$ in the CM differential cross section formula already includes the correct flux factor. Do not add an additional flux factor.

5. **Identical final-state particles.** If particles 3 and 4 are identical, the total cross section includes a symmetry factor of $1/2$, and the amplitude may have contributions from both $t$-channel and $u$-channel exchange that must be added coherently before squaring.

6. **Massless limit.** In the massless limit, the Kallen function simplifies: $\lambda(s, 0, 0) = s^2$, so $|\mathbf{p}_i| = |\mathbf{p}_f| = \sqrt{s}/2$. The constraint becomes $s + t + u = 0$.

---

## Related Documents

- [procedures.cross_section_2to2] -- Complete step-by-step procedure for computing 2->2 cross sections
- [phase_space.two_body] -- Two-body decay phase space formulas
- [phase_space.three_body] -- Three-body decay phase space formulas
- [feyncalc_reference.momentum_and_indices] -- FeynCalc momentum and index conventions
