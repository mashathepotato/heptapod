# Vector Boson Polarization Sums

## Massive vector (W, Z)

For a massive spin-1 boson with momentum $p$ and mass $m$, summing over all three polarization states gives:

$$\sum_\lambda \epsilon^\mu(\lambda) \epsilon^{*\nu}(\lambda) = -g^{\mu\nu} + \frac{p^\mu p^\nu}{m^2}$$

The three polarization states correspond to two transverse modes and one longitudinal mode. The longitudinal polarization vector grows as $E/m$ at high energies, which is the origin of the $p^\mu p^\nu / m^2$ term.

## Massless vector (photon, gluon)

For a massless spin-1 boson in Feynman gauge, or equivalently for any gauge-invariant amplitude:

$$\sum_\lambda \epsilon^\mu(\lambda) \epsilon^{*\nu}(\lambda) = -g^{\mu\nu}$$

This replacement is valid whenever the amplitude satisfies the Ward identity $p_\mu \mathcal{M}^\mu = 0$. In that case, the gauge-dependent terms proportional to $p^\mu$ or $p^\nu$ drop out and the simple $-g^{\mu\nu}$ replacement is exact.

## FeynCalc implementation

### Using DoPolarizationSums (recommended)

For massless vectors (photon, gluon):
```mathematica
(* k = photon momentum, 0 = covariant gauge reference vector *)
ampSq = DoPolarizationSums[ampSq, k, 0];
```

For massive vectors (W, Z):
```mathematica
(* k = boson momentum — no second argument for massive vectors *)
ampSq = DoPolarizationSums[ampSq, k];
```

**Important:** Do NOT use `DoPolarizationSums[ampSq, k, 0]` for massive vectors. The `0` is a covariant gauge reference vector appropriate only for massless bosons. For massive external vectors, calling with just the momentum gives the correct physical 3-state sum $-g^{\mu\nu} + p^\mu p^\nu / m^2$.

**Do NOT use `VirtualBoson -> True` for external particles.** `VirtualBoson -> True` forces $-g^{\mu\nu}$ (the 4-state sum), which is only correct for off-shell internal propagators, not physical on-shell particles.

### Manual replacement

For a massive vector in the initial state (e.g., $Z \to f\bar{f}$), after writing the amplitude with explicit Lorentz index $\mu$:

```mathematica
(* Polarization sum for massive vector boson *)
(* Replace epsilon^mu epsilon^*nu -> -g^{mu nu} + p^mu p^nu / M^2 *)
ampSq = ampSq /. {
  Pair[Momentum[Polarization[k, I], D], LorentzIndex[mu_, D]] *
  Pair[Momentum[Polarization[k, -I], D], LorentzIndex[nu_, D]] ->
    -MTD[mu, nu] + FVD[k, mu] FVD[k, nu] / MV^2
};
```

For massless vectors, the manual replacement is simpler:

```mathematica
ampSq = ampSq /. {
  Pair[Momentum[Polarization[k, I], D], LorentzIndex[mu_, D]] *
  Pair[Momentum[Polarization[k, -I], D], LorentzIndex[nu_, D]] ->
    -MTD[mu, nu]
};
```

### Handling multiple vector bosons

When the amplitude involves several vector bosons, apply `DoPolarizationSums` sequentially for each one:

```mathematica
(* Example: two massless photons in the final state *)
ampSq = DoPolarizationSums[ampSq, k1, 0];
ampSq = DoPolarizationSums[ampSq, k2, 0];

(* Example: two massive vectors (e.g., H -> W+ W-) *)
ampSq = DoPolarizationSums[ampSq, k1];
ampSq = DoPolarizationSums[ampSq, k2];
```

## Averaging

| Boson type | Polarization states | Averaging factor |
|------------|-------------------|-----------------|
| Massive vector (W, Z) | 3 | 1/3 |
| Massless vector (photon) | 2 | 1/2 |
| Massless vector (gluon) | 2 | 1/2 |

Remember that for gluons you must also average over color (divide by 8 for each initial-state gluon).

## Pitfalls

1. **The $p^\mu p^\nu / m^2$ term must be kept for massive vectors.** While this term often vanishes due to current conservation ($p_\mu J^\mu = 0$), this is not guaranteed in all processes. In particular, for W/Z decays and scattering processes involving non-conserved currents, dropping this term gives wrong results.

2. **DoPolarizationSums is the cleanest approach.** Manual replacements are error-prone, especially in $D$ dimensions where momentum and index conventions must match exactly. Prefer `DoPolarizationSums` unless you have a specific reason to do the replacement by hand.

3. **Averaging factors are not automatic.** Neither `FermionSpinSum` nor `DoPolarizationSums` includes the $1/(2s+1)$ averaging factor. You must divide by 3 for each initial-state massive vector and by 2 for each initial-state massless vector.

4. **Gauge dependence for massless vectors.** The replacement $\sum_\lambda \epsilon^\mu \epsilon^{*\nu} = -g^{\mu\nu}$ is strictly valid only for gauge-invariant subsets of diagrams. If you are computing individual diagrams (not the full gauge-invariant set), you may need to use a physical polarization sum with an auxiliary vector $n^\mu$:
$$\sum_\lambda \epsilon^\mu \epsilon^{*\nu} = -g^{\mu\nu} + \frac{p^\mu n^\nu + n^\mu p^\nu}{p \cdot n}$$

5. **Ghost contributions for gluons.** In non-abelian gauge theories (QCD), using $-g^{\mu\nu}$ for the gluon polarization sum in covariant gauges requires adding Faddeev-Popov ghost contributions to cancel unphysical polarization states. In axial or light-cone gauges, ghosts decouple but the polarization sum is more complicated.

## Links

- spin_sums.massive_vs_massless
- spin_sums.fermion_spin_sum
- feyncalc_reference.momentum_and_indices
