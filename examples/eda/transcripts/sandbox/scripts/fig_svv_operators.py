"""
Figure 2: S -> V1 V2 operator comparison.

Three different Lorentz structures for scalar decaying to two massive vectors:
- Renormalizable SVV (g eps1.eps2)
- Dim-5 field-strength (phi F F)
- Dim-5 dual field-strength (phi F Ftilde)

Shows dramatically different threshold behavior and high-energy growth.
Left: equal mass vectors, width vs mS/mV.
Right: threshold region detail (log scale).
"""
import sys
sys.path.insert(0, '/path/to/redacted)
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('/path/to/redacted)
from decay_catalog import *

mV = 1.0  # fix vector mass
x = np.linspace(2.001, 12, 500)  # x = mS / mV
mS = x * mV

# Compute widths, normalize to |g|^2 mV / (8 pi) for dim-4,
# and |g|^2 mV^3 / (8 pi) for dim-5 (coupling has dim GeV^{-1})
norm4 = mV / (8 * np.pi)  # dim-4 normalization
# For fair comparison, normalize each to its own coupling dimension
# dim-4 g has dim [GeV], dim-5 g has dim [GeV^{-1}]
# Plot Gamma / (|g|^2 * mS) to get dimensionless for all

norm = lambda ms: ms / (8 * np.pi)

y_svv = np.array([width_S_V1V2_svv(ms, mV, mV, 1.0) / (ms / (8*np.pi))
                   for ms in mS])
y_ff = np.array([width_S_V1V2_dim5FF(ms, mV, mV, 1.0) / (ms / (8*np.pi))
                  for ms in mS])
y_ffd = np.array([width_S_V1V2_dim5FFdual(ms, mV, mV, 1.0) / (ms / (8*np.pi))
                   for ms in mS])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: linear scale, full range
ax1.plot(x, y_svv, '-', label=r'SVV ($g\, \varepsilon_1 \cdot \varepsilon_2$)',
         color='#0C5DA5', lw=2.5)
ax1.plot(x, y_ff, '-', label=r'$\phi FF$ ($g\,[k_1 \cdot k_2\, \varepsilon_1 \cdot \varepsilon_2 - \ldots]$)',
         color='#FF2C00', lw=2.5)
ax1.plot(x, y_ffd, '-', label=r'$\phi F\tilde{F}$ ($g\,\epsilon^{\mu\nu\rho\sigma}\ldots$)',
         color='#00B945', lw=2.5)

ax1.set_xlabel(r'$m_S / m_V$')
ax1.set_ylabel(r'$\hat{\Gamma} \equiv \Gamma \,/\, (|g|^2 m_S / 8\pi)$')
ax1.set_xlim(2, 12)
ax1.set_ylim(0, None)
ax1.legend(loc='upper left', fontsize=11)

# Right: log-log near threshold
beta = np.sqrt(1 - 4*mV**2/mS**2)

ax2.loglog(beta, y_svv, '-', label=r'SVV: $\sim\beta/m_V^4$',
           color='#0C5DA5', lw=2.5)
ax2.loglog(beta, y_ff, '-', label=r'$\phi FF$: $\sim\beta\,(m_S^4 + \ldots)$',
           color='#FF2C00', lw=2.5)
ax2.loglog(beta, y_ffd, '-', label=r'$\phi F\tilde{F}$: $\sim\beta^3$',
           color='#00B945', lw=2.5)

# Reference slopes
b_ref = np.logspace(-2, -0.05, 100)
ax2.loglog(b_ref, 0.7*b_ref, ':', color='grey', lw=1, alpha=0.5)
ax2.loglog(b_ref, 0.7*b_ref**3, ':', color='grey', lw=1, alpha=0.5)
ax2.text(0.015, 0.03, r'$\beta^1$', color='grey', fontsize=11, rotation=20)
ax2.text(0.03, 5e-5, r'$\beta^3$', color='grey', fontsize=11, rotation=50)

ax2.set_xlabel(r'$\beta = \sqrt{1 - 4m_V^2/m_S^2}$')
ax2.set_ylabel(r'$\hat{\Gamma}$')
ax2.set_xlim(1e-2, 1)
ax2.legend(loc='lower right', fontsize=10.5)

plt.tight_layout()
plt.savefig('/path/to/redacted)
plt.close()
print("Saved fig_svv_operators.pdf")
