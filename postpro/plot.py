# import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import roppy
from roppy.mpl_util import landmask
from particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = '../output/pyladim_out.nc'
roms_file = '../input/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70,   80
i1, j1 = 150, 133

t = 30     # time step 31

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))

#
# print particle_file
pf = ParticleFile(particle_file)

Ntimes = pf.nFrames


# Create a figure

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
# fig.colorbar(h)

landmask(g, (0.6, 0.8, 0.0))

# Plot initial particle distribution
X, Y = pf.get_position(t)
tstring = pf.get_time(t)
h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(tstring)


# Show the results
plt.axis('image')
plt.show()
