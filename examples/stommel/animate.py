import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from postladim import ParticleFile
from gridforce_stommel import Grid, Forcing

km = 1000.0

# Particle file
particle_file = "stommel.nc"

# Get the grid information
grid = Grid(None)
force = Forcing(None, grid)

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(xlim=(0, grid.xmax / km), ylim=(0, grid.ymax / km), aspect="equal")
plt.xlabel("km")
plt.ylabel("km")



# Stream function
G = force.G
b = force.b
p = force.p
q = force.q
A = force.A
B = force.B
dx = grid.dx
I = np.arange(grid.imax) * grid.dx
J = np.arange(grid.jmax) * grid.dx
JJ, II = np.meshgrid(I, J)
psi = G * np.sin(np.pi * II / b) * (p * np.exp(A * JJ) + q * np.exp(B * JJ) - 1)

km = 1000
# Plot stream function background
plt.contourf(I / km, J / km, psi, alpha=0.3)
plt.contour(I / km, J / km, psi, colors="black", linewidths=0.5, alpha=0.3)
# Plot initial particle distribution
X, Y = pf.position(0)
particle_dist, = ax.plot(X / km, Y / km, ".", color="red", markeredgewidth=0.5, lw=0.5)
# title = ax.set_title(pf.time(0))
time0 = pf.time(0)  # Save start time
timestr = "0 days"
timestamp = ax.text(
    0.97,
    0.93,
    timestr,
    fontsize=16,
    horizontalalignment="right",
    transform=ax.transAxes,
)


# Update function
def animate(t):
    X, Y = pf.position(t)
    particle_dist.set_data(X / km, Y / km)
    # Time since start in minutes
    days = int((pf.time(t) - time0) / np.timedelta64(1, "D"))
    dtimestr = f"{days} days"
    timestamp.set_text(dtimestr)
    return particle_dist, timestamp


# Do the animation
anim = FuncAnimation(
    fig, animate, frames=num_times, interval=0, repeat=True, repeat_delay=500, blit=True
)

# anim.save("stommel.mp4")

plt.show()
