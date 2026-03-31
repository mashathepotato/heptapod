#!/usr/bin/env python3
"""
Per-pair suppression factor analysis figure.
Shows (a) the effective per-pair suppression from NDA and MG,
and (b) phase space volume scaling.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('heptapod.mplstyle')

# --- Data ---
n_pairs = np.array([0, 1, 2, 3])
k_body = 2 * n_pairs + 3  # total final state particles

# Phase space volumes
phi = np.array([1.41e-6, 9.76e-17, 8.13e-28, 1.73e-39, 1.33e-51])
phi_ratio = phi[1:] / phi[:-1]  # Phi_{k+2}/Phi_k

# NDA BR
nda_br = np.array([2.86, 1.85e-5, 1.89e-9, 8.26e-13])
nda_suppression = nda_br[1:] / nda_br[:-1]

# MG BR
mg_br = np.array([1.0, 3.56e-5, 4.34e-10])
mg_suppression = mg_br[1:] / mg_br[:-1]

# Dominant class width per diagram
width_per_diag = np.array([8.56e-19, 1.39e-24, 6.73e-30, 5.73e-35])
width_per_diag_suppression = width_per_diag[1:] / width_per_diag[:-1]

# Dominant class multiplicity
n_dom = np.array([1, 4, 84, 4320])
mult_ratio = n_dom[1:] / n_dom[:-1]

# Analytical estimate: (alpha/pi)^2
alpha_over_pi_sq = (1/137 / np.pi)**2

# --- Figure ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# (a) Per-pair suppression factor
transitions = [r'$0\to 1$', r'$1\to 2$', r'$2\to 3$']
x = np.arange(len(transitions))

ax1.semilogy(x, np.abs(nda_suppression), 's-', color='#FF2C00', markersize=10,
             label=r'NDA (total BR)')
ax1.semilogy(x[:2], np.abs(mg_suppression), 'D-', color='#0C5DA5', markersize=10,
             markerfacecolor='white', markeredgewidth=2,
             label=r'MadGraph (total BR)')
ax1.semilogy(x, np.abs(width_per_diag_suppression), 'o--', color='#845B97',
             markersize=8, label=r'NDA (per diagram)')
ax1.axhline(y=alpha_over_pi_sq, color='#474747', linestyle=':', linewidth=1.5)
ax1.text(2.0, alpha_over_pi_sq * 2.5, r'$(\alpha/\pi)^2$', fontsize=12,
         color='#474747', ha='center')

ax1.set_xticks(x)
ax1.set_xticklabels(transitions)
ax1.set_xlabel(r'Transition $n \to n+1$')
ax1.set_ylabel(r'Per-pair suppression factor')
ax1.legend(fontsize=10, loc='upper left')
ax1.set_ylim(1e-7, 1e-2)

# (b) Decomposition: coupling, phase space, multiplicity
ax2.semilogy(x, np.abs(phi_ratio[:3]), 'v-', color='#00B945', markersize=10,
             label=r'Phase space $\Phi_{k+2}/\Phi_k$')
ax2.semilogy(x, mult_ratio, '^-', color='#FF9500', markersize=10,
             label=r'Multiplicity $N_{n+1}/N_n$')

# Coupling factor per pair (constant)
e4 = (0.302822)**4
ax2.axhline(y=e4, color='#C20078', linestyle='--', linewidth=1.5)
ax2.text(2.0, e4 * 2, r'$e^4 = (4\pi\alpha)^2$', fontsize=11,
         color='#C20078', ha='center')

ax2.set_xticks(x)
ax2.set_xticklabels(transitions)
ax2.set_xlabel(r'Transition $n \to n+1$')
ax2.set_ylabel(r'Factor')
ax2.legend(fontsize=10, loc='center right')
ax2.set_ylim(1e-13, 1e3)

plt.tight_layout()
fig.savefig('figures/suppression_analysis.pdf')
plt.close()
print("Saved figures/suppression_analysis.pdf")
