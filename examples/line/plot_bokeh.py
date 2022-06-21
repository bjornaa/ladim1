# Use holoviews to plot the particle distribution at given time

from pathlib import Path
import numpy as np
from netCDF4 import Dataset
import bokeh
from bokeh.plotting import figure
from postladim import ParticleFile

# --- Settings ---

tstep = 40  # Time step to show
# Output file (and type)
outfile = "line_bokeh.png"
# outfile = "line_bokeh.html"
scale = 3  # Figure size factor

# --- Data files ---

ladim_dir = Path("../../")
grid_file = ladim_dir / "examples/data/ocean_avg_0014.nc"
particle_file = ladim_dir / "examples/line/line.nc"

# --- Read particle data ---

pf = ParticleFile(particle_file)
X = pf.X[tstep].values
Y = pf.Y[tstep].values

# --- Background bathymetry data ---

# Read bathymetry and land mask
with Dataset(grid_file) as f:
    H = f.variables["h"][:, :]
    M = f.variables["mask_rho"][:, :]
jmax, imax = M.shape
H[M < 1] = np.nan  # Mask out land

# --- Plot ---

# Figure
p = figure(
    frame_width=int(scale * imax),
    frame_height=int(scale * jmax),
    x_range=(-0.5, imax - 0.5),
    y_range=(-0.5, jmax - 0.5),
)

# Background bathymetry
#   Take logarithm to show details in shallow part,
#   Minus to make colours darker with increasing depth
p.image(
    image=[-np.log(H)], x=-0.5, y=-0.5, dw=imax, dh=jmax, palette="Blues8", alpha=0.7
)

# Particle distribution
p.circle(X, Y, size=2, color="red", alpha=0.5)

# --- Save output ---

if outfile.endswith("png"):
    p.toolbar_location = None
    bokeh.io.export_png(p, outfile)
else:
    bokeh.io.save(p, filename=outfile, title="", resources=bokeh.resources.CDN)
