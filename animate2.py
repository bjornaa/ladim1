import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date
import roppy
from roppy.mpl_util import landmask

# ---------------
# User settings
# ---------------

# Files
particle_file  = './output/pyladim_out.nc'
roms_file = 'data/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70,   80
i1, j1 = 150, 133

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0,i1,j0,j1))

#
print particle_file
f  = Dataset(particle_file)

Ntimes = len(f.dimensions['Time'])

# ------------------
# Utility functions
# ------------------

def read(t):
    """Read the particles at given time frame"""
    
    p0 = f.variables['pStart'][t]
    Npart = f.variables['pCount'][t]
    tid = f.variables['time'][t]
    tunit = f.variables['time'].units
    #print p0, Npart
    timestr = num2date(tid, tunit)
    X = f.variables['X'][p0:p0+Npart]
    Y = f.variables['Y'][p0:p0+Npart]
    # Not handling subgrids properly??
    X = X - i0
    Y = Y - j0
    return X, Y, timestr


def animate():
    for t in range(1, Ntimes):
        X, Y, tstring = read(t)
        h[0].set_xdata(X)
        h[0].set_ydata(Y)
        ax.set_title(tstring)
        fig.canvas.draw()





# Create a figure

fig = plt.figure(figsize=(12,8))
#ax = fig.add_subplot(1,1,1)
ax = fig.add_axes((0.1,0.1,0.8,0.8))

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.h, cmap=cmap)
fig.colorbar(h)
roppy.mpl_util.landmask(g.mask_rho, (0.6, 0.8, 0.0))

# Plot initial particle distribution
X, Y, tstring = read(0)
h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(tstring)

# Do the animation
fig.canvas.manager.window.after(100, animate)

# Show the results
plt.axis('image')
plt.show()

