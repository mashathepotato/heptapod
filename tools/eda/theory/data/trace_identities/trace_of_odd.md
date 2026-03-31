# Trace of Odd Number of Gamma Matrices

## Identity

$$\text{Tr}[\gamma^{\mu_1} \gamma^{\mu_2} \cdots \gamma^{\mu_{2n+1}}] = 0$$

The trace of any odd number of gamma matrices vanishes. This includes:

- $\text{Tr}[\gamma^\mu] = 0$
- $\text{Tr}[\gamma^\mu \gamma^\nu \gamma^\rho] = 0$
- $\text{Tr}[\not{p}] = 0$
- $\text{Tr}[\not{p}\not{q}\not{r}] = 0$

## With gamma-5

Adding a gamma-5 effectively adds 4 more gamma matrices ($\gamma^5 = i\gamma^0\gamma^1\gamma^2\gamma^3$), so the total count determines the result:

- $\text{Tr}[\gamma^\mu \gamma^5]$ = Tr[5 gammas] = 0
- $\text{Tr}[\gamma^\mu \gamma^\nu \gamma^5]$ = Tr[6 gammas] = 0 (by the specific gamma-5 trace identity, not the odd rule)
- $\text{Tr}[\gamma^\mu \gamma^\nu \gamma^\rho \gamma^5]$ = Tr[7 gammas] = 0

## FeynCalc code

```mathematica
<< FeynCalc`

DiracTrace[GSD[p]] // DiracSimplify
(* Result: 0 *)

DiracTrace[GSD[p] . GSD[q] . GSD[r]] // DiracSimplify
(* Result: 0 *)
```

## Why this matters

When expanding spin-summed $|\mathcal{M}|^2$, terms with odd powers of $m$ (from $(\not{p}+m)$ factors) produce traces of odd numbers of gamma matrices, which vanish. This simplifies calculations significantly.

## Links

- trace_identities.basic_traces
