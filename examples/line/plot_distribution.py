import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

from postladim import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = "line.nc"
grid_file = "../data/ocean_avg_0014.nc"

# Subgrid for plot
i0, i1 = 58, 150
j0, j1 = 60, 140

# timestamp
t = 90

# ----------------

# Read grid info
with Dataset(grid_file) as f0:
    H = f0.variables["h"][j0:j1, i0:i1]
    M = f0.variables["mask_rho"][j0:j1, i0:i1]
    lon = f0.variables["lon_rho"][j0:j1, i0:i1]
    lat = f0.variables["lat_rho"][j0:j1, i0:i1]

# Cell centers and boundaries
Xcell = np.arange(i0, i1)
Ycell = np.arange(j0, j1)
Xb = np.arange(i0 - 0.5, i1)
Yb = np.arange(j0 - 0.5, j1)

# Read particle_file
with ParticleFile(particle_file) as pf:
    X, Y = pf.position(t)
    timestamp = pf.time(t)

# ---------------------
# Plotting
# ---------------------

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1)

# Make background map
# -------------------
#   Bathymetry
cmap = plt.get_cmap("Blues")
h = ax.contourf(Xcell, Ycell, H, cmap=cmap, alpha=0.3)

#   Landmask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(M > 0, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

#   Graticule
ax.contour(Xcell, Ycell, lat, levels=range(55, 64), colors="black", linestyles=":")
ax.contour(Xcell, Ycell, lon, levels=range(-4, 10, 2), colors="black", linestyles=":")

# Plot particle distribution
# --------------------------
ax.plot(X, Y, ".", color="red", markeredgewidth=0, lw=0.5)
ax.set_title(timestamp)

# Show the results
# ----------------
plt.axis("image")
plt.axis((i0 + 1, i1 - 1, j0 + 1, j1 - 1))
plt.show()
