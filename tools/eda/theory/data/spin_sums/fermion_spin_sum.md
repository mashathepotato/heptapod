# Fermion Spin Sums

## Dirac fermion spin sums

For unpolarized calculations, sum over final-state spins and average over initial-state spins.

**Particle (fermion):**
$$\sum_s u(p,s)\bar{u}(p,s) = \not{p} + m$$

**Antiparticle (antifermion):**
$$\sum_s v(p,s)\bar{v}(p,s) = \not{p} - m$$

These completeness relations convert spinor bilinears into Dirac traces, which can then be evaluated using standard trace identities.

## FeynCalc implementation

FeynCalc's `FermionSpinSum` automatically applies these replacements:

```mathematica
<< FeynCalc`
(* Define amplitude *)
amp = SpinorUBar[p1, m1] . (Gamma) . SpinorV[p2, m2];
ampCC = ComplexConjugate[amp];

(* Square and spin-sum *)
ampSq = amp ampCC // FermionSpinSum;

(* Now evaluate the trace *)
ampSq = ampSq // DiracSimplify;
```

## What FermionSpinSum does internally

It replaces spinor bilinears with traces:

- `SpinorUBar[p,m] . G . SpinorU[p,m]` is replaced by `DiracTrace[(GSD[p] + m) . G]` (summed, not averaged)
- `SpinorVBar[p,m] . G . SpinorV[p,m]` is replaced by `DiracTrace[(GSD[p] - m) . G]`
- Mixed bilinears such as `SpinorUBar[p,m] . G . SpinorV[p,m]` are handled analogously with the appropriate sign on the mass term

The key point is that `FermionSpinSum` produces unevaluated `DiracTrace` objects. You must call `DiracSimplify` or `DiracTrace` afterwards to compute the actual trace.

## Averaging

For a spin-1/2 particle in the initial state, divide by 2 (two spin states).
For a massive vector in the initial state, divide by 3 (three polarizations).
For a massless vector, divide by 2.

**This averaging factor is NOT included by FermionSpinSum -- you must add it manually.**

A typical unpolarized cross section for a 2-to-2 fermion process therefore carries a prefactor of $\frac{1}{4}$ (averaging over both initial spins):

```mathematica
(* For e+ e- -> mu+ mu- *)
ampSqAvg = 1/4 * ampSq;
```

## Pitfalls

1. **FermionSpinSum sums but does NOT average.** You must multiply by $1/(2s+1)$ for each initial-state particle yourself. Forgetting this is one of the most common errors in textbook calculations.

2. **The sign difference matters.** The relative sign between the particle sum ($\not{p} + m$) and the antiparticle sum ($\not{p} - m$) is physical. Swapping $u$ and $v$ spinors without tracking this sign leads to wrong interference terms.

3. **Always call DiracSimplify after FermionSpinSum.** The output of `FermionSpinSum` contains unevaluated `DiracTrace` objects. Without simplification, subsequent algebraic manipulations will not work correctly.

4. **Majorana fermions.** For Majorana fermions, charge conjugation symmetry means that both the $u$-type and $v$-type spin sums give $\not{p} + m$. FeynCalc handles this correctly if you use the Majorana spinor conventions, but be careful when writing amplitudes by hand.

5. **Dimensional regularization.** In $D$ dimensions, the spin sum relations remain the same, but the trace algebra changes (e.g., $\text{tr}[\mathbb{1}] = 4$ is replaced by a $D$-dependent value in some schemes). Use `DiracSimplify` with the appropriate FeynCalc options for $D$-dimensional calculations.

## Links

- trace_identities.basic_traces
- trace_identities.gamma5_traces
- spin_sums.massive_vs_massless
- feyncalc_reference.spinors_and_traces
