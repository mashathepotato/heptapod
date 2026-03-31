# Massive vs Massless Spin Sums

## Quick reference

| Particle | Spin | States | Spin/Polarization Sum | Average factor |
|----------|------|--------|----------------------|----------------|
| Massive fermion | 1/2 | 2 | $\not{p} + m$ | 1/2 |
| Massless fermion | 1/2 | 2 | $\not{p}$ | 1/2 |
| Massive vector | 1 | 3 | $-g^{\mu\nu} + p^\mu p^\nu / m^2$ | 1/3 |
| Massless vector | 1 | 2 | $-g^{\mu\nu}$ | 1/2 |
| Scalar | 0 | 1 | 1 | 1 |

The "States" column counts the number of physical polarization/spin degrees of freedom. The "Average factor" is $1/(2s+1)$ for massive particles, except for massless vectors where only 2 transverse polarizations are physical.

## Massless limit

### Fermions: smooth limit

Setting $m = 0$ in the fermion spin sum gives:

$$\sum_s u(p,s)\bar{u}(p,s) = \not{p} + m \xrightarrow{m \to 0} \not{p}$$

This is a smooth, well-behaved limit. The number of spin states remains 2 in both cases (spin up and spin down for massive; left-helicity and right-helicity for massless). No subtlety arises.

### Vectors: discontinuous limit

The massive vector polarization sum has a fundamentally different structure from the massless one:

$$-g^{\mu\nu} + \frac{p^\mu p^\nu}{m^2} \quad \xrightarrow{m \to 0} \quad \text{diverges!}$$

The $p^\mu p^\nu / m^2$ term blows up as $m \to 0$. This is not a mathematical artifact -- it reflects the physical fact that a massive vector boson has 3 polarization states while a massless one has only 2. The longitudinal polarization does not smoothly decouple; it becomes the Goldstone boson degree of freedom (the Goldstone boson equivalence theorem).

**Consequence:** You cannot obtain the massless polarization sum by taking $m \to 0$ in the massive formula. Always use the correct formula for the particle you are dealing with.

## FeynCalc notes

### Massless fermions

For massless fermions, use zero mass in the spinor constructors:

```mathematica
(* Massless fermion spinors *)
amp = SpinorUBar[p, 0] . GA[mu] . SpinorU[k, 0];
ampCC = ComplexConjugate[amp];
ampSq = amp ampCC // FermionSpinSum // DiracSimplify;
```

### Massless vectors

For massless vectors (photons, gluons), use `DoPolarizationSums` with auxiliary vector 0:

```mathematica
(* Massless vector polarization sum *)
ampSq = DoPolarizationSums[ampSq, k, 0];
```

### Massive vectors

For massive external vectors (W, Z), call `DoPolarizationSums` with just the momentum — no second argument:

```mathematica
(* Massive vector polarization sum: -g^{mu nu} + k^mu k^nu / m^2 *)
ampSq = DoPolarizationSums[ampSq, k];
```

**Important:** Do NOT use `DoPolarizationSums[ampSq, k, 0]` for massive vectors — the `0` is a covariant gauge reference vector only appropriate for massless bosons. Do NOT use `VirtualBoson -> True` for external particles — it forces $-g^{\mu\nu}$ (the unphysical 4-state sum) which is only correct for off-shell internal propagators.

### Scalars

Scalars have no spin structure, so no spin sum is needed. The squared amplitude is simply $|\mathcal{M}|^2$ with no additional factors.

## Combined example: unpolarized cross section prefactors

For a process $A B \to C D$, the unpolarized squared amplitude is:

$$\overline{|\mathcal{M}|^2} = \frac{1}{(2s_A + 1)(2s_B + 1)} \sum_{\text{all spins/pols}} |\mathcal{M}|^2$$

Common cases:

| Process type | Averaging prefactor |
|---|---|
| $e^+e^- \to \mu^+\mu^-$ | $\frac{1}{2} \cdot \frac{1}{2} = \frac{1}{4}$ |
| $\gamma\gamma \to e^+e^-$ | $\frac{1}{2} \cdot \frac{1}{2} = \frac{1}{4}$ |
| $gg \to q\bar{q}$ | $\frac{1}{2} \cdot \frac{1}{2} \cdot \frac{1}{8} \cdot \frac{1}{8} = \frac{1}{256}$ (includes color) |
| $Z \to f\bar{f}$ | $\frac{1}{3}$ |
| $H \to f\bar{f}$ | $1$ |
| $W^+ \to \ell^+ \nu$ | $\frac{1}{3}$ |

## Pitfalls

1. **Never take $m \to 0$ in the massive vector polarization sum.** The limit is singular. Use the massless formula $-g^{\mu\nu}$ directly for photons and gluons.

2. **Counting degrees of freedom.** A massive vector has 3 polarization states (two transverse + one longitudinal). A massless vector has only 2 (both transverse). This mismatch is why the Higgs mechanism is needed: the "eaten" Goldstone boson provides the longitudinal degree of freedom.

3. **Color averaging for QCD.** For gluon initial states, you must average over color as well as polarization. Each gluon carries a factor of $1/8$ for color averaging on top of the $1/2$ for polarization averaging.

4. **Helicity-specific calculations.** If you want a specific helicity configuration rather than an unpolarized sum, do not use `FermionSpinSum` or `DoPolarizationSums`. Instead, use explicit helicity spinors or polarization vectors. FeynCalc supports this through `SpinorU[p, m, 1]` (spin up) and related constructs, or through the `FeynCalcFormLink` interface for numerical evaluation.

## Links

- spin_sums.fermion_spin_sum
- spin_sums.vector_polarization_sum
