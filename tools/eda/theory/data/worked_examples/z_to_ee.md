# Worked Example: Z → e⁺e⁻ (Vector-Axial Coupling)

### Process
Z(p, ε) → e⁻(p1) + e⁺(p2)

### Parameters
- M_Z = 91.1876 GeV
- m_e ≈ 0 (massless approximation)
- sin²θ_W = 0.2312
- α_em = 1/128
- g_Z = e/(sinθ_W cosθ_W)
- For the electron: T3 = -1/2, Q = -1
  - g_V = T3/2 - Q sin²θ_W = -1/4 + sin²θ_W ≈ -0.0188
  - g_A = T3/2 = -1/4 = -0.25
  - Vertex: i g_Z γ^μ (g_V - g_A γ⁵)

### Step 1: Write the amplitude
```mathematica
(* Z(p, eps^mu) -> e-(p1) e+(p2) *)
(* Vertex: i gZ gamma^mu (gV - gA gamma5) *)
amp = Pair[Momentum[Polarization[p, I], D], LorentzIndex[mu, D]] *
      SpinorUBar[p1, 0] . (I gZ GAD[mu] . (gV - gA GA[5])) . SpinorV[p2, 0];
```

### Step 2: Square, spin-sum, polarization sum
```mathematica
ampCC = ComplexConjugate[amp];
ampSq = amp ampCC // FermionSpinSum // DiracSimplify;

(* Polarization sum for massive Z: -g^{mu nu} + p^mu p^nu / MZ^2 *)
(* No second arg for massive vectors — the 0 gauge reference is for massless only *)
ampSq = DoPolarizationSums[ampSq, p] // Contract // Simplify;

(* Average over initial Z polarizations: divide by 3 *)
ampSqAvg = ampSq / 3;
```

### Step 3: Apply kinematics (massless electrons)
With m_e = 0:
- p1·p2 = M_Z²/2
- p·p1 = M_Z²/2
- p·p2 = M_Z²/2

### Step 4: Complete FeynCalc script
```mathematica
<< FeynCalc`

(* === Z -> e+ e-, V-A coupling === *)

(* Amplitude with polarization vector *)
amp = Pair[Momentum[Polarization[p, I], D], LorentzIndex[mu, D]] *
      SpinorUBar[p1, me] . (I gZ GAD[mu] . (gV - gA GA[5])) . SpinorV[p2, me];

(* Square and spin sum *)
ampSq = amp ComplexConjugate[amp] // FermionSpinSum // DiracSimplify;
Print["SYMBOLIC_RESULT[ampSq_before_polsum]: ", Short[ampSq, 3]]

(* Polarization sum for massive vector — no second arg *)
ampSq = DoPolarizationSums[ampSq, p] // Contract // Simplify;
Print["SYMBOLIC_RESULT[ampSq_after_polsum]: ", ampSq]

(* Kinematics *)
kinRules = {
  SP[p1, p2] -> (MZ^2 - 2 me^2)/2,
  SP[p, p1] -> (MZ^2 + me^2 - me^2)/2,
  SP[p, p2] -> (MZ^2 + me^2 - me^2)/2,
  SP[p, p] -> MZ^2,
  SP[p1, p1] -> me^2,
  SP[p2, p2] -> me^2
};
ampSqKin = ampSq /. kinRules // Simplify;
Print["SYMBOLIC_RESULT[ampSq_kinematic]: ", ampSqKin]

(* Decay width *)
Kallen[a_, b_, c_] := a^2 + b^2 + c^2 - 2 a b - 2 a c - 2 b c;
pMag = Sqrt[Kallen[MZ^2, me^2, me^2]] / (2 MZ);

(* Average over 3 Z polarizations *)
width = pMag / (8 Pi MZ^2) * ampSqKin / 3;
width = Simplify[width];
Print["SYMBOLIC_RESULT[width_symbolic]: ", width]
Print["LATEX_RESULT[width]: ", ToString[TeXForm[width]]]

(* Numerical values *)
sw2 = 0.2312;
cw2 = 1 - sw2;
alpha = 1/128.0;
ee = Sqrt[4 Pi alpha];
gZnum = ee / (Sqrt[sw2] Sqrt[cw2]);
gVnum = -1/4 + sw2;
gAnum = -1/4;

numRules = {MZ -> 91.1876, me -> 0.000511, gZ -> gZnum, gV -> gVnum, gA -> gAnum};
widthNum = width /. numRules // N;
Print["NUMERICAL_RESULT[width_GeV]: ", widthNum]
Print["NUMERICAL_RESULT[width_MeV]: ", widthNum * 1000]

Print["STATUS: complete"]
```

### Expected result
Γ(Z → e⁺e⁻) ≈ 84 MeV

The SM prediction is 83.91 MeV. This is one leptonic partial width; the total Z width is ~2.495 GeV.

### Key lessons
- V-A coupling introduces γ⁵ — traces split into V² + A² terms (cross terms vanish after polarization sum)
- Must handle polarization vectors: DoPolarizationSums is the cleanest approach
- Average over 3 Z polarizations (massive vector)
- Result is proportional to MZ(gV² + gA²)

Links: procedures.decay_width_1to2, feynman_rules.vertices_vector, spin_sums.fermion_spin_sum, spin_sums.vector_polarization_sum, phase_space.two_body, feyncalc_reference.spinors_and_traces
