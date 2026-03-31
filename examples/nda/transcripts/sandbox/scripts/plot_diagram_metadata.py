#!/usr/bin/env python3
"""
Diagram metadata figures:
(a) Total diagram count vs n
(b) Dominant-class diagram count vs n
(c) Per-class breakdown stacked bar chart
(d) Per-pair suppression factor
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

plt.style.use('heptapod.mplstyle')

# --- Data ---
n_pairs = np.array([0, 1, 2, 3])

# Total diagram counts
total_diagrams = np.array([1, 18, 1122, 149400])

# Per-class breakdown: list of dicts {n_heavy: n_diagrams}
classes = {
    0: {1: 1},
    1: {1: 4, 2: 12, 3: 2},
    2: {1: 84, 2: 378, 3: 504, 4: 138, 5: 18},
    3: {1: 4320, 2: 24768, 3: 52272, 4: 47520, 5: 16416, 6: 3744, 7: 360},
}

# Dominant class (1 heavy W) diagram count
dominant_diagrams = np.array([1, 4, 84, 4320])

# NDA width per diagram (dominant class)
width_per_diagram = np.array([8.56e-19, 1.39e-24, 6.73e-30, 5.73e-35])

# NDA total dominant class width
dominant_width = dominant_diagrams * width_per_diagram

# NDA branching ratios
nda_br = np.array([2.86, 1.85e-5, 1.89e-9, 8.26e-13])

# MG branching ratios
mg_br_dict = {1: 3.56e-5, 2: 4.34e-10}

# Per-pair suppression (from NDA dominant class total)
suppression_nda = np.array([
    nda_br[1] / nda_br[0],
    nda_br[2] / nda_br[1],
    nda_br[3] / nda_br[2],
])
suppression_mg = np.array([
    mg_br_dict[1] / 1.0,  # relative to BR(n=0) ~ 1
    mg_br_dict[2] / mg_br_dict[1],
])

# --- Figure: 2x2 panel ---
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# (a) Total diagram count
ax = axes[0, 0]
ax.semilogy(n_pairs, total_diagrams, 'o-', color='#0C5DA5', markersize=8)
ax.set_xlabel(r'Number of $e^+e^-$ pairs $n$')
ax.set_ylabel(r'Total diagrams')
ax.set_xticks([0, 1, 2, 3])
for i, (x, y) in enumerate(zip(n_pairs, total_diagrams)):
    offset = 1.8 if y > 10 else 1.5
    ax.annotate(f'{y:,}', (x, y * offset), ha='center', fontsize=10, color='#0C5DA5')

# (b) Dominant class diagram count + fraction
ax = axes[0, 1]
fraction = dominant_diagrams / total_diagrams * 100
ax.semilogy(n_pairs, dominant_diagrams, 's-', color='#FF2C00', markersize=8,
            label=r'Dominant (1$W$)')
ax.semilogy(n_pairs, total_diagrams, 'o--', color='#0C5DA5', markersize=8,
            alpha=0.4, label=r'All classes')
ax.set_xlabel(r'Number of $e^+e^-$ pairs $n$')
ax.set_ylabel(r'Diagram count')
ax.set_xticks([0, 1, 2, 3])
ax.legend(fontsize=10, loc='upper left')
# Annotate fractions
for i, (x, y, f) in enumerate(zip(n_pairs, dominant_diagrams, fraction)):
    ax.annotate(f'{f:.0f}\\%', (x + 0.15, y), fontsize=9, color='#FF2C00', va='center')

# (c) Stacked bar chart of class breakdown
ax = axes[1, 0]
max_heavy = 7
bar_width = 0.6
bottom = np.zeros(len(n_pairs))
cmap = plt.cm.viridis
heavy_colors = [cmap(i / max_heavy) for i in range(max_heavy + 1)]

for h in range(1, max_heavy + 1):
    counts = np.array([classes[n].get(h, 0) for n in n_pairs])
    if counts.sum() == 0:
        continue
    # Normalize to fraction
    fracs = counts / total_diagrams * 100
    ax.bar(n_pairs, fracs, bar_width, bottom=bottom,
           color=heavy_colors[h], label=f'{h}$W$' if h <= 4 else None)
    bottom += fracs

ax.set_xlabel(r'Number of $e^+e^-$ pairs $n$')
ax.set_ylabel(r'Class fraction (\%)')
ax.set_xticks([0, 1, 2, 3])
ax.set_ylim(0, 105)
ax.legend(fontsize=9, loc='upper right', title=r'Heavy props', title_fontsize=9)

# (d) Width per diagram and total dominant class width
ax = axes[1, 1]
ax.semilogy(n_pairs, width_per_diagram, 'o-', color='#845B97', markersize=8,
            label=r'Width/diagram')
ax.semilogy(n_pairs, dominant_width, 's--', color='#FF2C00', markersize=8,
            label=r'Total class width')
# Add MG points
mg_width_per_diag = {1: 1.066e-23 / 4, 2: 1.301e-28 / 84}
ax.semilogy([1, 2], [mg_width_per_diag[1], mg_width_per_diag[2]],
            'D', color='#0C5DA5', markersize=9, markerfacecolor='white',
            markeredgewidth=2, label=r'MG width/diagram', zorder=6)
ax.set_xlabel(r'Number of $e^+e^-$ pairs $n$')
ax.set_ylabel(r'Width (GeV)')
ax.set_xticks([0, 1, 2, 3])
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout()
fig.savefig('figures/diagram_metadata.pdf')
plt.close()
print("Saved figures/diagram_metadata.pdf")
