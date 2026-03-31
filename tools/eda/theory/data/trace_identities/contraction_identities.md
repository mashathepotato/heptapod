# Contraction Identities

## In D dimensions

$$\gamma^\mu \gamma_\mu = D$$

$$\gamma^\mu \gamma^\nu \gamma_\mu = -(D-2)\gamma^\nu$$

$$\gamma^\mu \gamma^\nu \gamma^\rho \gamma_\mu = 4g^{\nu\rho} - (4-D)\gamma^\nu\gamma^\rho$$

$$\gamma^\mu \gamma^\nu \gamma^\rho \gamma^\sigma \gamma_\mu = -2\gamma^\sigma\gamma^\rho\gamma^\nu + (4-D)\gamma^\nu\gamma^\rho\gamma^\sigma$$

## In 4 dimensions (D=4)

$$\gamma^\mu \gamma_\mu = 4$$

$$\gamma^\mu \gamma^\nu \gamma_\mu = -2\gamma^\nu$$

$$\gamma^\mu \gamma^\nu \gamma^\rho \gamma_\mu = 4g^{\nu\rho}$$

$$\gamma^\mu \gamma^\nu \gamma^\rho \gamma^\sigma \gamma_\mu = -2\gamma^\sigma\gamma^\rho\gamma^\nu$$

## Metric contractions

$$g^{\mu\nu}g_{\mu\nu} = D$$

$$p^\mu q_\mu = p \cdot q$$

## FeynCalc code

```mathematica
<< FeynCalc`

(* Contract Lorentz indices *)
Contract[GAD[mu] . GAD[nu] . GAD[mu]]
(* Result: -(D-2) GAD[nu] *)

(* Contract momenta *)
Contract[FVD[p, mu] FVD[q, mu]]
(* Result: SPD[p, q] *)

(* Full contraction of a trace result *)
result = DiracTrace[GAD[mu] . GSD[p] . GAD[nu] . GSD[q]] // DiracSimplify;
Contract[result MTD[mu, nu]]
(* Result: 4 D SPD[p,q] ... contracts mu,nu *)
```

## Pitfalls

- `Contract` contracts ALL matching Lorentz indices. If you want selective contraction, rename indices first.
- In D dimensions, $g^\mu{}_\mu = D$, not 4. This matters for dimensional regularization.
- Use `SPD[p,q]` (D-dimensional) not `SP[p,q]` (4-dimensional) for consistency in D-dim calculations.

## Links

- trace_identities.basic_traces
- feyncalc_reference.momentum_and_indices
