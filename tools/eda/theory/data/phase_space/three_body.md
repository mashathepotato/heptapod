# Three-Body Phase Space

**Node ID:** `phase_space.three_body`
**Category:** phase_space

## Overview

This document gives the formulas for the three-body (1->3) decay phase space. Unlike the two-body case, the three-body phase space is not fully constrained by the masses alone: the kinematics are described by two independent invariant-mass variables, and the decay width requires a two-dimensional integration over the Dalitz plot. Each formula includes the corresponding Mathematica code.

---

## General Formula

The differential decay width for $A(p) \to 1(p_1)\, 2(p_2)\, 3(p_3)$ is:

$$
d\Gamma = \frac{1}{(2\pi)^3} \frac{1}{32 M^3} |\mathcal{M}|^2 \, dm_{12}^2 \, dm_{23}^2
$$

where:
- $M$ is the decaying particle mass
- $m_{ij}^2 = (p_i + p_j)^2$ are invariant masses of particle pairs
- $|\mathcal{M}|^2$ is the spin-averaged squared amplitude (which in general depends on the invariant masses)

The total decay width is obtained by integrating over the kinematically allowed region (the Dalitz plot):

$$
\Gamma = \frac{1}{(2\pi)^3} \frac{1}{32 M^3} \int dm_{12}^2 \int dm_{23}^2 \, |\mathcal{M}|^2
$$

---

## Invariant Mass Relations

The three invariant masses are not independent. They satisfy:

$$
m_{12}^2 + m_{13}^2 + m_{23}^2 = M^2 + m_1^2 + m_2^2 + m_3^2
$$

This constraint eliminates one of the three invariant masses, leaving two independent integration variables.

---

## Dalitz Plot Boundaries

### Range of $m_{12}^2$

$$
m_{12}^2 \in \left[(m_1+m_2)^2,\; (M-m_3)^2\right]
$$

### Range of $m_{23}^2$ for fixed $m_{12}^2$

For a given value of $m_{12}^2$, the limits on $m_{23}^2$ are:

$$
(m_{23}^2)_{\min} = (E_2^* + E_3^*)^2 - \left(\sqrt{E_2^{*2} - m_2^2} + \sqrt{E_3^{*2} - m_3^2}\right)^2
$$

$$
(m_{23}^2)_{\max} = (E_2^* + E_3^*)^2 - \left(\sqrt{E_2^{*2} - m_2^2} - \sqrt{E_3^{*2} - m_3^2}\right)^2
$$

where $E_2^*$ and $E_3^*$ are the energies of particles 2 and 3 evaluated in the rest frame of the (12) system:

$$
E_2^* = \frac{m_{12}^2 - m_1^2 + m_2^2}{2\sqrt{m_{12}^2}}
$$

$$
E_3^* = \frac{M^2 - m_{12}^2 - m_3^2}{2\sqrt{m_{12}^2}}
$$

---

## Mathematica Code

### Dalitz Plot Boundary Functions

```mathematica
(* Energies in the (12) rest frame *)
E2star[m12sq_, m1_, m2_] := (m12sq - m1^2 + m2^2) / (2 Sqrt[m12sq]);
E3star[m12sq_, M_, m3_] := (M^2 - m12sq - m3^2) / (2 Sqrt[m12sq]);

(* Dalitz plot boundaries for m23^2 at fixed m12^2 *)
m23sqMin[m12sq_, M_, m1_, m2_, m3_] := Module[{e2, e3, p2, p3},
  e2 = E2star[m12sq, m1, m2];
  e3 = E3star[m12sq, M, m3];
  p2 = Sqrt[e2^2 - m2^2];
  p3 = Sqrt[e3^2 - m3^2];
  (e2 + e3)^2 - (p2 + p3)^2
];

m23sqMax[m12sq_, M_, m1_, m2_, m3_] := Module[{e2, e3, p2, p3},
  e2 = E2star[m12sq, m1, m2];
  e3 = E3star[m12sq, M, m3];
  p2 = Sqrt[e2^2 - m2^2];
  p3 = Sqrt[e3^2 - m3^2];
  (e2 + e3)^2 - (p2 - p3)^2
];
```

### Three-Body Decay Width (Numerical Integration)

```mathematica
(* Three-body phase space integration *)
(* ampSqFn[m12sq, m23sq] is the spin-averaged |M|^2 as a function of invariant masses *)
GammaThreeBody[M_, m1_, m2_, m3_, ampSqFn_] := Module[{result},
  result = NIntegrate[
    ampSqFn[m12sq, m23sq] / ((2 Pi)^3 32 M^3),
    {m12sq, (m1 + m2)^2, (M - m3)^2},
    {m23sq, m23sqMin[m12sq, M, m1, m2, m3], m23sqMax[m12sq, M, m1, m2, m3]}
  ];
  result
];

(* For constant |M|^2 (e.g., contact interaction), the total width is: *)
GammaThreeBodyConst[M_, m1_, m2_, m3_, ampSqConst_] :=
  GammaThreeBody[M, m1, m2, m3, Function[{m12sq, m23sq}, ampSqConst]];
```

### Expressing Scalar Products in Terms of Invariant Masses

```mathematica
(* Kinematic replacement rules for three-body decays *)
(* Express all scalar products in terms of m12sq, m23sq, and masses *)
threeBodyKinRules[M_, m1_, m2_, m3_] := {
  SP[p1, p2] -> (m12sq - m1^2 - m2^2)/2,
  SP[p2, p3] -> (m23sq - m2^2 - m3^2)/2,
  SP[p1, p3] -> (M^2 + m1^2 + m2^2 + m3^2 - m12sq - m23sq - m1^2 - m3^2)/2,
  (* Simplifies to: *)
  (* SP[p1, p3] -> (M^2 + m2^2 - m12sq - m23sq)/2  *)
  SP[p, p1] -> (M^2 + m1^2 - m23sq)/2 - SP[p1, p2],
  SP[p, p2] -> (M^2 + m2^2 - (M^2 + m1^2 + m2^2 + m3^2 - m12sq - m23sq))/2,
  SP[p, p3] -> (M^2 + m3^2 - m12sq)/2,
  SP[p, p] -> M^2,
  SP[p1, p1] -> m1^2,
  SP[p2, p2] -> m2^2,
  SP[p3, p3] -> m3^2
};

(* Cleaner version using the invariant mass constraint: *)
threeBodyKinRulesClean[M_, m1_, m2_, m3_] := {
  SP[p1, p2] -> (m12sq - m1^2 - m2^2)/2,
  SP[p2, p3] -> (m23sq - m2^2 - m3^2)/2,
  SP[p1, p3] -> (M^2 + m2^2 - m12sq - m23sq)/2,
  SP[p, p1] -> (M^2 + m1^2 - m23sq - 2 SP[p1, p2])/2,
  SP[p, p3] -> (M^2 + m3^2 - m12sq)/2,
  SP[p, p] -> M^2,
  SP[p1, p1] -> m1^2,
  SP[p2, p2] -> m2^2,
  SP[p3, p3] -> m3^2
};
```

---

## Massless Limit

When all final-state particles are massless ($m_1 = m_2 = m_3 = 0$), the formulas simplify considerably:

$$
d\Gamma = \frac{1}{(2\pi)^3} \frac{1}{32 M^3} |\mathcal{M}|^2 \, dm_{12}^2 \, dm_{23}^2
$$

with boundaries:
- $m_{12}^2 \in [0,\, M^2]$
- $m_{23}^2 \in [0,\, M^2 - m_{12}^2]$

The invariant mass constraint becomes $m_{12}^2 + m_{13}^2 + m_{23}^2 = M^2$.

---

## When to Use Three-Body Phase Space

- **Muon decay:** $\mu \to e\bar{\nu}_e\nu_\mu$ (after integrating out the $W$ boson, this is a four-fermion contact interaction with constant $|\mathcal{M}|^2$ in the massless limit)
- **Three-body meson decays:** e.g., $K \to \pi\pi\pi$
- **Off-shell intermediate resonances:** when an intermediate particle is far off-shell and the narrow-width approximation breaks down
- **Radiative decays with massive particles:** e.g., $\mu \to e\gamma\nu$ if treated as a 3-body final state

---

## Pitfalls

1. **Integration region.** The Dalitz plot boundaries are nontrivial functions of $m_{12}^2$. Using constant limits for $m_{23}^2$ will give incorrect results.

2. **Narrow resonances.** If the amplitude contains a Breit-Wigner resonance (e.g., $|\mathcal{M}|^2 \propto 1/((m_{12}^2 - M_R^2)^2 + M_R^2 \Gamma_R^2)$), numerical integration requires care. Use adaptive integration or split the integration region around the resonance peak.

3. **Identical particles.** For identical particles in the final state, include the appropriate symmetry factor ($1/n!$ for $n$ identical particles).

4. **Spin averaging.** The formula assumes $|\mathcal{M}|^2$ is already spin-averaged over initial states and summed over final states, consistent with the two-body convention.

5. **Phase space vs. matrix element.** The three-body phase space measure $dm_{12}^2\, dm_{23}^2$ is flat. All nontrivial kinematic structure comes from $|\mathcal{M}|^2$.

---

## Related Documents

- [phase_space.two_body] -- Two-body phase space formulas
- [phase_space.mandelstam] -- Mandelstam variables for 2->2 scattering
- [procedures.decay_width_1to2] -- Complete procedure for 1->2 decay widths
