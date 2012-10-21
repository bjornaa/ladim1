import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date
import roppy
from roppy.mpl_util import landmask
from particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file  = '../output/pyladim_out.nc'
roms_file      = '../input/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70,   80
i1, j1 = 150, 133

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0,i1,j0,j1))

#
#print particle_file
pf = ParticleFile(particle_file)

Ntimes = pf.nFrames


def animate():
    for t in range(1, Ntimes):
        X, Y = pf.get_position(t)
        X, Y = X-i0, Y-j0
        tstring = pf.get_time(t)
        h[0].set_xdata(X)
        h[0].set_ydata(Y)
        ax.set_title(tstring)
        fig.canvas.draw()


# Create a figure

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(1,1,1)

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.h, cmap=cmap, alpha=0.3)
#fig.colorbar(h)
roppy.mpl_util.landmask(g.mask_rho, (0.6, 0.8, 0.0))

# Plot initial particle distribution
X, Y = pf.get_position(0)
X, Y = X-i0, Y-j0
tstring = pf.get_time(0)
h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(tstring)

# Do the animation
fig.canvas.manager.window.after(100, animate)

# Show the results
plt.axis('image')
plt.show()

