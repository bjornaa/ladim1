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

# Subgrid definition
i0, i1 = 58, 150
j0, j1 = 60, 130

# Particle identifiers for trajectories
# Here every 5th
pids = range(5, 1000, 10)

# ----------------

# ROMS grid, plot domain
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

# particle_file
pf = ParticleFile(particle_file)

# Make plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1)

# Background map
#   Bathymetry
cmap = plt.get_cmap("Blues")
h = ax.contourf(Xcell, Ycell, H, cmap=cmap, alpha=0.9)

#   Landmask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(M > 0, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

#   Graticule
ax.contour(Xcell, Ycell, lat, levels=range(55, 64), colors="black", linestyles=":")
ax.contour(Xcell, Ycell, lon, levels=range(-4, 10, 2), colors="black", linestyles=":")


# Trajectories
for p in pids:
    #traj = pf.trajectory(p)
    plt.plot(pf.X.sel(pid=p), pf.Y.sel(pid=p).values, "r")
    # plt.plot(traj.X[0], traj.Y[0], 'ro')  # Start points

plt.axis("image")
plt.show()
