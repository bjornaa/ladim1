import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import roppy
from roppy.mpl_util import landmask
from particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
# particle_file = '../output/pyladim_out.nc'
particle_file = '../output/streak.nc'
roms_file = '../input/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70, 80
i1, j1 = 150, 133

t = 96     # time step 31

# Length scale (in grid units)
sigma = 3.14

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))

#
# print particle_file
pf = ParticleFile(particle_file)

# Ntimes = pf.nFrames

X, Y = pf.get_position(t)
tstring = pf.get_time(t)


# # Compute weigths based on land
# N = len(X)
# for k in range(N):
#     A = np.zeros((j1-j0, i1-i0))
#     for j in range(j0, j1):
#         for i in range(i0, i1):
#             A[j-j0, i-i0] += g.mask_rho * np.exp

A = np.zeros((j1-j0, i1-i0))
L2 = 2*sigma
for j in range(j0, j1):
    for i in range(i0, i1):
        A[j-j0, i-i0] = np.sum(np.exp(- ((i-X)/L2)**2 - ((j-Y)/L2)**2))
A = A / (np.pi * L2**2)

print(np.sum(A))

# Create a figure

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)

# Make background map
# cmap = plt.get_cmap('Blues')
# h = ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
# fig.colorbar(h)

h = ax.contourf(g.X, g.Y, A)
fig.colorbar(h)

landmask(g, (0.6, 0.8, 0.0))

# Plot iparticle distribution
h = ax.plot(X, Y, '.', color='black', markeredgewidth=0, lw=0.5)
ax.set_title(tstring)

# Show the results
plt.axis('image')
plt.show()
