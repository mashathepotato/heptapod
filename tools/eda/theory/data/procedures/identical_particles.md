# Identical Particles and Symmetry Factors

**Node ID:** `procedures.identical_particles`
**Category:** procedure

## Overview

When a process has identical particles in the final state, the squared amplitude and phase-space integration must account for the indistinguishability of these particles. This document covers the symmetry factors, the statistical signs from Fermi and Bose statistics, and how to implement these correctly in FeynCalc calculations.

---

## The Symmetry Factor Rule

If there are $n_j$ identical particles of type $j$ in the final state, the decay width or cross section includes a **symmetry factor**:

$$
S = \prod_j \frac{1}{n_j!}
$$

This factor prevents double-counting of identical final-state configurations in the phase-space integration.

### Common Cases

| Final state | Symmetry factor $S$ |
|---|---|
| Two distinguishable particles ($a b$) | $1$ |
| Two identical particles ($a a$) | $1/2!= 1/2$ |
| Three identical particles ($a a a$) | $1/3! = 1/6$ |
| Two identical pairs ($a a b b$) | $1/(2! \times 2!) = 1/4$ |
| $n$ identical photons | $1/n!$ |

### Where the Factor Enters

The symmetry factor multiplies the integrated rate:

$$
\Gamma(A \to 1\,2) = S \cdot \frac{|\mathbf{p}|}{8\pi M^2} \cdot \frac{1}{n_{\text{init}}} \sum_{\text{spins}} |\mathcal{M}|^2
$$

$$
\sigma = S \cdot \int \frac{d\sigma}{dt}\,dt
$$

The squared amplitude $|\mathcal{M}|^2$ itself is **not** modified by $S$. The factor applies only to the phase-space integral.

---

## Bose Statistics: Identical Bosons

### Symmetrization of the Amplitude

When two identical bosons appear in the final state, the total amplitude must be **symmetric** under their exchange. If the Feynman rules produce an amplitude $\mathcal{M}(p_1, p_2)$ for a specific momentum assignment, the symmetrized amplitude is:

$$
\mathcal{M}_{\text{sym}} = \mathcal{M}(p_1, p_2) + \mathcal{M}(p_2, p_1)
$$

The relative **plus sign** comes from Bose-Einstein statistics.

### Important Subtlety

In practice, many textbooks and codes use a different but equivalent convention:

**Convention A (symmetrize amplitude, include $1/n!$):**

$$
\Gamma = \frac{1}{2!} \cdot \frac{|\mathbf{p}|}{8\pi M^2} \sum |\mathcal{M}_{\text{sym}}|^2
$$

**Convention B (unsymmetrized amplitude, include $1/n!$):**

If the Feynman rules already produce the correct amplitude for a definite momentum assignment, and you integrate over the full phase space, you include $1/n!$ to compensate for the overcounting:

$$
\Gamma = \frac{1}{2!} \cdot \frac{|\mathbf{p}|}{8\pi M^2} \sum |\mathcal{M}(p_1, p_2)|^2
$$

Convention B is standard in most textbook treatments and is what we use here.

**When do you need Convention A?** When there are multiple diagrams where the symmetrization is not automatically handled by summing over all diagrams. In that case, you must explicitly symmetrize.

### Example: $H \to \gamma\gamma$

The decay $H \to \gamma\gamma$ has two identical photons in the final state:

$$
\Gamma(H \to \gamma\gamma) = \frac{1}{2} \cdot \frac{|\mathbf{p}|}{8\pi M_H^2} \sum_{\text{pol}} |\mathcal{M}|^2
$$

The factor $1/2$ accounts for the two identical photons.

### FeynCalc Code

```mathematica
(* === Identical bosons: H -> gamma gamma === *)

(* Compute |M|^2 as usual (loop amplitude, not shown here) *)
(* ... ampSqFinal contains the spin-summed squared amplitude ... *)

(* Apply symmetry factor *)
nIdentical = 2; (* two identical photons *)
symmetryFactor = 1/Factorial[nIdentical];

(* Decay width *)
pMag = mH/2; (* massless photons *)
decayWidth = symmetryFactor * (pMag / (8 Pi mH^2)) * ampSqFinal // Simplify;
```

---

## Fermi Statistics: Identical Fermions

### Antisymmetrization of the Amplitude

When two identical fermions appear in the final state, the total amplitude must be **antisymmetric** under their exchange. The antisymmetrized amplitude is:

$$
\mathcal{M}_{\text{anti}} = \mathcal{M}(p_1, s_1; p_2, s_2) - \mathcal{M}(p_2, s_2; p_1, s_1)
$$

The relative **minus sign** comes from Fermi-Dirac statistics.

### When Does This Matter?

This is relevant when there are two or more identical fermions in the final state AND there exist multiple Feynman diagrams that differ by the exchange of these fermions.

**Example:** In $e^+e^- \to e^+e^-$ (Bhabha scattering), the final-state $e^+$ and $e^-$ are distinguishable, so no antisymmetrization is needed. But in $e^-e^- \to e^-e^-$ (Moller scattering), the two final-state electrons are identical.

### Example: Moller Scattering ($e^-e^- \to e^-e^-$)

Two diagrams contribute: t-channel and u-channel photon exchange. The amplitudes $\mathcal{M}_t$ and $\mathcal{M}_u$ are related by exchanging the two final-state electrons ($p_3 \leftrightarrow p_4$).

Fermi statistics demands:

$$
\mathcal{M}_{\text{total}} = \mathcal{M}_t - \mathcal{M}_u
$$

The **relative minus sign** encodes the antisymmetry under fermion exchange.

### FeynCalc Code

```mathematica
(* === Identical fermions: Moller scattering e-e- -> e-e- === *)

<< FeynCalc`

(* t-channel diagram: electron 1 scatters to electron 3, *)
(*                    electron 2 scatters to electron 4   *)
ampT = SpinorUBar[p3, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
       (-I MTD[mu, nu] / SP[p1 - p3, p1 - p3]) *
       SpinorUBar[p4, me] . (-I e GAD[nu]) . SpinorU[p2, me];

(* u-channel diagram: electron 1 scatters to electron 4, *)
(*                    electron 2 scatters to electron 3   *)
(* This is the EXCHANGED diagram: p3 <-> p4               *)
ampU = SpinorUBar[p4, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
       (-I MTD[mu, nu] / SP[p1 - p4, p1 - p4]) *
       SpinorUBar[p3, me] . (-I e GAD[nu]) . SpinorU[p2, me];

(* MINUS sign from Fermi statistics *)
ampTotal = ampT - ampU;

(* Square, spin-sum, trace *)
ampTotalSq = FermionSpinSum[ampTotal * ComplexConjugate[ampTotal]];
result = DiracSimplify[ampTotalSq] // Contract;

(* Apply Mandelstam variables *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, me, me, me, me];
resultMandel = TrickMandelstam[result, {s, t, u, 4 me^2}] // Simplify;

(* Cross section with symmetry factor 1/2 for identical final-state particles *)
n1 = 2; n2 = 2;
symmetryFactor = 1/2;
dsigmaDt = symmetryFactor / (16 Pi Kallen[s, me^2, me^2]) *
           (1/(n1 n2)) * resultMandel;
```

### Clarification: Sign vs. Symmetry Factor

The relative minus sign and the $1/n!$ symmetry factor are **independent** and both required:

1. **Relative minus sign** ($-$): Comes from antisymmetry of the fermion wave function. It affects the amplitude and therefore the interference term in $|\mathcal{M}|^2$. It changes the physics (constructive vs. destructive interference).

2. **Symmetry factor** ($1/2$): Comes from overcounting in phase-space integration. Two identical particles in the final state means each physical configuration is counted twice when integrating over all of phase space.

Both must be included. They serve different purposes.

---

## Identical Particles in Decay Widths

### Two Identical Particles

For $A \to 1 + 1$ (e.g., $H \to gg$ or $\pi^0 \to \gamma\gamma$):

$$
\Gamma = \frac{1}{2} \cdot \frac{|\mathbf{p}|}{8\pi M^2} \cdot \frac{1}{n_{\text{init}}} \sum |\mathcal{M}|^2
$$

### Three Identical Particles

For $A \to 1 + 1 + 1$:

$$
\Gamma = \frac{1}{6} \cdot (\text{phase-space integral}) \cdot \frac{1}{n_{\text{init}}} \sum |\mathcal{M}|^2
$$

### FeynCalc Code Template

```mathematica
(* === General template for identical particles in decays === *)

(* After computing ampSqFinal (spin-summed, traces evaluated, *)
(* kinematics substituted):                                     *)

(* Count identical particles in final state *)
nIdenticalBosons = 2;  (* e.g., 2 photons *)
nIdenticalFermions = 0;
symmetryFactor = 1 / (Factorial[nIdenticalBosons] * Factorial[nIdenticalFermions]);

(* For decay width *)
decayWidth = symmetryFactor * (pMag / (8 Pi M^2)) * (1/nInit) * ampSqFinal;

(* For cross section *)
sigmaTot = symmetryFactor * Integrate[dsigmaDt, {t, tMinus, tPlus}];
```

---

## Identical Particles in Cross Sections

For $2 \to 2$ scattering with identical final-state particles, both the amplitude structure and the phase-space factor are affected.

### Amplitude Structure

When two diagrams are related by exchanging identical final-state particles:

- **Identical bosons:** $\mathcal{M} = \mathcal{M}_{\text{direct}} + \mathcal{M}_{\text{exchange}}$ (plus sign)
- **Identical fermions:** $\mathcal{M} = \mathcal{M}_{\text{direct}} - \mathcal{M}_{\text{exchange}}$ (minus sign)

### Phase-Space Factor

The total cross section includes $S = 1/2$:

$$
\sigma = \frac{1}{2} \int \frac{d\sigma}{dt}\,dt
$$

### Relation Between $t$ and $u$ Channels

For identical final-state particles, the u-channel diagram is the exchange of the t-channel diagram. The total squared amplitude automatically has the structure:

$$
|\mathcal{M}|^2 = |\mathcal{M}_t|^2 + |\mathcal{M}_u|^2 \pm 2\,\text{Re}(\mathcal{M}_t^* \mathcal{M}_u)
$$

where $+$ is for bosons and $-$ is for fermions. The interference term introduces a dependence on $tu$ that integrates to a non-trivial contribution.

---

## Summary Table

| Situation | Amplitude modification | Phase-space factor |
|---|---|---|
| All particles distinguishable | None | $S = 1$ |
| 2 identical bosons in final state | $\mathcal{M} = \mathcal{M}_1 + \mathcal{M}_2$ (if exchange diagram exists) | $S = 1/2$ |
| 2 identical fermions in final state | $\mathcal{M} = \mathcal{M}_1 - \mathcal{M}_2$ (relative minus) | $S = 1/2$ |
| $n$ identical particles of one type | Appropriate (anti)symmetrization | $S = 1/n!$ |
| Mixed: $n_a$ of type $a$, $n_b$ of type $b$ | (Anti)symmetrize within each group | $S = 1/(n_a! \, n_b!)$ |

---

## Common Pitfalls

1. **Confusing the sign and the symmetry factor.** The relative minus sign for identical fermions is part of the amplitude (it changes the interference term). The $1/n!$ factor is a separate phase-space correction. Both are needed.

2. **Applying the symmetry factor to $|\mathcal{M}|^2$ instead of $\Gamma$ or $\sigma$.** The factor $1/n!$ multiplies the integrated rate, not the squared amplitude. In the differential rate $d\Gamma$ or $d\sigma/dt$, it appears as an overall prefactor.

3. **Forgetting to antisymmetrize.** If you write down only the t-channel diagram for identical-fermion scattering and forget the u-channel with its relative minus sign, the result will be wrong even before applying the $1/2$ factor.

4. **Double-counting when diagrams already include the exchange.** If you enumerate diagrams using a tool that already generates both the direct and exchange diagrams as separate contributions, do not add an additional symmetrization. The relative sign must still be correct.

5. **Identical particles in the initial state.** For identical particles in the initial state (e.g., $pp$ collisions, $e^-e^-$ scattering), there is an additional factor of $1/2$ in the flux factor. This is distinct from the final-state symmetry factor. In the formula $d\sigma/dt = |\mathcal{M}|^2 / (16\pi\lambda)$, the flux factor is already included; the initial-state $1/2$ is an additional correction for identical beams.

6. **Interference between non-exchange diagrams.** Not all interference is related to particle exchange. Two diagrams may interfere even for distinguishable particles (e.g., s-channel and t-channel in Bhabha scattering). See [procedures.interference] for the general treatment.

---

## Related Documents

- [procedures.decay_width_1to2] -- Decay width formula where the symmetry factor enters
- [procedures.cross_section_2to2] -- Cross section formula where the symmetry factor enters
- [phase_space.two_body] -- Two-body phase space integration details
- [procedures.interference] -- General treatment of interference between diagrams
