# Spinors, Traces, and Simplification in FeynCalc

## Spinor objects

| FeynCalc | Physics | Usage |
|----------|---------|-------|
| `SpinorU[p, m]` | u(p) | Incoming fermion |
| `SpinorUBar[p, m]` | u-bar(p) | Outgoing fermion |
| `SpinorV[p, m]` | v(p) | Outgoing antifermion |
| `SpinorVBar[p, m]` | v-bar(p) | Incoming antifermion |

## Building amplitudes

Amplitudes are written as chains of Dirac matrices between spinors:

```mathematica
(* General structure: SpinorUBar . (vertex) . SpinorV *)
amp = SpinorUBar[p1, m1] . (I g GAD[mu]) . SpinorV[p2, m2];
```

The dot (`.`) is Mathematica's `Dot` operator -- it preserves matrix ordering.

## ComplexConjugate

```mathematica
ampCC = ComplexConjugate[amp];
```

This reverses the Dirac chain and applies complex conjugation:
- u-bar Gamma v becomes v-bar Gamma-dagger u
- Properly handles gamma5 (hermitian) and gamma^mu (hermitian)

### Complex coupling constants

**Important:** `ComplexConjugate` only conjugates FeynCalc's own internal objects (spinors, gamma matrices, polarization vectors). It does **not** conjugate arbitrary Mathematica symbols. This means coupling constants like `g`, `yL`, `yR` are left untouched — silently assuming they are real.

For complex couplings (common in BSM physics, CP-violating phases, etc.), apply coupling conjugation as a **separate replacement rule** after `ComplexConjugate` has handled spinor chain reversal:

```mathematica
(* Step 1: ComplexConjugate handles spinor reversal *)
ampCC = ComplexConjugate[amp];
(* Step 2: Manually conjugate coupling symbols *)
ampCC = ampCC /. {gL -> Conjugate[gL], gR -> Conjugate[gR]};
ampSq = amp ampCC;
```

This produces the correct $|\mathcal{M}|^2$ with $|g_L|^2$, $|g_R|^2$, and $g_L g_R^*$ interference terms. Without the replacement rule, the result assumes all couplings are real ($g_L g_R$ instead of $g_L g_R^*$).

**Why not `Conjugate -> {...}` option?** FeynCalc's `ComplexConjugate[amp, Conjugate -> {gL, gR}]` can fail for scalar chiral vertices (SFF with `GA[7]`/`GA[6]` but no Lorentz indices) — the Dirac structures interfere with the coupling-conjugation logic. Separating spinor reversal from coupling conjugation avoids this issue and works uniformly for all vertex types.

**When to use:** Any time your amplitude contains symbolic (non-numeric) coupling constants that may be complex. If all couplings are known to be real, omit the replacement rule for simplicity.

## FermionSpinSum

```mathematica
ampSq = amp * ampCC // FermionSpinSum;
```

Replaces spinor outer products with Dirac traces:
- Sum_s u u-bar becomes slashed-p + m
- Sum_s v v-bar becomes slashed-p - m

**Important**: This SUMS over spins, does NOT average. Divide by (2s+1) for initial-state averaging.

## DiracSimplify

```mathematica
result = ampSq // DiracSimplify;
```

Evaluates Dirac traces and simplifies gamma matrix algebra. Handles:
- Trace evaluation
- Gamma matrix anticommutation
- Contraction of Lorentz indices within traces

## DiracTrace

```mathematica
(* Explicitly compute a trace *)
result = DiracTrace[GSD[p] . GSD[q]] // DiracSimplify;
(* Result: 4 SP[p, q] *)
```

## Order of operations

1. `amp * ComplexConjugate[amp]` -- form |M|^2
2. `// FermionSpinSum` -- replace spinor bilinears with traces
3. `// DiracSimplify` -- evaluate traces
4. `Contract[...]` -- contract remaining Lorentz indices (if any open indices from vector bosons)

## Chiral projectors

FeynCalc provides native chiral projectors — always prefer these over manual $(1 \pm \gamma^5)/2$:

| FeynCalc | Physics | Definition |
|----------|---------|------------|
| `GA[7]` | $P_L$ | $(1 - \gamma^5)/2$ (left-handed) |
| `GA[6]` | $P_R$ | $(1 + \gamma^5)/2$ (right-handed) |

```mathematica
(* Chiral vertex example: V -> F Fbar with independent gL, gR *)
amp = PolarizationVector[p, mu] *
      SpinorUBar[p1, m1] . (I GAD[mu] . (gL GA[7] + gR GA[6])) . SpinorV[p2, m2];
```

## Pitfalls

- Always use `SpinorUBar` (not `SpinorU`) for outgoing fermions in |M|^2 calculations
- `DiracSimplify` must be called AFTER `FermionSpinSum` -- the spin sum creates traces, then DiracSimplify evaluates them
- For amplitudes with Lorentz indices (e.g., vector boson decay), `Contract` is needed after trace evaluation
- Don't mix 4D and D-dimensional objects: use `GSD`/`GAD`/`SPD` consistently
- Use `GA[7]`/`GA[6]` for chiral projectors, never `(1 - GA[5])/2` or `GAD[5]`
- For complex couplings, apply `ampCC = ampCC /. {g -> Conjugate[g]}` after `ComplexConjugate[amp]` — bare `ComplexConjugate[amp]` silently assumes all coupling symbols are real

## Links

- feyncalc_reference.quick_start
- feyncalc_reference.momentum_and_indices
- spin_sums.fermion_spin_sum
- trace_identities.basic_traces
