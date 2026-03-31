"""
Figure 4: SM validation and mass-ratio anatomy.

Left: ratio of tree-level prediction to PDG value for 4 benchmark decays.
Right: anatomy of t -> Wb width as function of mt, showing the interplay
       of phase space closure and longitudinal enhancement.
"""
import sys
sys.path.insert(0, '/path/to/redacted)
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('/path/to/redacted)
from decay_catalog import *

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# --- Left: SM validation bar chart ---
labels = [r'$H\to b\bar{b}$', r'$Z\to e^+e^-$', r'$W\to e\nu$', r'$t\to Wb$']

# Tree-level values (GeV)
sm = sm_validation()
tree = [sm['H_bb']['tree_run'], sm['Z_ee']['tree'], sm['W_enu']['tree'], sm['t_Wb']['tree']]
pdg = [sm['H_bb']['pdg_partial'], sm['Z_ee']['pdg_partial'],
       sm['W_enu']['pdg_partial'], sm['t_Wb']['pdg_width']]
# NDA for H->bb: rescale from pole to running mass (NDA_pole * (mb_run/mb_pole)^2)
nda_Hbb_run = sm['H_bb']['nda'] * (SM.mb_run_mH / SM.mb_pole)**2
nda = [nda_Hbb_run, sm['Z_ee']['nda'], sm['W_enu']['nda'], sm['t_Wb']['nda']]

ratios_tree = [t/p for t, p in zip(tree, pdg)]
ratios_nda = [n/p for n, p in zip(nda, pdg)]

x_pos = np.arange(len(labels))
w = 0.35
bars1 = ax1.bar(x_pos - w/2, ratios_tree, w, label='Tree-level exact',
                color='#0C5DA5', alpha=0.85)
bars2 = ax1.bar(x_pos + w/2, ratios_nda, w, label='NDA improved',
                color='#FF9500', alpha=0.85)

ax1.axhline(1.0, color='grey', ls='--', lw=1, alpha=0.7)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(labels, fontsize=13)
ax1.set_ylabel(r'$\Gamma_{\rm calc} / \Gamma_{\rm PDG}$')
ax1.set_ylim(0.85, 1.15)
ax1.legend(loc='upper right', fontsize=12)

# Annotate ratios
for bar, r in zip(bars1, ratios_tree):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{r:.2f}', ha='center', va='bottom', fontsize=10)
for bar, r in zip(bars2, ratios_nda):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{r:.2f}', ha='center', va='bottom', fontsize=10)

# --- Right: t -> Wb anatomy ---
mW = 80.377
mb = 4.18
gL = SM.g / np.sqrt(2)

mt_arr = np.linspace(mW + mb + 0.1, 350, 300)

gamma_t = np.array([width_f_Vf_chiral(mt, mW, mb, gL2=gL**2, gR2=0)
                     for mt in mt_arr])

ax2.plot(mt_arr, gamma_t, '-', color='#0C5DA5', lw=2.5)
ax2.axvline(172.56, color='grey', ls='--', lw=1, alpha=0.7)
ax2.axhline(1.424, color='#FF2C00', ls=':', lw=1.5, alpha=0.7)
ax2.text(175, 1.5, r'$m_t = 172.6$ GeV', fontsize=10, color='grey')
ax2.text(250, 1.55, r'$\Gamma_{\rm PDG}$', fontsize=10, color='#FF2C00')

# Mark the physical point
ax2.plot(172.56, width_f_Vf_chiral(172.56, mW, mb, gL2=gL**2, gR2=0),
         'o', color='#FF2C00', ms=7, zorder=5)

ax2.set_xlabel(r'$m_t$ [GeV]')
ax2.set_ylabel(r'$\Gamma(t \to Wb)$ [GeV]')
ax2.set_xlim(mW + mb, 350)
ax2.set_ylim(0, None)

plt.tight_layout()
plt.savefig('/path/to/redacted)
plt.close()
print("Saved fig_sm_validation.pdf")
