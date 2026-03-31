"""
Figure 3: Longitudinal polarization enhancement.

Width of S -> V1 V2 and V -> V1 V2 as function of parent-to-daughter
mass ratio, showing the M^2/m_V^2 growth from longitudinal modes.
Compared to purely transverse contributions and to channels without
longitudinal enhancement.
"""
import sys
sys.path.insert(0, '/path/to/redacted)
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('/path/to/redacted)
from decay_catalog import *

mV_daughter = 1.0
x = np.linspace(2.01, 15, 500)  # x = M_parent / m_daughter

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# --- Left: S -> V1 V2 decomposition ---
mS = x * mV_daughter
beta = np.sqrt(1 - 4*mV_daughter**2 / mS**2)

# Full SVV width
y_full = np.array([width_S_V1V2_svv(ms, mV_daughter, mV_daughter, 1.0)
                    for ms in mS])
# Normalize to |g|^2/(16 pi mS) to isolate the polarization structure
y_norm = y_full * 16 * np.pi * mS / (ps2(mS, mV_daughter, mV_daughter))

# The polarization factor is: 2 + (2mV^2 - mS^2)^2 / (4mV^4)
pol_T = 2 * np.ones_like(x)  # transverse contribution
pol_L = (2*mV_daughter**2 - mS**2)**2 / (4*mV_daughter**4)  # longitudinal
pol_full = pol_T + pol_L

ax1.plot(x, pol_full, '-', label=r'Full (T+L)', color='#0C5DA5', lw=2.5)
ax1.plot(x, pol_T, '--', label=r'Transverse only', color='#FF2C00', lw=2.5)
ax1.plot(x, pol_L, '-.', label=r'Longitudinal only', color='#00B945', lw=2.5)
# Reference line ~ x^4
x_ref = np.linspace(4, 15, 100)
ax1.plot(x_ref, x_ref**4 / (4 * 16), ':', color='grey', lw=1, alpha=0.5)
ax1.text(8, 180, r'$\sim x^4$', color='grey', fontsize=12)

ax1.set_xlabel(r'$m_S / m_V$')
ax1.set_ylabel(r'Polarization factor $\sum_{\lambda_1\lambda_2} |\varepsilon_1 \cdot \varepsilon_2|^2_{\rm eff}$')
ax1.set_xlim(2, 15)
ax1.set_yscale('log')
ax1.set_ylim(1, 5e3)
ax1.legend(loc='upper left', fontsize=12)

# --- Right: Comparison of all channels with vector daughters ---
# Normalize to |g|^2 M / (8 pi) for each
norm_fn = lambda ms: ms / (8 * np.pi)

y_svv_n = np.array([width_S_V1V2_svv(ms, mV_daughter, mV_daughter, 1.0) / (ms/(8*np.pi))
                     for ms in mS])

# V -> V1 V2 (parent vector)
M_parent = x * mV_daughter
y_vvv_n = np.array([width_V_V1V2(mp, mV_daughter, mV_daughter, 1.0) / (mp/(8*np.pi))
                     for mp in M_parent])

# V -> S V1 (mS = mV1 = mV_daughter)
y_vsv_n = np.array([width_V_SV1(mp, mV_daughter, mV_daughter, 1.0) / (mp/(8*np.pi))
                     for mp in M_parent])

# SSS for comparison (no enhancement)
y_sss_n = np.array([width_S_S1S2(ms, mV_daughter, mV_daughter, 1.0) / (ms/(8*np.pi))
                     for ms in mS])

# SSV for comparison
y_ssv_n = np.array([width_V_S1S2(mp, mV_daughter, mV_daughter, 1.0) / (mp/(8*np.pi))
                     for mp in M_parent])

ax2.semilogy(x, y_svv_n, '-', label=r'$S \to V_1 V_2$', color='#0C5DA5', lw=2.5)
ax2.semilogy(x, y_vvv_n, '-', label=r'$V \to V_1 V_2$', color='#FF2C00', lw=2.5)
ax2.semilogy(x, y_vsv_n, '-', label=r'$V \to S\, V^\prime$', color='#00B945', lw=2.5)
ax2.semilogy(x, y_sss_n, '--', label=r'$S \to S_1 S_2$', color='#845B97', lw=2)
ax2.semilogy(x, y_ssv_n, '--', label=r'$V \to S_1 S_2$', color='#FF9500', lw=2)

ax2.set_xlabel(r'$M / m_{\rm daughter}$')
ax2.set_ylabel(r'$\hat{\Gamma} \equiv \Gamma \,/\, (|g|^2 M / 8\pi)$')
ax2.set_xlim(2, 15)
ax2.set_ylim(1e-3, 1e5)
ax2.legend(loc='upper left', fontsize=11)

plt.tight_layout()
plt.savefig('/path/to/redacted)
plt.close()
print("Saved fig_longitudinal.pdf")
