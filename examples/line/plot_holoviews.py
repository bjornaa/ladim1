# Use holoviews to plot the particle distribution at given time

from pathlib import Path
import numpy as np
import xarray as xr
import holoviews as hv
import cmocean
from postladim import ParticleFile

hv.extension("bokeh")

# --- Settings ---

tstep = 40  # Time step to show
# Output file (and type)
output_file = "line_hv.png"
# output_file = "line_hv.html"
scale = 5  # Figure size factor

# --- Data files ---

ladim_dir = Path("../../")
grid_file = ladim_dir / "examples/data/ocean_avg_0014.nc"
particle_file = ladim_dir / "examples/line/line.nc"

# --- Particle data ---

with ParticleFile(particle_file) as pf:
    XY = pf.position(tstep)

# --- Background bathymetry data ---

# Read bathymetry and land mask
with xr.open_dataset(grid_file) as ds:
    H = ds.h  # Bottom topography
    M = ds.mask_rho  # Land mask
jmax, imax = M.shape
H = H.where(M > 0)  # Mask out land
M = M.where(M < 1)  # Mask out sea

# --- Holoviews elements ---

# Land image
land = hv.Image(data=M, kdims=["xi_rho", "eta_rho"], group="Land")

# Bathymetry image
# Take logarithm to show details in the shallow North Sea
topo = hv.Image(data=np.log10(H), kdims=["xi_rho", "eta_rho"], group="Topo")

# Particle distribution
spread = hv.Points(data=XY)

# Overlay
h = topo * land * spread

# --- Plot options ---

h.opts(frame_width=int(scale * imax), frame_height=int(scale * jmax))
h.opts("Points", size=2, color="red")
h.opts("Image.Topo", cmap="blues", alpha=0.7)
h.opts("Image.Land", cmap=["#80B040"])

# --- Save output ---

if output_file.endswith("png"):
    h.opts(toolbar=None)
hv.save(h, filename=output_file)
