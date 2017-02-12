import time
# import itertools
# import matplotlib; matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import animation
from netCDF4 import Dataset
import roppy
import roppy.mpl_util
from postladim.particlefile import ParticleFile


# PROBLEM, timestring is not updated

# ---------------
# User settings
# ---------------

# Files
particle_file = 'line.nc'
grid_file = '../data/ocean_avg_0014.nc'

# Subgrid definition
i0, i1 = 58, 150
j0, j1 = 60, 140

# ----------------

# ROMS grid, plot domain

# Slight overkill to use roppy, could be more stand alone
f0 = Dataset(grid_file)
g = roppy.SGrid(f0, subgrid=(i0+1, i1, j0+1, j1))

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

fig = plt.figure(figsize=(12, 10))
ax = plt.axes(xlim=(i0+1, i1-1), ylim=(j0+1, j1-1), aspect='equal')
# Make background map
cmap = plt.get_cmap('Blues')
ax.contourf(g.X, g.Y, g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g, (0.6, 0.8, 0.0))
ax.contour(g.X, g.Y, g.lat_rho, levels=range(57, 64),
           colors='black', linestyles=':')
ax.contour(g.X, g.Y, g.lon_rho, levels=range(-4, 10, 2),
           colors='black', linestyles=':')


# Plot initial particle distribution
X, Y = pf.position(0)
# timestring = pf.time(0)
# noinspection PyRedeclaration

h, = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
h1 = ax.set_title(pf.time(0))


# Show the results
# plt.axis('image')
# plt.axis((i0+1, i1-1, j0+1, j1-1))


# initialization function: plot the background of each frame
def init():
    # h.set_data(X, Y)
    return h, h1


def animate(t):
    i = t % num_times
    if i == 0:
        time.sleep(0.5)
    X, Y = pf.position(i)
    h.set_data(X, Y)
    h1.set_text(pf.time(i))
    return h, h1

# Can have more general argument for frames
# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=2000, interval=20, blit=True)


plt.show()
