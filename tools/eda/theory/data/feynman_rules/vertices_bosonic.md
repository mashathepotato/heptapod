# Bosonic Vertices

Node ID: `feynman_rules.vertices_bosonic`

## Overview

Purely bosonic vertices involve only scalar and/or vector fields with no fermion lines. These include self-interactions of scalar fields, gauge boson self-couplings (triple and quartic), and scalar-gauge couplings arising from covariant derivatives or the Higgs mechanism. Momentum flow conventions are critical: all momenta are defined as incoming unless stated otherwise.

---

## Triple Scalar Vertex: S-S-S

**Lagrangian:**

$$\mathcal{L} = \frac{\lambda_3}{3!}\, \phi^3$$

**Vertex factor:** $i\lambda_3$

The $3! = 6$ in the Lagrangian compensates the 3! ways to contract three identical fields, so the vertex factor is simply $i\lambda_3$.

```mathematica
(* Triple scalar vertex *)
(* All momenta incoming: p1 + p2 + p3 = 0 *)
vertexSSS = I lambda3;
```

For a cubic interaction involving distinct scalars $\lambda_{abc}\phi_a\phi_b\phi_c$, there is no symmetry factor and the vertex is just $i\lambda_{abc}$.

---

## Quartic Scalar Vertex: S-S-S-S

**Lagrangian:**

$$\mathcal{L} = \frac{\lambda_4}{4!}\, \phi^4$$

**Vertex factor:** $i\lambda_4$

```mathematica
(* Quartic scalar vertex *)
vertexSSSS = I lambda4;
```

For the SM Higgs potential $V = \lambda(|\Phi|^2 - v^2/2)^2$, the physical Higgs quartic vertex is $-6i\lambda = -3i m_H^2/v^2$.

---

## Scalar-Scalar-Vector Vertex: S-S-V

Arises from the covariant derivative $|D_\mu\phi|^2$ with $D_\mu = \partial_\mu - igV_\mu$.

**Vertex factor (all momenta incoming):**

$$ig(p_1 - p_2)^\mu$$

where $p_1$ and $p_2$ are the momenta of the two scalars (particle vs antiparticle), and $\mu$ is the Lorentz index of the vector boson.

```mathematica
(* S-S-V vertex: scalar(p1) + scalar-bar(p2) + V(mu) *)
(* All momenta incoming: p1 + p2 + q = 0 *)
vertexSSV = I g FVD[p1 - p2, mu];
```

**Momentum convention is critical:** The sign of $p_1 - p_2$ depends on which scalar is the particle and which is the antiparticle. For a complex scalar $\phi$:
- $\phi$ carries charge $+Q$: momentum $p_1$
- $\phi^*$ carries charge $-Q$: momentum $p_2$
- The vertex is $iQ e(p_1 - p_2)^\mu$

```mathematica
(* Example: charged pion electromagnetic vertex *)
(* pi+(p1) + pi-(p2) + gamma(mu, q), all incoming *)
vertexPiPiGamma = I e FVD[p1 - p2, mu];
```

---

## Scalar-Vector-Vector Vertex: S-V-V

Arises from the Higgs mechanism: when a scalar acquires a VEV, the $|D_\mu\phi|^2$ term generates a mass term $m_V^2 V_\mu V^\mu$ and a coupling of the physical scalar to two gauge bosons.

**SM Higgs-W-W vertex:**

$$ig\, m_W\, g^{\mu\nu}$$

**SM Higgs-Z-Z vertex:**

$$i\frac{g}{\cos\theta_W}\, m_Z\, g^{\mu\nu}$$

```mathematica
(* Higgs-W-W vertex *)
vertexHWW = I g mW MTD[mu, nu];

(* Higgs-Z-Z vertex *)
vertexHZZ = I (g / cosThW) mZ MTD[mu, nu];
```

More generally, for any S-V-V coupling $\mathcal{L} = g_{SVV}\, \phi\, V_\mu V^\mu$:

```mathematica
(* Generic S-V-V vertex *)
vertexSVV = I gSVV MTD[mu, nu];
```

Note: There is no momentum dependence in the tree-level S-V-V vertex. It is purely $g^{\mu\nu}$.

---

## Triple Gauge Vertex: V-V-V

The non-abelian gauge self-interaction from the field strength $F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g f^{abc} A_\mu^b A_\nu^c$.

**Vertex factor (all momenta incoming, $p_1 + p_2 + p_3 = 0$):**

$$g f^{abc}\left[g^{\mu\nu}(p_1 - p_2)^\rho + g^{\nu\rho}(p_2 - p_3)^\mu + g^{\rho\mu}(p_3 - p_1)^\nu\right]$$

where $a,b,c$ are color/gauge indices and $\mu,\nu,\rho$ are Lorentz indices for the three gauge bosons with momenta $p_1, p_2, p_3$ respectively.

```mathematica
(* Triple gauge vertex: V_a(p1,mu) + V_b(p2,nu) + V_c(p3,rho) *)
(* All momenta incoming *)
vertexVVV = g fabc (
    MTD[mu, nu] FVD[p1 - p2, rho] +
    MTD[nu, rho] FVD[p2 - p3, mu] +
    MTD[rho, mu] FVD[p3 - p1, nu]
);
```

**SM electroweak triple gauge vertices:**

For W+W-Z and W+W-gamma, the structure constants are replaced by electroweak couplings:

```mathematica
(* W+(p1,mu) W-(p2,nu) Z(p3,rho), all incoming *)
vertexWWZ = I g cosThW (
    MTD[mu, nu] FVD[p1 - p2, rho] +
    MTD[nu, rho] FVD[p2 - p3, mu] +
    MTD[rho, mu] FVD[p3 - p1, nu]
);

(* W+(p1,mu) W-(p2,nu) gamma(p3,rho), all incoming *)
vertexWWgamma = I e (
    MTD[mu, nu] FVD[p1 - p2, rho] +
    MTD[nu, rho] FVD[p2 - p3, mu] +
    MTD[rho, mu] FVD[p3 - p1, nu]
);
```

For QCD (gluon self-coupling), $f^{abc}$ are the SU(3) structure constants and $g \to g_s$.

---

## Quartic Gauge Vertex: V-V-V-V

**Vertex factor for four gauge bosons (all momenta incoming):**

$$-ig^2\left[f^{abe}f^{cde}(g^{\mu\rho}g^{\nu\sigma} - g^{\mu\sigma}g^{\nu\rho}) + f^{ace}f^{bde}(g^{\mu\nu}g^{\rho\sigma} - g^{\mu\sigma}g^{\nu\rho}) + f^{ade}f^{bce}(g^{\mu\nu}g^{\rho\sigma} - g^{\mu\rho}g^{\nu\sigma})\right]$$

This vertex has no momentum dependence. It involves all three independent pairings of the four gauge bosons.

```mathematica
(* Quartic gauge vertex structure (schematic, one channel) *)
(* Must include all three channels with appropriate structure constants *)
vertexVVVV = -I gs^2 (
    fabe fcde (MTD[mu, rho] MTD[nu, sigma] - MTD[mu, sigma] MTD[nu, rho]) +
    face fbde (MTD[mu, nu] MTD[rho, sigma] - MTD[mu, sigma] MTD[nu, rho]) +
    fade fbce (MTD[mu, nu] MTD[rho, sigma] - MTD[mu, rho] MTD[nu, sigma])
);
```

---

## Scalar-Scalar-Vector-Vector Vertex: S-S-V-V

Arises from $|D_\mu\phi|^2$ at second order in the gauge field:

**Vertex factor:**

$$ig^2 g^{\mu\nu}$$

```mathematica
(* S-S-V-V seagull vertex *)
vertexSSVV = I g^2 MTD[mu, nu];
```

This "seagull" vertex is required by gauge invariance. Omitting it gives gauge-dependent results. It has no momentum dependence.

---

## Summary Table

| Vertex | Momentum dependence | Lorentz structure | Coupling dimension |
|--------|-------------------|-------------------|-------------------|
| S-S-S | None | Scalar | $[\lambda_3] = 1$ (mass) |
| S-S-S-S | None | Scalar | $[\lambda_4] = 0$ (dimensionless) |
| S-S-V | $p_1^\mu - p_2^\mu$ | Vector | $[g] = 0$ |
| S-V-V | None | $g^{\mu\nu}$ | $[g_{SVV}] = 1$ (mass) |
| V-V-V | $p_i^\mu$ differences | Mixed tensor-vector | $[g] = 0$ |
| V-V-V-V | None | Products of $g^{\mu\nu}$ | $[g^2] = 0$ |
| S-S-V-V | None | $g^{\mu\nu}$ | $[g^2] = 0$ |

---

## Pitfalls

1. **Momentum flow convention.** Always define whether momenta are all incoming or all outgoing and be consistent throughout the calculation. The standard convention for the triple gauge vertex is all momenta incoming with $p_1 + p_2 + p_3 = 0$. Mixing conventions produces sign errors in the momentum-dependent terms.

2. **Symmetry factors in the Lagrangian vs vertex.** The Lagrangian factor $1/n!$ for $n$ identical particles is compensated by the $n!$ ways to contract fields, so the vertex factor does not include $1/n!$. However, when computing diagrams with identical particles in the final state, include a statistical factor $1/n!$ in the phase space integration.

3. **Quartic vertices require all permutations.** The quartic gauge vertex has three independent tensor structures corresponding to three ways to pair four particles. Missing any channel violates gauge invariance.

4. **Seagull vertices are mandatory.** The S-S-V-V contact interaction is required by gauge invariance. It cancels gauge-dependent pieces from diagrams with S-S-V vertices connected by a vector propagator. Omitting it is a common error.

5. **Relative signs between diagrams.** When multiple diagrams contribute (e.g., s-channel and t-channel scalar exchange), the relative sign between them depends on the momentum routing. Use a consistent convention and verify by checking gauge invariance or known limits.

6. **Color structure.** For QCD vertices, the color factor $f^{abc}$ (triple gluon) or products $f^{abe}f^{cde}$ (quartic gluon) must be included. For quark-gluon vertices (not covered here -- see `feynman_rules.vertices_vector`), the color factor is $T^a_{ij}$ with $\mathrm{Tr}[T^a T^b] = \delta^{ab}/2$.

---

## Links

- `feynman_rules.propagators` -- Propagators for internal lines connecting these vertices
- `feyncalc_reference.momentum_and_indices` -- Handling momenta, Lorentz indices, and contractions in FeynCalc
