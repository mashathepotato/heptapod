# Scalar and Pseudoscalar Vertices

Node ID: `feynman_rules.vertices_scalar`

## Overview

Scalar (S) and pseudoscalar (P) Yukawa interactions couple a spin-0 boson to a fermion-antifermion pair. The two cases differ by the presence of $\gamma^5$ in the vertex, leading to distinct spin structure and mass dependence in the squared amplitude.

---

## Scalar Yukawa Vertex: S-F-Fbar

**Lagrangian:**

$$\mathcal{L}_S = g_S\, \bar\psi \psi \phi$$

**Vertex factor:** $ig_S$

**FeynCalc amplitude for S(p) -> F(p1) Fbar(p2):**

```mathematica
(* Scalar Yukawa: S -> F Fbar *)
(* Vertex factor is I gS (scalar, no gamma matrix structure) *)
amp = SpinorUBar[p1, m1] . (I gS) . SpinorV[p2, m2];
```

After spin-summing and squaring:

```mathematica
(* |M|^2 after spin sum *)
ampSq = amp ComplexConjugate[amp];
ampSqSimplified = FermionSpinSum[ampSq] // DiracSimplify;
(* Result: gS^2 Tr[(p1-slash + m1)(p2-slash - m2)] *)
(* = gS^2 * 4(p1.p2 - m1 m2) *)
```

Using kinematics $p_1 \cdot p_2 = (M^2 - m_1^2 - m_2^2)/2$:

$$|\mathcal{M}|^2 = g_S^2 \left[2(M^2 - m_1^2 - m_2^2) - 4m_1 m_2\right] = 2g_S^2\left[M^2 - (m_1 + m_2)^2\right]$$

Wait -- let us be precise. The trace gives:

$$\mathrm{Tr}[(\not{p}_1 + m_1)(\not{p}_2 - m_2)] = 4(p_1 \cdot p_2 - m_1 m_2)$$

So $|\mathcal{M}|^2 = g_S^2 \cdot 4(p_1 \cdot p_2 - m_1 m_2) = 2g_S^2[M^2 - (m_1 + m_2)^2]$.

---

## Pseudoscalar Yukawa Vertex: P-F-Fbar

**Lagrangian:**

$$\mathcal{L}_P = g_P\, \bar\psi\, i\gamma^5\, \psi \phi$$

**Vertex factor:** $-g_P \gamma^5$

**FeynCalc amplitude for P(p) -> F(p1) Fbar(p2):**

```mathematica
(* Pseudoscalar Yukawa: P -> F Fbar *)
(* Vertex factor is -gP GA[5] *)
amp = SpinorUBar[p1, m1] . (-gP GA[5]) . SpinorV[p2, m2];
```

After spin-summing and squaring:

```mathematica
(* |M|^2 after spin sum *)
ampSq = amp ComplexConjugate[amp];
ampSqSimplified = FermionSpinSum[ampSq] // DiracSimplify;
(* Result: gP^2 Tr[(p1-slash + m1) GA[5] (p2-slash - m2) GA[5]] *)
(* = gP^2 * (-4)(p1.p2 + m1 m2) *)
```

Using $\gamma^5 \gamma^\mu \gamma^5 = -\gamma^\mu$ and $\gamma^5 \gamma^5 = 1$:

$$\mathrm{Tr}[(\not{p}_1 + m_1)\gamma^5(\not{p}_2 - m_2)\gamma^5] = -4(p_1 \cdot p_2 + m_1 m_2)$$

So $|\mathcal{M}|^2 = g_P^2 \cdot 4(p_1 \cdot p_2 + m_1 m_2) = 2g_P^2[M^2 - (m_1 - m_2)^2]$.

Note the sign flip: $-m_1 m_2 \to +m_1 m_2$ relative to the scalar case.

---

## Chiral Scalar Vertex: S-F-Fbar with $P_L$, $P_R$

A general scalar coupling to fermions can have independent left- and right-handed Yukawa couplings:

**Lagrangian:**

$$\mathcal{L}_{\text{chiral}} = \bar\psi (y_L P_L + y_R P_R) \psi\, \phi, \qquad P_L = \frac{1-\gamma^5}{2},\; P_R = \frac{1+\gamma^5}{2}$$

**Vertex factor:** $i(y_L P_L + y_R P_R)$

This is the most general Yukawa vertex. The pure scalar ($y_L = y_R = g_S$) and pseudoscalar ($y_L = -y_R = g_P$) are special cases.

**FeynCalc amplitude for S(p) -> F(p1) Fbar(p2):**

```mathematica
(* Chiral scalar: S -> F Fbar with independent yL, yR *)
(* GA[7] = P_L = (1 - GA[5])/2, GA[6] = P_R = (1 + GA[5])/2 *)
amp = SpinorUBar[p1, m1] . (I (yL GA[7] + yR GA[6])) . SpinorV[p2, m2];
```

**Important FeynCalc convention:**
- `GA[7]` = $P_L$ = $(1-\gamma^5)/2$ (left-handed projector)
- `GA[6]` = $P_R$ = $(1+\gamma^5)/2$ (right-handed projector)

After spin-summing and squaring:

$$|\mathcal{M}|^2 = 2\left[|y_L|^2 + |y_R|^2\right](p_1 \cdot p_2) - 2\left[|y_L|^2 - |y_R|^2\right] m_1 m_2$$

Note: for complex couplings, the squared amplitude involves $|y_L|^2$ and $|y_R|^2$ (not $y_L^2$ and $y_R^2$). In FeynCalc, apply coupling conjugation as a separate replacement rule after `ComplexConjugate` handles spinor reversal:

```mathematica
(* Step 1: ComplexConjugate handles spinor chain reversal *)
ampCC = ComplexConjugate[amp];
(* Step 2: Manually conjugate coupling symbols *)
ampCC = ampCC /. {yL -> Conjugate[yL], yR -> Conjugate[yR]};
ampSq = amp ampCC // FermionSpinSum // DiracSimplify;
```

**Warning:** Do NOT use `ComplexConjugate[amp, Conjugate -> {yL, yR}]` — this fails for scalar chiral vertices (SFF with `GA[7]`/`GA[6]` but no Lorentz indices) because the Dirac structures interfere with the coupling-conjugation logic.

**Special cases:**
- Pure scalar: $y_L = y_R = g_S$ → recovers $g_S^2 \cdot 4(p_1 \cdot p_2 - m_1 m_2)$
- Pure pseudoscalar: $y_L = -y_R = g_P$ → recovers $g_P^2 \cdot 4(p_1 \cdot p_2 + m_1 m_2)$

This vertex type is common in BSM physics (e.g., general 2HDM, MSSM neutralino/chargino couplings) where CP-violating phases make $y_L \neq y_R$.

---

## Key Physical Differences

| Property | Scalar ($\bar\psi\psi\phi$) | Pseudoscalar ($\bar\psi i\gamma^5\psi\phi$) |
|----------|---------------------------|---------------------------------------------|
| $\|\mathcal{M}\|^2$ | $\propto M^2 - (m_1+m_2)^2$ | $\propto M^2 - (m_1-m_2)^2$ |
| Threshold | Vanishes at $M = m_1 + m_2$ | Vanishes at $M = \|m_1 - m_2\|$ |
| Equal masses | Both give $\propto (M^2 - 4m^2)$ | Same |
| Massless fermions | Both give $\propto M^2$ | Same (chiral symmetry) |
| Partial wave | S-wave (L=0) | S-wave (L=0) |
| Parity of boson | $J^P = 0^+$ | $J^P = 0^-$ |

When both fermion masses are equal ($m_1 = m_2 = m_f$), the two cases become identical up to a sign that cancels in $|\mathcal{M}|^2$ after trace evaluation. The distinction matters physically when $m_1 \neq m_2$.

---

## Standard Model Higgs Yukawa

The SM Higgs is a scalar with Yukawa coupling proportional to fermion mass:

$$g_S = \frac{m_f}{v}, \quad v = 246\;\text{GeV}$$

```mathematica
(* SM Higgs to fermion pair: H -> f fbar *)
(* yf = mf / v is the Yukawa coupling *)
yf = mf / v;
amp = SpinorUBar[p1, mf] . (I yf) . SpinorV[p2, mf];

(* After spin sum and trace *)
ampSq = FermionSpinSum[amp ComplexConjugate[amp]] // DiracSimplify;
(* = yf^2 * 4(p1.p2 - mf^2) = 2 yf^2 (mH^2 - 4 mf^2) *)
```

For H -> bb with $m_b \approx 4.18$ GeV, $m_H \approx 125$ GeV:
- $y_b = m_b/v \approx 0.017$
- Include color factor $N_c = 3$

---

## Complete FeynCalc Workflow Example

```mathematica
(* Full calculation: S(M) -> F(m1) Fbar(m2), scalar Yukawa *)
<<FeynCalc`;

(* 1. Write amplitude *)
amp = SpinorUBar[p1, m1] . (I gS) . SpinorV[p2, m2];

(* 2. Square and spin-sum *)
ampSq = amp ComplexConjugate[amp];
ampSqSummed = FermionSpinSum[ampSq] // DiracSimplify;

(* 3. Apply kinematics: p = p1 + p2, p^2 = M^2 *)
kinRules = {
  ScalarProduct[p1, p1] -> m1^2,
  ScalarProduct[p2, p2] -> m2^2,
  ScalarProduct[p1, p2] -> (M^2 - m1^2 - m2^2)/2
};
result = ampSqSummed /. kinRules;
(* Expected: 2 gS^2 (M^2 - (m1 + m2)^2) *)
```

---

## Pitfalls

1. **The factor of $i$ in the vertex.** Whether the vertex is $ig$ or $g$ depends on convention. The Lagrangian $\mathcal{L} = g\bar\psi\psi\phi$ gives a vertex factor $ig$ from the Feynman rule $i\mathcal{L}_{\text{int}}$. Always include the $i$ explicitly.

2. **Spinor assignments for external fermions:**
   - Outgoing fermion (particle): `SpinorUBar[p, m]` (= $\bar{u}$)
   - Outgoing antifermion: `SpinorV[p, m]` (= $v$)
   - Incoming fermion (particle): `SpinorU[p, m]` (= $u$)
   - Incoming antifermion: `SpinorVBar[p, m]` (= $\bar{v}$)
   - For a decay A -> B C, particle B gets `SpinorUBar`, antiparticle C gets `SpinorV`.

3. **Dot product ordering matters.** The amplitude is read against the fermion line: start from the barred spinor, go through vertices, end at the unbarred spinor. The FeynCalc `.` (Dot) operator respects non-commutativity of Dirac matrices.

4. **ComplexConjugate reverses the chain.** FeynCalc's `ComplexConjugate` automatically reverses the spinor chain and applies $(\gamma^\mu)^\dagger = \gamma^0 \gamma^\mu \gamma^0$, producing the correct $|\mathcal{M}|^2$.

5. **FermionSpinSum replaces spinor bilinears with traces.** It performs $\sum_s u\bar{u} \to \not{p}+m$ and $\sum_s v\bar{v} \to \not{p}-m$. The result is a Dirac trace that `DiracSimplify` evaluates.

---

## Links

- `procedures.decay_width_1to2` -- How to go from |M|^2 to a decay width
- `spin_sums.fermion_spin_sum` -- Fermion spin sum rules and FeynCalc implementation
- `feynman_rules.vertices_vector` -- Vector and axial-vector vertices for comparison
- `feyncalc_reference.spinors_and_traces` -- Spinor conventions and trace evaluation
- `worked_examples.h_to_bb` -- Complete worked example of H -> bb using these rules
