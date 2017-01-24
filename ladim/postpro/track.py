# -*- coding: utf-8 -*-

# Make a track of one particle

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import roppy.mpl_util
from particlefile import ParticleFile

pid0 = 0   # Must use zero for streak line

particle_file = "../output/line.nc"
roms_file = '../input/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70, 80
i1, j1 = 150, 133

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))
# f0.close()


pf = ParticleFile(particle_file)

X, Y, first_time, last_time = pf.read_track(pid0)
X = np.array(X)
Y = np.array(Y)

# Make plot

cmap = plt.get_cmap('Blues')
plt.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g, (0.6, 0.8, 0.0))

plt.plot(X[0], Y[0], 'rx')
plt.plot(X, Y, '-')

plt.axis('image')
plt.show()
