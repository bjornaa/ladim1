# Not working
# Follow https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
# Do a simpler example first


import time
import itertools
# import matplotlib; matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import animation
from netCDF4 import Dataset
# import roppy
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

# ----------------

# ROMS grid, plot domain

# Slight overkill to use roppy, could be more stand alone
f0 = Dataset(grid_file)
g = roppy.SGrid(f0, subgrid=(i0, i1, j0, j1))

# particle_file
pf = ParticleFile(particle_file)

Ntimes = pf.num_times


def animate(i):
    # for t in range(1, Ntimes):
    for t in itertools.count():
        t = (t + 1) % Ntimes
        if t == 0:
            time.sleep(0.5)
        X, Y = pf.position(t)
        # timestring = pf.time(t)
        h[0].set_xdata(X)
        h[0].set_ydata(Y)
        # ax.set_title(timestring)
        return h,

# Create a figure

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)

# Make background map
cmap = plt.get_cmap('Blues')
h = ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g, (0.6, 0.8, 0.0))
h = ax.plot([], [], '.', color='red', markeredgewidth=0, lw=0.5)

def init():

    # Plot initial particle distribution
    X, Y = pf.position(0)
    # timestring = pf.time(0)
    # noinspection PyRedeclaration
    h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
    # ax.set_title(timestring)
    return h,

# Do the animation
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=20, blit=True)
# Show the results
plt.axis('image')
plt.axis((i0+1, i1-1, j0+1, j1-1))
plt.show()
