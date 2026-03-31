# Two-Body Phase Space

**Node ID:** `phase_space.two_body`
**Category:** phase_space

## Overview

This document gives the complete formulas for the two-body (1->2) decay phase space. The decay width for $A \to 1\, 2$ is expressed in terms of the spin-averaged squared amplitude and the kinematic function of the masses. All scalar products of external momenta are fully determined by the masses alone, making the two-body case analytically tractable. Each formula includes the corresponding Mathematica/FeynCalc code.

---

## Decay Width Formula

$$
\Gamma = \frac{|\mathbf{p}|}{8\pi M^2} \overline{|\mathcal{M}|^2}
$$

where:
- $M$ is the decaying particle mass
- $|\mathbf{p}|$ is the magnitude of the 3-momentum of either final-state particle in the rest frame
- $\overline{|\mathcal{M}|^2}$ is the spin-averaged, spin-summed squared amplitude

**Convention:** The bar denotes averaging over initial spins and summing over final spins. If $|\mathcal{M}|^2$ is summed over ALL spins (no averaging), divide by $(2s+1)$ for the initial particle spin $s$.

---

## Momentum Magnitude

$$
|\mathbf{p}| = \frac{\lambda^{1/2}(M^2, m_1^2, m_2^2)}{2M}
$$

where the **Kallen (triangle) function** is:

$$
\lambda(a,b,c) = a^2 + b^2 + c^2 - 2ab - 2ac - 2bc
$$

### Alternative form

$$
|\mathbf{p}| = \frac{1}{2M}\sqrt{M^4 - 2M^2(m_1^2 + m_2^2) + (m_1^2 - m_2^2)^2}
$$

This can also be factored as:

$$
|\mathbf{p}| = \frac{M}{2}\sqrt{\left(1 - \frac{(m_1+m_2)^2}{M^2}\right)\left(1 - \frac{(m_1-m_2)^2}{M^2}\right)}
$$

### Equal mass case ($m_1 = m_2 = m$)

$$
|\mathbf{p}| = \frac{M}{2}\sqrt{1 - \frac{4m^2}{M^2}}
$$

---

## Kinematics in the Rest Frame

In the decaying particle's rest frame, the momenta are:

$$
p = (M, \mathbf{0}), \qquad p_1 = (E_1, \mathbf{p}), \qquad p_2 = (E_2, -\mathbf{p})
$$

The energies of the decay products are:

$$
E_1 = \frac{M^2 + m_1^2 - m_2^2}{2M}
$$

$$
E_2 = \frac{M^2 + m_2^2 - m_1^2}{2M}
$$

These follow from energy-momentum conservation $p = p_1 + p_2$ and the on-shell conditions.

---

## Scalar Products from Kinematics

All Lorentz-invariant scalar products are completely fixed by the masses:

$$
p_1 \cdot p_2 = \frac{M^2 - m_1^2 - m_2^2}{2}
$$

$$
p \cdot p_1 = \frac{M^2 + m_1^2 - m_2^2}{2}
$$

$$
p \cdot p_2 = \frac{M^2 + m_2^2 - m_1^2}{2}
$$

These are derived from the on-shell conditions $p^2 = M^2$, $p_i^2 = m_i^2$, and momentum conservation $p = p_1 + p_2$.

---

## Mathematica Code for Numerical Evaluation

```mathematica
(* Kallen function *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;

(* 3-momentum magnitude *)
pMag[M_, m1_, m2_] := Sqrt[Kallen[M^2, m1^2, m2^2]] / (2 M);

(* Decay width from spin-averaged |M|^2 *)
DecayWidth[M_, m1_, m2_, ampSqAvg_] := pMag[M, m1, m2] / (8 Pi M^2) * ampSqAvg;

(* Apply kinematic replacements to symbolic |M|^2 *)
kinematicRules[M_, m1_, m2_] := {
  SP[p1, p2] -> (M^2 - m1^2 - m2^2)/2,
  SP[p, p1] -> (M^2 + m1^2 - m2^2)/2,
  SP[p, p2] -> (M^2 + m2^2 - m1^2)/2,
  SP[p, p] -> M^2,
  SP[p1, p1] -> m1^2,
  SP[p2, p2] -> m2^2
};
```

### FeynCalc-Compatible Replacement Rules

When using FeynCalc, scalar products are stored internally as `Pair[Momentum[...], Momentum[...]]`. Use the following rules for direct substitution:

```mathematica
(* FeynCalc internal representation replacement rules *)
kinematicRulesFC[M_, m1_, m2_] := {
  Pair[Momentum[p], Momentum[p]] -> M^2,
  Pair[Momentum[p1], Momentum[p1]] -> m1^2,
  Pair[Momentum[p2], Momentum[p2]] -> m2^2,
  Pair[Momentum[p], Momentum[p1]] -> (M^2 + m1^2 - m2^2)/2,
  Pair[Momentum[p], Momentum[p2]] -> (M^2 + m2^2 - m1^2)/2,
  Pair[Momentum[p1], Momentum[p2]] -> (M^2 - m1^2 - m2^2)/2
};
```

---

## Pitfalls

1. **Spin averaging convention.** The formula $\Gamma = |\mathbf{p}|/(8\pi M^2) \overline{|\mathcal{M}|^2}$ assumes $\overline{|\mathcal{M}|^2}$ is SUMMED over final spins and AVERAGED over initial spins. If $|\mathcal{M}|^2$ is summed over ALL spins (no averaging), divide by $(2s+1)$ for the initial particle spin $s$ (i.e., 1 for scalars, 2 for spin-1/2, 3 for massive spin-1).

2. **Identical particles.** For identical particles in the final state (e.g., $H \to \gamma\gamma$), include a symmetry factor of $1/2!$ in the decay width.

3. **Kinematic threshold.** The Kallen function becomes negative if the decay is kinematically forbidden ($M < m_1 + m_2$), making $|\mathbf{p}|$ imaginary. Always verify that $M > m_1 + m_2$ before evaluating.

4. **Color factors.** For decays to quarks, the squared amplitude must include a color factor $N_c = 3$. This is not automatically included in manually constructed amplitudes.

5. **FeynCalc internal representation.** FeynCalc stores dot products as `Pair[Momentum[p1], Momentum[p2]]`, not `SP[p1, p2]`. Use `FCI` to convert between external (`SP`) and internal (`Pair`) notation, or write replacement rules in the internal form.

---

## Related Documents

- [procedures.decay_width_1to2] -- Complete step-by-step procedure for computing 1->2 decay widths
- [phase_space.three_body] -- Three-body phase space formulas
- [phase_space.mandelstam] -- Mandelstam variables for 2->2 scattering
- [spin_sums.fermion_spin_sum] -- Fermion spin sum completeness relations
- [spin_sums.vector_polarization_sum] -- Polarization sums for vector bosons
