#!/usr/bin/env python3
"""
Plot branching ratio vs number of e+e- pairs n,
with experimental sensitivity thresholds.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.style.use('heptapod.mplstyle')

# --- Data ---
n_pairs = np.array([0, 1, 2, 3])

# NDA branching ratios (dominant class total)
nda_br = np.array([2.86, 1.85e-5, 1.89e-9, 8.26e-13])

# MadGraph branching ratios (where available)
mg_n = np.array([1, 2])
mg_br = np.array([3.56e-5, 4.34e-10])

# Experimental measurement
exp_n = np.array([1])
exp_br = np.array([3.4e-5])
exp_err = np.array([0.4e-5])  # combined stat+sys

# NDA/MG correction factor for calibrated estimate
# n=1: MG/NDA = 1.92, n=2: MG/NDA = 0.23
# Use geometric mean of ratio spread as uncertainty band
nda_br_calibrated = nda_br.copy()
nda_br_calibrated[1] = mg_br[0]  # use MG where available
nda_br_calibrated[2] = mg_br[1]
# For n=3: NDA = 8.26e-13; MG/NDA ratio was 0.23-1.92
# Use NDA as central, band from 0.1x to 3x
nda_br_upper = nda_br.copy()
nda_br_lower = nda_br.copy()
nda_br_upper[3] = nda_br[3] * 3
nda_br_lower[3] = nda_br[3] * 0.1

# Extrapolated n=4 estimate using MG per-pair suppression
# MG per-pair: 4.34e-10 / 3.56e-5 = 1.22e-5
# But suppression weakens with n; NDA ratio weakens by ~4x per step
# Conservative range: 1e-17 to 1e-15
n4_est_central = 5e-16
n4_est_upper = 5e-15
n4_est_lower = 5e-17

# Experimental sensitivities
sensitivities = {
    r'SINDRUM (1985)': 1e-5,
    r'Mu3e Phase I': 2e-15,
    r'Mu3e Phase II': 1e-16,
    r'HiMB (future)': 1e-18,
}

# --- Figure ---
fig, ax = plt.subplots(figsize=(8, 6))

# Sensitivity bands (horizontal spans)
colors_sens = ['#9E9E9E', '#0C5DA5', '#00B945', '#845B97']
y_positions = list(sensitivities.values())
labels_sens = list(sensitivities.keys())

for i, (label, ses) in enumerate(sensitivities.items()):
    ax.axhline(y=ses, color=colors_sens[i], linestyle='--', linewidth=1.2, alpha=0.7)
    # Place label at right edge
    ax.text(3.65, ses * 1.8, label, fontsize=9, color=colors_sens[i],
            ha='right', va='bottom')

# Fill observable region
ax.axhspan(1e-18, 1e1, alpha=0.03, color='green')

# NDA points
ax.semilogy(n_pairs, nda_br, 'o-', color='#FF2C00', markersize=9,
            label=r'NDA estimate', zorder=5)

# MadGraph points
ax.semilogy(mg_n, mg_br, 's', color='#0C5DA5', markersize=11,
            markerfacecolor='white', markeredgewidth=2.5,
            label=r'MadGraph (exact)', zorder=6)

# Experimental measurement
ax.errorbar(exp_n, exp_br, yerr=exp_err, fmt='D', color='#00B945',
            markersize=10, markeredgewidth=2, capsize=4, capthick=2,
            label=r'SINDRUM measurement', zorder=7)

# NDA uncertainty band for n=3
ax.fill_between([2.9, 3.1], [nda_br_lower[3], nda_br_lower[3]],
                [nda_br_upper[3], nda_br_upper[3]],
                color='#FF2C00', alpha=0.15)

# Extrapolated n=4
ax.semilogy([4], [n4_est_central], 'v', color='#FF9500', markersize=10,
            markeredgewidth=2, markerfacecolor='white',
            label=r'Extrapolated ($n=4$)', zorder=5)
ax.fill_between([3.9, 4.1], [n4_est_lower, n4_est_lower],
                [n4_est_upper, n4_est_upper],
                color='#FF9500', alpha=0.15)

ax.set_xlabel(r'Number of $e^+e^-$ pairs $n$')
ax.set_ylabel(r'Branching ratio')
ax.set_xlim(-0.3, 4.6)
ax.set_ylim(1e-20, 1e1)
ax.set_xticks([0, 1, 2, 3, 4])
ax.set_xticklabels([r'$0$', r'$1$', r'$2$', r'$3$', r'$4$'])
ax.legend(loc='lower left', fontsize=11)

fig.savefig('figures/br_vs_n.pdf')
plt.close()
print("Saved figures/br_vs_n.pdf")
