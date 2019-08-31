# plot_cellcount.py

"""Count and plot number of particles in grid cell"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from postladim import ParticleFile, cellcount

# ---------------
# User settings
# ---------------

pfile = "line.nc"  # LADiM particle file
grid_file = "../data/ocean_avg_0014.nc"

tframe0 = 20  # Start time frame
tframe1 = 95

# Subgrid definition
i0, i1 = 58, 150
j0, j1 = 60, 140

# --------------------------------

# ROMS grid, plot domain
with Dataset(grid_file) as f0:
    M = f0.variables["mask_rho"][j0:j1, i0:i1]
    lon = f0.variables["lon_rho"][j0:j1, i0:i1]
    lat = f0.variables["lat_rho"][j0:j1, i0:i1]

# Cell centers and boundaries
Xcell = np.arange(i0, i1)
Ycell = np.arange(j0, j1)
Xb = np.arange(i0 - 0.5, i1)
Yb = np.arange(j0 - 0.5, j1)

# ---------------------------
# Read and count particles
# ---------------------------

pf = ParticleFile(pfile)
C = np.zeros_like(M)
for t in range(tframe0, tframe1):
    X, Y = pf.position(t)
    C += cellcount(X, Y, gridspec=(i0, i1, j0, j1))
C = np.ma.masked_where(C == 0, C)

# ------------------------- ---
# Plot particle concentration
# -----------------------------

plt.set_cmap("cool")
plt.pcolormesh(Xb, Yb, C)
plt.colorbar()

# Land mask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(M > 0, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

#   Graticule
plt.contour(Xcell, Ycell, lat, levels=range(55, 64), colors="black", linestyles=":")
plt.contour(Xcell, Ycell, lon, levels=range(-4, 10, 2), colors="black", linestyles=":")

plt.axis("image")
plt.show()
