# 1->2 Decay Width Procedure

**Node ID:** `procedures.decay_width_1to2`
**Category:** procedure

## Overview

This document gives the complete step-by-step recipe for computing the partial decay width $\Gamma(A \to 1\, 2)$ of a particle $A$ with mass $M$ decaying into two particles with masses $m_1$ and $m_2$. The procedure is valid for any 1->2 decay in any renormalizable QFT. Each step includes the corresponding FeynCalc Mathematica code.

---

## Master Formula

The decay width for a two-body decay is:

$$
\Gamma(A \to 1\, 2) = \frac{|\mathbf{p}|}{8\pi M^2} \cdot \frac{1}{n_{\text{init}}} \sum_{\text{spins}} |\mathcal{M}|^2
$$

where:
- $|\mathbf{p}|$ is the magnitude of the 3-momentum of either final-state particle in the rest frame of $A$
- $M$ is the mass of the decaying particle
- $n_{\text{init}}$ is the number of spin/polarization states of the initial particle (1 for scalars, 2 for massive fermions, 3 for massive vectors, 2 for massless vectors)
- $\sum_{\text{spins}} |\mathcal{M}|^2$ is the spin-summed (not averaged) squared amplitude

---

## Step 1: Write the Amplitude from Feynman Rules

Identify the Feynman diagram(s) and write the invariant amplitude $\mathcal{M}$ using the Feynman rules. Assign momenta $p$ to the decaying particle and $p_1$, $p_2$ to the final-state particles, with $p = p_1 + p_2$.

**Scalar vertex example** ($H \to f\bar{f}$, Yukawa coupling):

$$
i\mathcal{M} = -i \frac{y_f}{\sqrt{2}} \bar{u}(p_1) v(p_2)
$$

**Vector vertex example** ($Z \to f\bar{f}$):

$$
i\mathcal{M} = -i \frac{g}{2\cos\theta_W} \bar{u}(p_1) \gamma^\mu (g_V - g_A \gamma^5) v(p_2)\, \varepsilon_\mu(p)
$$

### FeynCalc Code

```mathematica
(* === Step 1: Define the amplitude === *)

(* Example: H -> b bbar (scalar Yukawa vertex) *)
(* u(p1) . (-i yb / Sqrt[2]) . v(p2) *)
amp = SpinorUBar[p1, mb] . (- I yb / Sqrt[2]) . SpinorV[p2, mb];

(* Example: Z -> f fbar (vector vertex with V-A coupling) *)
(* u(p1) . (-i g/(2 cw)) gamma^mu (gV - gA gamma^5) . v(p2) . eps_mu(p) *)
amp = SpinorUBar[p1, mf] . (-I gz/2) GAD[mu] . (gV - gA GA[5]) . SpinorV[p2, mf] *
      PolarizationVector[p, mu];
```

**See:** [feynman_rules.vertices_scalar], [feynman_rules.vertices_vector]

---

## Step 2: Compute the Squared Amplitude |M|^2

The squared amplitude is:

$$
|\mathcal{M}|^2 = \mathcal{M} \mathcal{M}^*
$$

In FeynCalc, the complex conjugate of a fermion amplitude is obtained with `ComplexConjugate`, which reverses spinor chains and conjugates couplings.

### FeynCalc Code

```mathematica
(* === Step 2: Square the amplitude === *)

ampCC = ComplexConjugate[amp];
ampSq = amp * ampCC;
```

**Pitfall:** `ComplexConjugate` automatically handles the reversal of spinor chains ($\bar{u} \Gamma v \to \bar{v} \bar{\Gamma} u$) and the complex conjugation of $\gamma^5$ terms. Do NOT manually reverse spinor ordering.

---

## Step 3: Apply Spin and Polarization Sums

Sum over the spins of all final-state particles and, if the initial particle has spin, also sum over its polarization states. The initial-state averaging factor $1/n_{\text{init}}$ is applied separately in the final formula.

**Fermion spin sums:**

$$
\sum_s u(p,s)\bar{u}(p,s) = \not{p} + m, \qquad \sum_s v(p,s)\bar{v}(p,s) = \not{p} - m
$$

**Massive vector polarization sum:**

$$
\sum_\lambda \varepsilon_\mu(\lambda) \varepsilon_\nu^*(\lambda) = -g_{\mu\nu} + \frac{p_\mu p_\nu}{M_V^2}
$$

### FeynCalc Code

```mathematica
(* === Step 3: Spin/polarization sums === *)

(* FermionSpinSum replaces spinor outer products with slash+mass *)
ampSqSummed = FermionSpinSum[ampSq];

(* For massive external vector bosons: no second arg *)
(* This gives the physical 3-state sum: -g^{mu nu} + p^mu p^nu / m^2 *)
ampSqSummed = DoPolarizationSums[ampSqSummed, p];
(* For massless external vectors (photon, gluon): use 0 gauge reference *)
(* ampSqSummed = DoPolarizationSums[ampSqSummed, k, 0]; *)
(* Do NOT use VirtualBoson -> True for external particles *)
```

**Pitfall:** For a massive initial-state vector boson, the polarization sum gives 3 states. For a massless vector (photon), it gives 2. Keep track of $n_{\text{init}}$ accordingly.

**See:** [spin_sums.fermion_spin_sum], [spin_sums.vector_polarization_sum]

---

## Step 4: Evaluate Traces

After applying spin sums, the expression contains Dirac traces. Use `DiracSimplify` (or `DiracTrace` followed by simplification) to evaluate all traces.

### FeynCalc Code

```mathematica
(* === Step 4: Evaluate Dirac traces === *)

ampSqTraced = DiracSimplify[ampSqSummed];

(* Alternative: if DiracSimplify does not fully evaluate, use DiracTrace explicitly *)
(* ampSqTraced = ampSqSummed /. DiracTrace -> TR // Contract; *)
```

At this stage, the result is a Lorentz scalar expressed in terms of dot products of external momenta: $p \cdot p_1$, $p \cdot p_2$, $p_1 \cdot p_2$, and the masses.

**Pitfall:** If the expression still contains free Lorentz indices after this step, something has gone wrong. Check that all polarization sums have been applied and all contractions performed. Use `Contract` to contract any remaining indices.

**See:** [feyncalc_reference.spinors_and_traces]

---

## Step 5: Apply 2-Body Kinematics

In the rest frame of the decaying particle ($p = (M, \mathbf{0})$), the kinematic invariants are fully determined by the masses alone.

### Kinematic Relations

From $p = p_1 + p_2$ and the on-shell conditions $p^2 = M^2$, $p_1^2 = m_1^2$, $p_2^2 = m_2^2$:

$$
p_1 \cdot p_2 = \frac{M^2 - m_1^2 - m_2^2}{2}
$$

$$
p \cdot p_1 = \frac{M^2 + m_1^2 - m_2^2}{2}
$$

$$
p \cdot p_2 = \frac{M^2 - m_1^2 + m_2^2}{2}
$$

### The Kallen Function and Final-State Momentum

The magnitude of the 3-momentum of either decay product in the rest frame of $A$ is:

$$
|\mathbf{p}| = \frac{\lambda^{1/2}(M^2, m_1^2, m_2^2)}{2M}
$$

where the **Kallen (triangle) function** is:

$$
\lambda(a, b, c) = a^2 + b^2 + c^2 - 2ab - 2ac - 2bc
$$

Equivalently:

$$
|\mathbf{p}| = \frac{M}{2}\sqrt{\left(1 - \frac{(m_1+m_2)^2}{M^2}\right)\left(1 - \frac{(m_1-m_2)^2}{M^2}\right)}
$$

### FeynCalc Code

```mathematica
(* === Step 5: Substitute 2-body kinematics === *)

(* On-shell conditions *)
onshell = {
  Pair[Momentum[p], Momentum[p]] -> M^2,
  Pair[Momentum[p1], Momentum[p1]] -> m1^2,
  Pair[Momentum[p2], Momentum[p2]] -> m2^2
};

(* Momentum conservation: express p.p1 and p.p2 in terms of p1.p2 *)
momcons = {
  Pair[Momentum[p], Momentum[p1]] -> (M^2 + m1^2 - m2^2)/2,
  Pair[Momentum[p], Momentum[p2]] -> (M^2 - m1^2 + m2^2)/2,
  Pair[Momentum[p1], Momentum[p2]] -> (M^2 - m1^2 - m2^2)/2
};

ampSqFinal = ampSqTraced /. onshell /. momcons // Simplify;

(* Kallen function *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;

(* Final-state momentum magnitude *)
pMag = Sqrt[Kallen[M^2, m1^2, m2^2]] / (2 M);
```

**Pitfall:** FeynCalc stores 4-momenta dot products using `Pair[Momentum[p1], Momentum[p2]]`. Make sure your replacement rules use this form, not `FourVector` or `SP`. You can also use `SP[p1, p2] -> (M^2 - m1^2 - m2^2)/2` if you first convert to `SP` notation with `FCI`.

---

## Step 6: Assemble the Decay Width

Combine the spin-summed squared amplitude with the phase-space prefactor.

### Final Formula

$$
\Gamma = \frac{|\mathbf{p}|}{8\pi M^2} \cdot \frac{1}{n_{\text{init}}} \sum_{\text{spins}} |\mathcal{M}|^2
$$

For a **scalar** decaying particle: $n_{\text{init}} = 1$.
For a **massive fermion**: $n_{\text{init}} = 2$.
For a **massive vector boson**: $n_{\text{init}} = 3$.
For a **massless vector boson**: $n_{\text{init}} = 2$.

### FeynCalc Code

```mathematica
(* === Step 6: Compute the decay width === *)

(* Number of initial spin states *)
nInit = 1; (* scalar; use 2 for fermion, 3 for massive vector *)

(* Decay width *)
decayWidth = (pMag / (8 Pi M^2)) * (1/nInit) * ampSqFinal // Simplify;

(* Print the result *)
Print["Gamma = ", decayWidth];

(* Numerical evaluation (substitute coupling values and masses) *)
decayWidthNum = decayWidth /. {
  M -> 125.0,    (* GeV, e.g. Higgs mass *)
  m1 -> 4.18,    (* GeV, e.g. b quark mass *)
  m2 -> 4.18,    (* GeV *)
  yb -> 4.18 * Sqrt[2] / 246.0  (* Yukawa coupling *)
};
Print["Gamma (numerical) = ", decayWidthNum, " GeV"];
```

**See:** [phase_space.two_body]

---

## Complete FeynCalc Workflow (Copy-Paste Template)

Below is the full workflow assembled into a single code block, using $H \to b\bar{b}$ as the concrete example.

```mathematica
(* ============================================= *)
(* Complete 1->2 Decay Width: H -> b bbar        *)
(* ============================================= *)

(* Load FeynCalc *)
<< FeynCalc`

(* Step 1: Define the amplitude *)
(* H -> b bbar via Yukawa: M = -yb/Sqrt[2] ubar(p1) v(p2) *)
amp = SpinorUBar[p1, mb] . (-I yb / Sqrt[2]) . SpinorV[p2, mb];

(* Step 2: Square the amplitude *)
ampCC = ComplexConjugate[amp];
ampSq = amp * ampCC;

(* Step 3: Fermion spin sums *)
ampSqSummed = FermionSpinSum[ampSq];

(* Step 4: Evaluate traces *)
ampSqTraced = DiracSimplify[ampSqSummed];

(* Step 5: Apply 2-body kinematics *)
kinRules = {
  Pair[Momentum[p1], Momentum[p1]] -> mb^2,
  Pair[Momentum[p2], Momentum[p2]] -> mb^2,
  Pair[Momentum[p1], Momentum[p2]] -> (mH^2 - 2 mb^2)/2
};

ampSqFinal = ampSqTraced /. kinRules // Simplify;
(* Expected result: yb^2 * (mH^2 - 4 mb^2) / 2  *)
(* With color factor Nc = 3: multiply by 3 *)
ampSqFinalColor = 3 * ampSqFinal;

(* Step 6: Assemble decay width *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;
pMag = Sqrt[Kallen[mH^2, mb^2, mb^2]] / (2 mH);
(* Simplifies to: pMag = Sqrt[mH^2 - 4 mb^2] / 2 *)

nInit = 1; (* Higgs is a scalar *)
decayWidth = (pMag / (8 Pi mH^2)) * (1/nInit) * ampSqFinalColor // Simplify;

(* Expected analytic result:
   Gamma = (3 yb^2 mH) / (32 pi) * (1 - 4 mb^2/mH^2)^(3/2)
*)

(* Numerical evaluation *)
numRules = {mH -> 125.0, mb -> 4.18, yb -> 4.18 * Sqrt[2] / 246.0};
Print["Gamma(H -> bb) = ", decayWidth /. numRules, " GeV"];
(* Expected: ~ 2.4 MeV *)
```

---

## Common Pitfalls

1. **Forgetting the color factor.** For decays to quarks, multiply $|\mathcal{M}|^2$ by $N_c = 3$. FeynCalc does not automatically include color factors for manually constructed amplitudes.

2. **Confusing spin sum vs spin average.** The formula uses the **spin-summed** (not averaged) $|\mathcal{M}|^2$ in the numerator, with $1/n_{\text{init}}$ as a separate prefactor. Do not double-count the averaging.

3. **Wrong sign in the $v$-spinor sum.** The completeness relation for $v$-spinors is $\sum_s v \bar{v} = \not{p} - m$ (minus sign), not $\not{p} + m$. FeynCalc's `FermionSpinSum` handles this automatically if spinors are entered correctly using `SpinorV` (not `SpinorU`).

4. **Applying kinematic replacements before traces.** Always evaluate traces first, then substitute kinematic relations. Substituting momenta into spinor expressions before the trace is taken will produce errors.

5. **Forgetting identical-particle factors.** If the two final-state particles are identical (e.g., $H \to \gamma\gamma$), include an extra factor of $1/2!$. See [procedures.identical_particles].

6. **Threshold condition.** The decay is kinematically allowed only if $M > m_1 + m_2$. The Kallen function becomes negative (and $|\mathbf{p}|$ imaginary) below threshold.

---

## Related Documents

- [feynman_rules.vertices_scalar] -- Yukawa and scalar interaction vertices
- [feynman_rules.vertices_vector] -- Gauge boson interaction vertices
- [spin_sums.fermion_spin_sum] -- Fermion spin sum completeness relations
- [spin_sums.vector_polarization_sum] -- Polarization sums for vector bosons
- [phase_space.two_body] -- Two-body phase space integration
- [feyncalc_reference.spinors_and_traces] -- FeynCalc spinor and trace functions
- [procedures.interference] -- Handling multiple diagrams
- [procedures.identical_particles] -- Symmetry factors for identical particles
