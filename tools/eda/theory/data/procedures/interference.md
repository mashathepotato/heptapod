# Interference Between Diagrams

**Node ID:** `procedures.interference`
**Category:** procedure

## Overview

When multiple Feynman diagrams contribute to the same process (same initial and final states), their amplitudes must be added coherently before squaring. This document explains when and how interference arises, provides the FeynCalc procedure for computing interference terms, and describes situations where interference vanishes.

---

## Fundamental Principle

Quantum mechanics requires that we sum amplitudes, not probabilities. If diagrams $1, 2, \ldots, n$ contribute to the same process:

$$
\mathcal{M}_{\text{total}} = \mathcal{M}_1 + \mathcal{M}_2 + \cdots + \mathcal{M}_n
$$

The squared amplitude is:

$$
|\mathcal{M}_{\text{total}}|^2 = \sum_i |\mathcal{M}_i|^2 + \sum_{i < j} 2\,\text{Re}(\mathcal{M}_i^* \mathcal{M}_j)
$$

The **interference terms** are the cross terms $2\,\text{Re}(\mathcal{M}_i^* \mathcal{M}_j)$ with $i \neq j$.

### Two-Diagram Case

For two diagrams:

$$
|\mathcal{M}|^2 = |\mathcal{M}_1|^2 + |\mathcal{M}_2|^2 + 2\,\text{Re}(\mathcal{M}_1^* \mathcal{M}_2)
$$

The interference term can be positive, negative, or zero depending on the relative phase between the amplitudes and the kinematics.

---

## When Diagrams Interfere

Diagrams interfere when they connect the **same initial state** to the **same final state** with the **same quantum numbers**. Specifically:

1. **Same external particles.** Both diagrams must have identical sets of incoming and outgoing particles (same flavors, momenta assignments).

2. **Same helicity/spin configuration.** After summing over spins, interference survives if the diagrams can contribute to at least one common helicity configuration.

3. **Same internal quantum numbers.** The diagrams must be able to produce the same color, flavor, or other conserved quantum number configuration in the final state.

### Common Examples of Interfering Diagrams

- **s-channel and t-channel diagrams** in $e^+e^- \to e^+e^-$ (Bhabha scattering): the photon can be exchanged in either channel.
- **W and Z exchange** in processes where both contribute (e.g., neutrino scattering).
- **Multiple Feynman diagrams at the same order** in perturbation theory with different internal topologies but identical external states.

---

## When Interference Vanishes

Interference vanishes ($\mathcal{M}_1^* \mathcal{M}_2 = 0$ after spin/color sums) in these cases:

### 1. Different Color Structures

If diagram 1 produces a color singlet via one path and diagram 2 via a different path that is orthogonal in color space, the color trace of the interference term vanishes.

**Example:** In gluon-gluon scattering, certain diagram pairs have orthogonal color structures:
$$
\text{Tr}(T^a T^b T^c T^d) \neq \text{Tr}(T^a T^c T^b T^d)
$$
These are different but not necessarily orthogonal. However, for some processes, specific color structures are truly orthogonal.

### 2. Orthogonal Helicity Configurations

If diagram 1 only contributes to helicity configuration $(+,+,-,-)$ and diagram 2 only to $(+,-,+,-)$, they never interfere after helicity summation.

### 3. Different Intermediate States with Definite Quantum Numbers

If the intermediate states carry different conserved quantum numbers (e.g., different total angular momentum), the interference vanishes after angular integration.

### 4. Different Final-State Flavors in Subprocesses

If diagram 1 produces a final-state particle through one flavor channel and diagram 2 through a different flavor channel that are distinguishable, there is no interference.

**Example:** $H \to b\bar{b}$ and $H \to c\bar{c}$ do not interfere because the final states are distinguishable.

---

## FeynCalc Procedure for Interference Terms

### Method 1: Direct Computation (Recommended)

The most straightforward approach is to sum all amplitudes before squaring.

```mathematica
(* === Method 1: Sum amplitudes then square === *)

(* Define individual diagram amplitudes *)
amp1 = SpinorVBar[p2, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
       (-I MTD[mu, nu] / SP[p1 + p2, p1 + p2]) *
       SpinorUBar[p3, me] . (-I e GAD[nu]) . SpinorV[p4, me];

amp2 = SpinorVBar[p2, me] . (-I e GAD[mu]) . SpinorV[p4, me] *
       (-I MTD[mu, nu] / SP[p1 - p3, p1 - p3]) *
       SpinorUBar[p3, me] . (-I e GAD[nu]) . SpinorU[p1, me];

(* Total amplitude *)
ampTotal = amp1 + amp2;

(* Square, spin-sum, trace *)
ampTotalCC = ComplexConjugate[ampTotal];
ampTotalSq = ampTotal * ampTotalCC;
ampTotalSqSummed = FermionSpinSum[ampTotalSq];
ampTotalSqTraced = DiracSimplify[ampTotalSqSummed] // Contract;

(* This automatically includes all interference terms *)
```

**Advantage:** Simple and correct. FeynCalc handles the cross terms automatically when the product $(M_1 + M_2)(M_1^* + M_2^*)$ is expanded.

**Disadvantage:** For many diagrams, the intermediate expressions can be very large.

### Method 2: Compute Interference Terms Separately

When you want to isolate the interference contribution (for example, to check its relative size or sign), compute each piece individually.

```mathematica
(* === Method 2: Separate pieces === *)

(* Individual squared amplitudes *)
amp1Sq = FermionSpinSum[amp1 * ComplexConjugate[amp1]];
amp1SqTraced = DiracSimplify[amp1Sq] // Contract;

amp2Sq = FermionSpinSum[amp2 * ComplexConjugate[amp2]];
amp2SqTraced = DiracSimplify[amp2Sq] // Contract;

(* Interference term: M1* M2 + M1 M2* = 2 Re(M1* M2) *)
(* Compute M1* M2 *)
intTerm12 = FermionSpinSum[ComplexConjugate[amp1] * amp2];
intTerm12Traced = DiracSimplify[intTerm12] // Contract;

(* And its conjugate M1 M2* *)
intTerm21 = FermionSpinSum[amp1 * ComplexConjugate[amp2]];
intTerm21Traced = DiracSimplify[intTerm21] // Contract;

(* The full interference contribution *)
interference = intTerm12Traced + intTerm21Traced // Simplify;
(* This equals 2 Re(M1* M2) after spin sums *)

(* Verify: total should equal the sum *)
totalCheck = amp1SqTraced + amp2SqTraced + interference // Simplify;
(* Should match ampTotalSqTraced from Method 1 *)
```

**Pitfall:** The interference term `ComplexConjugate[amp1] * amp2` is not real in general before spin sums. Only after summing over spins and taking the real part (by adding the conjugate term) do you get the physical interference contribution.

---

## Handling Fermion Line Routing in Interference

When diagrams have different fermion line routing (e.g., s-channel vs t-channel in $e^+e^- \to e^+e^-$), the interference term involves traces that connect spinors in a different order than either individual diagram.

### Example: Bhabha Scattering Interference

In the s-channel diagram, the fermion lines are:
- Line 1: $\bar{v}(p_2) \Gamma^\mu u(p_1)$
- Line 2: $\bar{u}(p_3) \Gamma^\nu v(p_4)$

In the t-channel diagram, the fermion lines are:
- Line 1: $\bar{u}(p_3) \Gamma^\mu u(p_1)$
- Line 2: $\bar{v}(p_2) \Gamma^\nu v(p_4)$

The interference term $\mathcal{M}_s^* \mathcal{M}_t$ mixes these line routings, producing a **single** trace over all four external momenta rather than a product of two traces:

$$
\text{Interference} \propto \text{Tr}[\not{p}_1 \gamma^\mu \not{p}_2 \gamma^\nu \not{p}_4 \gamma_\mu \not{p}_3 \gamma_\nu]
$$

### FeynCalc Code for Fermion Line Rerouting

```mathematica
(* FeynCalc handles this automatically when you use the direct method *)
(* (Method 1 above). FermionSpinSum correctly identifies the spinor *)
(* chains and contracts them into the appropriate traces.             *)

(* If doing it manually, the key insight is that the interference *)
(* term produces a SINGLE trace over all gamma matrices, unlike   *)
(* the individual squared amplitudes which give PRODUCTS of two   *)
(* smaller traces.                                                  *)
```

**Pitfall:** When computing interference terms manually (without `FermionSpinSum`), it is easy to make errors in the fermion line routing. The trace structure of the interference term is generically different from that of the individual squared amplitudes. Always let FeynCalc handle the spinor algebra via `FermionSpinSum`.

---

## Relative Signs Between Interfering Diagrams

### Relative Fermion Signs

When two diagrams differ by the exchange of two identical external fermions, they carry a **relative minus sign** from Fermi statistics. This sign is part of the amplitude, not the interference.

```mathematica
(* If diagrams differ by exchange of two identical fermion lines, *)
(* one amplitude gets an explicit minus sign:                      *)
amp2 = -1 * (amplitude from exchanged diagram);
```

### Relative Coupling Signs

Different diagrams may involve different coupling constants (e.g., vector vs. axial-vector couplings). These relative signs propagate into the interference term and can cause constructive or destructive interference.

---

## Practical Checklist

Before computing, determine:

1. **How many diagrams contribute?** Enumerate all diagrams at the desired order.
2. **Do they interfere?** Check that they connect the same initial and final states with consistent quantum numbers.
3. **What are the relative signs?** Account for fermion exchange signs and coupling signs.
4. **Is the interference term significant?** Sometimes interference is suppressed (e.g., by small coupling ratios or kinematic factors) and can be neglected for estimates.

### Decision Flowchart

```
Are the initial AND final states identical?
  NO  --> No interference. Compute |M_i|^2 separately and sum.
  YES --> Do the diagrams share at least one helicity configuration?
            NO  --> Interference vanishes after spin sum.
            YES --> Do the diagrams have the same color structure?
                      NO  --> Check if color trace of cross term vanishes.
                      YES --> Full interference. Compute using Method 1 or 2.
```

---

## Complete Example: Bhabha Scattering Interference

```mathematica
(* ================================================ *)
(* Interference in Bhabha Scattering: e+e- -> e+e-  *)
(* s-channel + t-channel photon exchange             *)
(* ================================================ *)

<< FeynCalc`

(* s-channel amplitude *)
ampS = SpinorVBar[p2, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
       (-I MTD[mu, nu] / (SP[p1 + p2, p1 + p2])) *
       SpinorUBar[p3, me] . (-I e GAD[nu]) . SpinorV[p4, me];

(* t-channel amplitude *)
(* Note: relative sign from fermion line crossing *)
ampT = -(
  SpinorUBar[p3, me] . (-I e GAD[mu]) . SpinorU[p1, me] *
  (-I MTD[mu, nu] / (SP[p1 - p3, p1 - p3])) *
  SpinorVBar[p2, me] . (-I e GAD[nu]) . SpinorV[p4, me]
);

(* Total amplitude *)
ampTotal = ampS + ampT;

(* Square, spin-sum, trace *)
ampTotalSq = FermionSpinSum[ampTotal * ComplexConjugate[ampTotal]];
result = DiracSimplify[ampTotalSq] // Contract;

(* Express in Mandelstam variables *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, me, me, me, me];
resultMandel = TrickMandelstam[result, {s, t, u, 4 me^2}] // Simplify;

(* Separate into pieces for inspection *)
(* |Ms|^2 *)
ampSSq = FermionSpinSum[ampS * ComplexConjugate[ampS]];
resultS = DiracSimplify[ampSSq] // Contract;
resultSMandel = TrickMandelstam[resultS, {s, t, u, 4 me^2}] // Simplify;

(* |Mt|^2 *)
ampTSq = FermionSpinSum[ampT * ComplexConjugate[ampT]];
resultT = DiracSimplify[ampTSq] // Contract;
resultTMandel = TrickMandelstam[resultT, {s, t, u, 4 me^2}] // Simplify;

(* Interference: total - |Ms|^2 - |Mt|^2 *)
interferenceMantel = resultMandel - resultSMandel - resultTMandel // Simplify;

Print["s-channel: ", resultSMandel];
Print["t-channel: ", resultTMandel];
Print["Interference: ", interferenceMantel];
Print["Total: ", resultMandel];
```

---

## Common Pitfalls

1. **Forgetting to sum amplitudes before squaring.** The most common error is to compute $|\mathcal{M}_1|^2 + |\mathcal{M}_2|^2$ and forget the interference term. This gives an incorrect result whenever diagrams interfere.

2. **Wrong relative sign for fermion exchange.** When two diagrams differ by exchanging identical external fermions, there is a relative minus sign. Missing this sign flips the interference from constructive to destructive (or vice versa).

3. **Assuming interference always vanishes.** While interference vanishes in specific cases (orthogonal color, orthogonal helicity), it is present in the general case. Always check explicitly.

4. **Trace structure of interference.** The interference term may produce a single long trace instead of a product of short traces. This is not an error; it is the correct structure when fermion lines are rerouted between diagrams.

5. **Complex couplings.** If couplings are complex (e.g., CKM matrix elements, CP-violating phases), the interference term $\text{Re}(\mathcal{M}_1^* \mathcal{M}_2)$ depends on the relative phase. Do not assume couplings are real unless justified.

6. **Gauge dependence of individual diagrams.** Individual Feynman diagrams are not gauge-invariant. Only the total amplitude (sum of all diagrams at a given order) is gauge-invariant. Interference terms between individual diagrams can be gauge-dependent; only the total $|\mathcal{M}|^2$ is physical.

---

## Related Documents

- [procedures.decay_width_1to2] -- Apply this after computing the total squared amplitude for a decay
- [procedures.cross_section_2to2] -- Apply this after computing the total squared amplitude for scattering
- [feyncalc_reference.spinors_and_traces] -- FeynCalc trace evaluation functions
- [procedures.identical_particles] -- Additional sign factors from identical particles
