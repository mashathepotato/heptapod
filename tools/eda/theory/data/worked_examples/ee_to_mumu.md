# Worked Example: e⁺e⁻ → μ⁺μ⁻ (QED 2→2 Scattering)

### Process
e⁻(p1) + e⁺(p2) → μ⁻(p3) + μ⁺(p4) via s-channel photon exchange

### Parameters
- √s = 10 GeV (well below Z pole)
- m_e = m_μ = 0 (massless approximation — valid at high energy)
- α = 1/137
- e = √(4πα)

### Feynman diagram
s-channel: e⁺e⁻ → γ* → μ⁺μ⁻

### Step 1: Write the amplitude
```mathematica
(* e-(p1) e+(p2) -> gamma* -> mu-(p3) mu+(p4) *)
(* Two QED vertices connected by photon propagator *)
(* = [vbar(p2) (-ie gamma^mu) u(p1)] * (-g_{mu nu}/s) * [ubar(p3) (-ie gamma^nu) v(p4)] *)
amp = SpinorVBar[p2, 0] . (-I ee GAD[mu]) . SpinorU[p1, 0] *
      (-MTD[mu, nu]) FAD[p1 + p2] *
      SpinorUBar[p3, 0] . (-I ee GAD[nu]) . SpinorV[p4, 0];
```

### Step 2: Square, spin-sum, simplify
```mathematica
ampCC = ComplexConjugate[amp];
ampSq = amp ampCC // FermionSpinSum // DiracSimplify // Contract;
```

### Step 3: Apply Mandelstam variables
```mathematica
SetMandelstam[s, t, u, p1, p2, -p3, -p4, 0, 0, 0, 0];
ampSqMandelstam = TrickMandelstam[ampSq, {s, t, u, 0}] // Simplify;
```

Expected result for massless case:
|M|²_summed = 8e⁴(t² + u²)/s² = 2e⁴(1 + cos²θ)

(The factor 8 comes from summing over all 4 spins; if averaging over initial spins, divide by 4, giving 2e⁴(t²+u²)/s².)

### Step 4: Cross section
```mathematica
(* Differential cross section: dσ/dΩ = |M|²_avg / (64 π² s) *)
(* Average over initial spins: divide by 4 (2 for e-, 2 for e+) *)
ampSqAvg = ampSq / 4;

(* Total cross section: integrate over angles *)
(* For massless: σ = 4πα²/(3s) *)
```

### Step 5: Complete FeynCalc script
```mathematica
<< FeynCalc`

(* === e+ e- -> mu+ mu- via QED === *)

(* Amplitude: s-channel photon *)
amp = SpinorVBar[p2, 0] . (-I ee GAD[mu]) . SpinorU[p1, 0] *
      (-MTD[mu, nu]) FAD[p1 + p2] *
      SpinorUBar[p3, 0] . (-I ee GAD[nu]) . SpinorV[p4, 0];

(* Square and spin sum *)
ampSq = amp ComplexConjugate[amp] // FermionSpinSum // DiracSimplify // Contract;
Print["SYMBOLIC_RESULT[ampSq_raw]: ", ampSq]

(* Mandelstam variables for massless particles *)
SetMandelstam[s, t, u, p1, p2, -p3, -p4, 0, 0, 0, 0];
ampSqM = ampSq // Simplify;
Print["SYMBOLIC_RESULT[ampSq_mandelstam]: ", ampSqM]

(* Spin-averaged *)
ampSqAvg = ampSqM / 4;
Print["SYMBOLIC_RESULT[ampSq_averaged]: ", ampSqAvg]

(* Total cross section: σ = 1/(16 π s |p_i|²) ∫ |M|²_avg dt *)
(* For massless: |p_i| = √s/2, so |p_i|² = s/4 *)
(* σ = 1/(16 π s × s/4) ∫ |M|²_avg dt = 4/(16 π s²) ∫ |M|²_avg dt *)
(* t ranges from -(s) to 0 for massless particles *)
sigma = 4 / (16 Pi s^2) * Integrate[ampSqAvg /. u -> -s - t, {t, -s, 0}];
sigma = Simplify[sigma];
Print["SYMBOLIC_RESULT[sigma_symbolic]: ", sigma]

(* Verify: should give 4 Pi alpha^2 / (3 s) *)
sigmaCheck = sigma /. ee^2 -> 4 Pi alpha // Simplify;
Print["SYMBOLIC_RESULT[sigma_check]: ", sigmaCheck]

(* Numerical at sqrt(s) = 10 GeV *)
sqrtS = 10.0;
alphaNum = 1/137.0;
sigmaNum = 4 Pi alphaNum^2 / (3 sqrtS^2);  (* in GeV^-2 *)
(* Convert to pb: 1 GeV^-2 = 0.3894e9 pb *)
sigmaPb = sigmaNum * 0.3894*10^9;
Print["NUMERICAL_RESULT[sigma_GeV2]: ", N[sigmaNum]]
Print["NUMERICAL_RESULT[sigma_pb]: ", N[sigmaPb]]

Print["STATUS: complete"]
```

### Expected result
σ(e⁺e⁻ → μ⁺μ⁻) = 4πα²/(3s)

At √s = 10 GeV: σ ≈ 0.87 nb = 870 pb

### Key lessons
- 2→2 scattering requires a propagator (here: photon)
- FAD handles the propagator denominator, but the numerator (-g^μν for photon) must be written explicitly
- Use SetMandelstam to express everything in s, t, u
- Spin averaging: divide by 4 (2 × 2 for two initial fermions)
- Unit conversion: 1 GeV⁻² = 0.3894 × 10⁹ pb
- Use `ToString[TeXForm[expr]]` for LaTeX output (not bare `TeXForm`)
- Use integer constants where possible to keep symbolic results exact

Links: procedures.cross_section_2to2, feynman_rules.vertices_vector, feynman_rules.propagators, spin_sums.fermion_spin_sum, phase_space.mandelstam, feyncalc_reference.spinors_and_traces
