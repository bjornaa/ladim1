import time
import itertools
import matplotlib; matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from netCDF4 import Dataset
# import roppy
import roppy.mpl_util
from postladim.particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = 'station.nc'
grid_file = '../data/ocean_avg_0014.nc'

# Subgrid definition
i0, i1 = 100, 135
j0, j1 = 85, 110

# ----------------

# ROMS grid, plot domain

# Slight overkill to use roppy, could be more stand alone
f0 = Dataset(grid_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))

# particle_file
pf = ParticleFile(particle_file)

Ntimes = pf.ntimes


def animate():
    # for t in range(1, Ntimes):
    for t in itertools.count():
        t = (t + 1) % Ntimes
        if t == 0:
            time.sleep(0.5)
        X, Y = pf.get_position(t)
        timestring = pf.get_time(t)
        h[0].set_xdata(X)
        h[0].set_ydata(Y)
        ax.set_title(timestring)
        fig.canvas.draw()

# Create a figure

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g, (0.6, 0.8, 0.0))

# Plot initial particle distribution
X, Y = pf.get_position(0)
timestring = pf.get_time(0)
h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(timestring)

# Do the animation
fig.canvas.manager.window.after(100, animate)

# Show the results
plt.axis('image')
plt.axis((i0+1, i1-1, j0+1, j1-1))
plt.show()
