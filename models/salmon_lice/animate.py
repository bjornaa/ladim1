# import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from netCDF4 import Dataset
from postladim.particlefile import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = 'out.nc'
grid_file = '/scratch/Data/NK800/file_0000.nc'

# Subdomain specification
i0, i1 = 320, 500
j0, j1 = 500, 680

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


farmid = pf['farmid']

# Plot initial particle distribution
X, Y = pf.position(0)
pid = pf['pid', 0]
X1 = X[farmid[pid]==10041]
Y1 = Y[farmid[pid]==10041]
X2 = X[farmid[pid]==10054]
Y2 = Y[farmid[pid]==10054]
particle_dist1, = ax.plot(X1, Y1, '.', color='red', markeredgewidth=0, lw=0.5)
particle_dist2, = ax.plot(X2, Y2, '.', color='blue', markeredgewidth=0, lw=0.5)
# title = ax.set_title(pf.time(0))
timestamp = ax.text(0.01, 0.97, pf.time(0), fontsize=15,
                    transform=ax.transAxes)

# Save the start positions
Xa, Ya = X[0], Y[0]
Xb, Yb = X[-1], Y[-1]
start, = ax.plot([Xa, Xb], [Ya, Yb], 'o', color='black', markersize=18)


# Update function
def animate(t):
    X, Y = pf.position(t)
    pid = pf['pid', t]
    X1 = X[farmid[pid]==10041]
    Y1 = Y[farmid[pid]==10041]
    X2 = X[farmid[pid]==10054]
    Y2 = Y[farmid[pid]==10054]
    particle_dist1.set_data(X1, Y1)
    particle_dist2.set_data(X2, Y2)
    timestamp.set_text(pf.time(t))
    # ax.plot([Xa, Xb], [Ya, Yb], 'o', color='black', markersize=23, zorder=-8)
    return particle_dist1, particle_dist2, timestamp

# Do the animation
anim = FuncAnimation(fig, animate, frames=num_times, interval=20,
                     repeat=True, repeat_delay=500, blit=True)

plt.show()
