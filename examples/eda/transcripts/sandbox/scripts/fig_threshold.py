"""
Figure 1: Threshold power-law structure of all 1->2 decay channels.

Left: log-log near threshold reveals beta^n power laws.
Right: full range on linear scale (fermionic channels only,
       which remain finite as beta -> 1).
"""
import sys
sys.path.insert(0, '/path/to/redacted)
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('/path/to/redacted)
from decay_catalog import *

M = 1.0
norm = M / (8 * np.pi)

# --- Left panel: log-log threshold structure ---
beta_log = np.logspace(-2.5, -0.01, 500)
m_log = M * np.sqrt(1 - beta_log**2) / 2

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Pure bosonic
y_sss = width_S_S1S2(M, m_log, m_log, 1.0) / norm
ax1.loglog(beta_log, y_sss, '-', label=r'SSS: $S\to S_1 S_2$',
           color='#0C5DA5', lw=2.5)

y_ssv = width_V_S1S2(M, m_log, m_log, 1.0) / norm
ax1.loglog(beta_log, y_ssv, '-', label=r'SSV: $V\to S_1 S_2$',
           color='#FF2C00', lw=2.5)

# Fermionic (scalar parent)
y_sff_s = width_S_ff_va(M, m_log, m_log, gS2=1, gP2=0) / norm
ax1.loglog(beta_log, y_sff_s, '-', label=r'SFF (scalar): $S\to f\bar{f}$',
           color='#00B945', lw=2.5)

y_sff_p = width_S_ff_va(M, m_log, m_log, gS2=0, gP2=1) / norm
ax1.loglog(beta_log, y_sff_p, '--', label=r'SFF (pseudo): $S\to f\bar{f}$',
           color='#00B945', lw=2.5)

# Fermionic (vector parent)
y_vff_v = width_V_ff_va(M, m_log, m_log, gV2=1, gA2=0) / norm
ax1.loglog(beta_log, y_vff_v, '-', label=r'VFF (vector): $V\to f\bar{f}$',
           color='#FF9500', lw=2.5)

y_vff_a = width_V_ff_va(M, m_log, m_log, gV2=0, gA2=1) / norm
ax1.loglog(beta_log, y_vff_a, '--', label=r'VFF (axial): $V\to f\bar{f}$',
           color='#FF9500', lw=2.5)

# Reference slopes
b_ref = beta_log
ax1.loglog(b_ref, 0.15*b_ref**1, ':', color='grey', lw=1, alpha=0.6)
ax1.loglog(b_ref, 0.15*b_ref**3, ':', color='grey', lw=1, alpha=0.6)
ax1.text(0.006, 0.25, r'$\beta^1$', color='grey', fontsize=12, rotation=17)
ax1.text(0.015, 0.0003, r'$\beta^3$', color='grey', fontsize=12, rotation=47)

ax1.set_xlabel(r'$\beta = \sqrt{1 - 4m^2/M^2}$')
ax1.set_ylabel(r'$\hat{\Gamma} \equiv \Gamma \,/\, (|g|^2 M / 8\pi)$')
ax1.set_xlim(3e-3, 1)
ax1.set_ylim(1e-8, 5)
ax1.legend(loc='lower right', fontsize=9.5)

# --- Right panel: linear scale, full range ---
beta_lin = np.linspace(1e-4, 0.9999, 500)
m_lin = M * np.sqrt(1 - beta_lin**2) / 2

# Scalar parent -> fermions
y1 = width_S_ff_va(M, m_lin, m_lin, gS2=1, gP2=0) / norm
y2 = width_S_ff_va(M, m_lin, m_lin, gS2=0, gP2=1) / norm
ax2.plot(beta_lin, y1, '-', label=r'$S\to f\bar{f}$\,(scalar)', color='#0C5DA5', lw=2)
ax2.plot(beta_lin, y2, '--', label=r'$S\to f\bar{f}$\,(pseudo)', color='#0C5DA5', lw=2)

# Vector parent -> fermions
y3 = width_V_ff_va(M, m_lin, m_lin, gV2=1, gA2=0) / norm
y4 = width_V_ff_va(M, m_lin, m_lin, gV2=0, gA2=1) / norm
y5 = width_V_ff_tensor(M, m_lin, m_lin, 1.0) / norm
ax2.plot(beta_lin, y3, '-', label=r'$V\to f\bar{f}$\,(vector)', color='#FF2C00', lw=2)
ax2.plot(beta_lin, y4, '--', label=r'$V\to f\bar{f}$\,(axial)', color='#FF2C00', lw=2)
ax2.plot(beta_lin, y5, '-.', label=r'$V\to f\bar{f}$\,(tensor)', color='#FF2C00', lw=2)

# Fermion parent -> scalar + fermion
y6 = width_f_Sf_va(M, m_lin, m_lin, gS2=1, gP2=0) / norm
y7 = width_f_Sf_va(M, m_lin, m_lin, gS2=0, gP2=1) / norm
ax2.plot(beta_lin, y6, '-', label=r'$f\to S\,f^\prime$\,(scalar)', color='#00B945', lw=2)
ax2.plot(beta_lin, y7, '--', label=r'$f\to S\,f^\prime$\,(pseudo)', color='#00B945', lw=2)

# SSS and SSV for reference
y8 = width_S_S1S2(M, m_lin, m_lin, 1.0) / norm
y9 = width_V_S1S2(M, m_lin, m_lin, 1.0) / norm
ax2.plot(beta_lin, y8, '-', label=r'$S\to S_1 S_2$', color='#845B97', lw=2)
ax2.plot(beta_lin, y9, '--', label=r'$V\to S_1 S_2$', color='#845B97', lw=2)

ax2.set_xlabel(r'$\beta = \sqrt{1 - 4m^2/M^2}$')
ax2.set_ylabel(r'$\hat{\Gamma} \equiv \Gamma \,/\, (|g|^2 M / 8\pi)$')
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.1)
ax2.legend(loc='upper left', fontsize=8.5, ncol=2)

plt.tight_layout()
plt.savefig('/path/to/redacted)
plt.close()
print("Saved fig_threshold.pdf")
