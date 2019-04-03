import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from postladim import ParticleFile
from gridforce_analytic import Grid

# Particle file
particle_file = "obstacle.nc"

# Get the grid information
grid = Grid(None)

imax, jmax = grid.imax, grid.jmax
# L = grid.L
R = grid.R
X0 = grid.X0

# particle_file
pf = ParticleFile(particle_file)
num_times = pf.num_times

# Set up the plot area
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(xlim=(0, imax), ylim=(0, jmax), aspect="equal")

# Plot the semicircular obstacle
circle = plt.Circle((X0, 0), R, color="g")
ax.add_artist(circle)

# Plot initial particle distribution
X, Y = pf.position(0)
particle_dist, = ax.plot(X, Y, ".", color="red", markeredgewidth=0.5, lw=0.5)
# title = ax.set_title(pf.time(0))
time0 = pf.time(0)  # Save start-time
timestr = "00:00"
timestamp = ax.text(0.02, 0.93, timestr, fontsize=16, transform=ax.transAxes)


# Update function
def animate(t):
    X, Y = pf.position(t)
    particle_dist.set_data(X, Y)
    # Time since start in minutes
    dtime = int((pf.time(t) - time0).total_seconds() / 60)
    # Format hh:mm
    dtimestr = "{:02d}:{:02d}".format(*divmod(dtime, 60))
    timestamp.set_text(dtimestr)
    return particle_dist, timestamp


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

# anim.save("obstacle.mp4")

plt.show()
