# import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
# from netCDF4 import Dataset
from postladim.particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = 'obstacle.nc'

# ----------------

imax, jmax = 100, 50
km = 1000
L = imax*km
W = jmax*km
R = 0.32
X0 = 0.5*imax

# Cell centers and boundaries
# Xcell = np.arange(0, imax+1)
# Ycell = np.arange(1, jmax)
# Xb = np.arange(0.5, i1)
# Yb = np.arange(j0-0.5, j1)

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(xlim=(0, imax), ylim=(0, jmax), aspect='equal')

# Background bathymetry
# cmap = plt.get_cmap('Blues')
# ax.contourf(Xcell, Ycell, H, cmap=cmap, alpha=0.3)

# Landmask
# constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
# M = np.ma.masked_where(M > 0, M)
# plt.pcolormesh(Xb, Yb, M, cmap=constmap)
circle = plt.Circle((X0, 0), R*jmax, color='g')
ax.add_artist(circle)


# Plot initial particle distribution
X, Y = pf.position(0)
particle_dist, = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
# title = ax.set_title(pf.time(0))
timestamp = ax.text(0.02, 0.93, pf.time(0), fontsize=16,
                    transform=ax.transAxes)


# Update function
def animate(t):
    X, Y = pf.position(t)
    particle_dist.set_data(X, Y)
    timestamp.set_text(pf.time(t))
    return particle_dist, timestamp

# Do the animation
anim = FuncAnimation(fig, animate, frames=num_times, interval=20,
                     repeat=True, repeat_delay=500, blit=True)

plt.show()
