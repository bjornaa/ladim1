# import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from postladim import ParticleFile
from nested_gridforce import Grid

# ---------------
# User settings
# ---------------

# Files
particle_file = "nested.nc"


# Define the grids
g = Grid(dict(grid_args=[]))

I, J = np.meshgrid(np.arange(g.imax), np.arange(g.jmax))
I = I.ravel()
J = J.ravel()

H = g.sample_depth(I, J)
M = g.onland(I, J)

H = H.reshape((g.jmax, g.imax))
M = M.reshape((g.jmax, g.imax))

# Cell centers and boundaries
Xcell = np.arange(0, g.imax)
Ycell = np.arange(0, g.jmax)
Xb = np.arange(0.5, g.imax)
Yb = np.arange(0.5, g.jmax)

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 10))
ax = plt.axes(aspect="equal")

# Background bathymetry
cmap = plt.get_cmap("Blues")
ax.contourf(Xcell, Ycell, H, cmap=cmap, alpha=0.3)

# Lon/lat lines
# ax.contour(Xcell, Ycell, lat, levels=range(54, 61),
#           colors='black', linestyles=':')
# ax.contour(Xcell, Ycell, lon, levels=range(0, 14, 2),
#           colors='black', linestyles=':')

# Landmask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(~M, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

# Plot border of fine subgrid
x0, y0 = 55, 12  # Not easy to get from nested_gridforce
x1 = x0 + g.fine_grid.imax
y1 = y0 + g.fine_grid.jmax
plt.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color="black")

# Plot initial particle distribution
X, Y = pf.position(0)
particle_dist, = ax.plot(X, Y, ".", color="red", markeredgewidth=0, lw=0.5)
# title = ax.set_title(pf.time(0))
timestamp = ax.text(0.01, 0.97, pf.time(0), fontsize=15, transform=ax.transAxes)


# Update function
def animate(t):
    X, Y = pf.position(t)
    particle_dist.set_data(X, Y)
    timestamp.set_text(pf.time(t))
    return particle_dist, timestamp


anim_running = True


def onClick(event):
    global anim_running
    if anim_running:
        anim.event_source.stop()
        anim_running = False
    else:
        anim.event_source.start()
        anim_running = True


# Do the animation
anim = FuncAnimation(
    fig,
    animate,
    frames=num_times,
    interval=20,
    repeat=True,
    repeat_delay=500,
    blit=True,
)

fig.canvas.mpl_connect("button_press_event", onClick)

plt.show()
