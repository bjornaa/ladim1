# import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from postladim.particlefile import ParticleFile
from gridforce_discrete import Grid

# Input file
particle_file = 'obstacle.nc'

# Get the grid information
grid = Grid()

# Open the particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(xlim=(0, grid.imax), ylim=(0, grid.jmax), aspect='equal')

# Landmask
Xb = np.arange(-0.5, grid.imax)
Yb = np.arange(-0.5, grid.jmax)
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(grid.M > 0, grid.M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)
# Draw the cirular boundary
T = np.linspace(0, np.pi)
plt.plot(grid.X0 + grid.R*np.cos(T), grid.R*np.sin(T), color='black', )

# Plot initial particle distribution
X, Y = pf.position(0)
particle_dist, = ax.plot(X, Y, '.', color='red', markeredgewidth=0.5, lw=0.5)
time0 = pf.time(0)   # Save start-time
timestr = "00:00"
timestamp = ax.text(0.02, 0.93, timestr, fontsize=16,
                    transform=ax.transAxes)


# Update function
def animate(t):
    X, Y = pf.position(t)
    particle_dist.set_data(X, Y)
    # Time since start in minutes
    dtime = int((pf.time(t)-time0).total_seconds() / 60)
    # Format hh:mm
    dtimestr = "{:02d}:{:02d}".format(*divmod(dtime, 60))
    timestamp.set_text(dtimestr)
    return particle_dist, timestamp


# Do the animation
anim = FuncAnimation(fig, animate, frames=num_times, interval=20,
                     repeat=True, repeat_delay=500, blit=True)

plt.show()
