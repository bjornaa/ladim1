import time
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import roppy
import roppy.mpl_util
from postladim.particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = 'streak.nc'
grid_file = '../data/ocean_avg_0014.nc'

# Subgrid definition
i0, i1 = 100, 130
j0, j1 = 90, 115

# timestamp
t = 176


# ----------------

# ROMS grid, plot domain

# Slight overkill to use roppy, could be more stand alone
f0 = Dataset(grid_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))


# particle_file
pf = ParticleFile(particle_file)

Ntimes = pf.ntimes

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1)

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g, (0.6, 0.8, 0.0))
ax.contour(g.X, g.Y, g.lat_rho, levels=range(57, 64),
           colors='black', linestyles=':')
ax.contour(g.X, g.Y, g.lon_rho, levels=range(-4, 10, 2),
           colors='black', linestyles=':')


# Plot initial particle distribution
X, Y = pf.get_position(t)
timestring = pf.get_time(t)
h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(timestring)

# Show the results
plt.axis('image')
plt.axis((i0+1, i1-1, j0+1, j1-1))
plt.show()
