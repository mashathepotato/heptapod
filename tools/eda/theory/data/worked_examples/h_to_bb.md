# Worked Example: H → bb̄ (Scalar Yukawa)

This is the simplest tree-level decay: Higgs boson decaying to a bottom quark pair via scalar Yukawa coupling.

### Process
H(p) → b(p1) + b̄(p2)

### Parameters
- M_H = 125.0 GeV
- m_b = 4.18 GeV (running mass at m_H scale)
- y_b = √2 m_b / v = √2 × 4.18 / 246 ≈ 0.0240
- Color factor: N_c = 3

### Step 1: Write the amplitude
The Yukawa vertex for H-b-b̄ is: -i y_b / √2 (convention: L = -y_b/√2 H b̄ b)

Actually, let's use the simpler convention: L = -g H b̄ b, with g = m_b/v.

Vertex factor: -ig = -i m_b/v

```mathematica
(* H → b b̄, scalar Yukawa *)
amp = SpinorUBar[p1, mb] . (-I g) . SpinorV[p2, mb];
```

### Step 2: Square and spin-sum
```mathematica
ampCC = ComplexConjugate[amp];
ampSq = amp ampCC // FermionSpinSum // DiracSimplify;
```

Result: `ampSq = 4 g^2 (SP[p1,p2] - mb^2)`

Explanation: FermionSpinSum replaces u ū → /p1 + mb and v v̄ → /p2 - mb, giving:
Tr[(/p1 + mb)(-ig)(/p2 - mb)(ig)] = g^2 Tr[(/p1 + mb)(/p2 - mb)] = g^2 × 4(p1·p2 - mb²)

### Step 3: Apply kinematics
In the Higgs rest frame:
- p1·p2 = (M_H² - 2m_b²)/2

```mathematica
ampSqKin = ampSq /. {SP[p1, p2] -> (MH^2 - 2 mb^2)/2};
(* Result: 4 g^2 (MH^2/2 - mb^2 - mb^2) = 4 g^2 (MH^2/2 - 2mb^2) = 2 g^2 (MH^2 - 4mb^2) *)
```

Wait, let me be more careful:
p1·p2 = (M_H² - m_b² - m_b²)/2 = (M_H² - 2m_b²)/2

So ampSq = 4g²(p1·p2 - m_b²) = 4g²((M_H² - 2m_b²)/2 - m_b²) = 4g²(M_H² - 2m_b² - 2m_b²)/2 = 2g²(M_H² - 4m_b²)

### Step 4: Phase space and decay width
Γ = N_c × |p|/(8π M_H²) × |M|²_avg

where |M|²_avg = |M|²_summed (no initial spin averaging since scalar has 1 state).

|p| = (1/2M_H)√(M_H⁴ - 4M_H²m_b²) = (M_H/2)√(1 - 4m_b²/M_H²)

### Step 5: Complete FeynCalc script
```mathematica
<< FeynCalc`

(* === H -> b bbar, scalar Yukawa === *)
(* Amplitude *)
amp = SpinorUBar[p1, mb] . (-I g) . SpinorV[p2, mb];

(* Square and spin sum *)
ampSq = amp ComplexConjugate[amp] // FermionSpinSum // DiracSimplify;
Print["SYMBOLIC_RESULT[ampSq]: ", ampSq]

(* Kinematics: p1.p2 = (MH^2 - 2 mb^2)/2 *)
ampSqKin = ampSq /. {
  SP[p1, p2] -> (MH^2 - 2 mb^2)/2,
  SP[p1, p1] -> mb^2,
  SP[p2, p2] -> mb^2
};
ampSqKin = Simplify[ampSqKin];
Print["SYMBOLIC_RESULT[ampSq_kinematic]: ", ampSqKin]

(* Phase space *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;
pMag = Sqrt[Kallen[MH^2, mb^2, mb^2]] / (2 MH);

(* Decay width: Gamma = Nc * |p| / (8 pi MH^2) * |M|^2 *)
(* No spin averaging needed (scalar initial state) *)
(* Use integer Nc = 3, not 3.0 — floats contaminate symbolic results *)
Nc = 3;
width = Nc * pMag / (8 Pi MH^2) * ampSqKin;
width = Simplify[width];
Print["SYMBOLIC_RESULT[width_symbolic]: ", width]
Print["LATEX_RESULT[width]: ", ToString[TeXForm[width]]]

(* Numerical evaluation *)
numRules = {MH -> 125, mb -> 4.18, g -> 4.18/246};
widthNum = width /. numRules // N;
Print["NUMERICAL_RESULT[width_GeV]: ", widthNum]
Print["NUMERICAL_RESULT[width_MeV]: ", widthNum * 1000]

Print["STATUS: complete"]
```

### Expected result
Γ(H → bb̄) ≈ 2.4 MeV

This agrees with the SM prediction to within ~10% (QCD corrections increase it to ~2.6 MeV).

### Key lessons
- Scalar Yukawa is the simplest vertex: just a constant (no gamma matrices in the vertex)
- The trace is trivial: Tr[(/p1+m)(/p2-m)] = 4(p1·p2 - m²)
- Color factor N_c = 3 must be included by hand — use integer `3`, not `3.0` (float contamination)
- No initial-state spin averaging (scalar has 1 state)
- Use `ToString[TeXForm[expr]]` for LaTeX output (not bare `TeXForm`)
- For complex couplings, apply `ampCC = ampCC /. {g -> Conjugate[g]}` after `ComplexConjugate[amp]` to conjugate coupling symbols

Links: procedures.decay_width_1to2, feynman_rules.vertices_scalar, spin_sums.fermion_spin_sum, phase_space.two_body, feyncalc_reference.spinors_and_traces
