# import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from netCDF4 import Dataset
from postladim import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = 'streak.nc'
grid_file = '../data/ocean_avg_0014.nc'

# Subgrid definition
i0, i1 = 100, 140
j0, j1 = 85, 130

# ----------------

# ROMS grid, plot domain
with Dataset(grid_file) as f0:
    H = f0.variables['h'][j0:j1, i0:i1]
    M = f0.variables['mask_rho'][j0:j1, i0:i1]
    lon = f0.variables['lon_rho'][j0:j1, i0:i1]
    lat = f0.variables['lat_rho'][j0:j1, i0:i1]

# Cell centers and boundaries
Xcell = np.arange(i0, i1)
Ycell = np.arange(j0, j1)
Xb = np.arange(i0-0.5, i1)
Yb = np.arange(j0-0.5, j1)

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 10))
ax = plt.axes(xlim=(i0+1, i1-1), ylim=(j0+1, j1-1), aspect='equal')

# Background bathymetry
cmap = plt.get_cmap('Blues')
ax.contourf(Xcell, Ycell, H, cmap=cmap, alpha=0.3)

# Lon/lat lines
ax.contour(Xcell, Ycell, lat, levels=range(57, 64),
           colors='black', linestyles=':')
ax.contour(Xcell, Ycell, lon, levels=range(-4, 10, 2),
           colors='black', linestyles=':')

# Landmask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(M > 0, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

# Scatter plot, colour = particle age
X, Y = pf.position(0)
pids = pf['pid'][0]
C = pf['release_time'][pids]/86400  # release time, reverse to get age
vmax = pf.num_times / 24   # Maximun particle age in days
pdistr = ax.scatter(
    X, Y, c=C[::-1], vmin=0, vmax=vmax, cmap=plt.get_cmap('plasma_r'))
cb = plt.colorbar(pdistr)
cb.set_label('Particle age [days]', fontsize=14)
timestamp = ax.text(0.01, 0.97, pf.time(0), fontsize=15,
                    transform=ax.transAxes)


# Update function
def animate(t):
    X, Y = pf.position(t)
    pdistr.set_offsets(np.vstack((X,Y)).T)
    C = pf['release_time'][pf['pid'][t]] / 86400.0
    pdistr.set_array(C[::-1])
    timestamp.set_text(pf.time(t))
    return pdistr, timestamp


# Do the animation
anim = FuncAnimation(fig, animate, frames=num_times, interval=20,
                     repeat=True, repeat_delay=500, blit=True)

plt.show()
