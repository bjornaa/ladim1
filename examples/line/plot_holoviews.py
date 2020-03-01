# Use holoviews to plot the particle distribution at given time

from pathlib import Path
import numpy as np
import xarray as xr
import holoviews as hv
from postladim import ParticleFile

hv.extension("bokeh")

# --- Settings ---
tstep = 40   # Time step to show
# Output file (and type)
output_file = "line_hv.png"
#output_file = "line_hv.html"
scale = 5   # Figure size factor

# --- Data files ---

ladim_dir = Path("../../")
grid_file = ladim_dir / "examples/data/ocean_avg_0014.nc"
particle_file = ladim_dir / "examples/line/line.nc"

# --- Read particle data ---

pf = ParticleFile(particle_file)
X, Y = pf.position(tstep)

# --- Background bathymetry data ---

# Read bathymetry and land mask
with xr.open_dataset(grid_file) as A:
    H = A.h
    M = A.mask_rho
jmax, imax = M.shape
H = H.where(M > 0)  # Mask out land
M = M.where(M < 1)  # Mask out sea

# --- Holoviews elements ---

# Land image
land = hv.Image(data=M, kdims=["xi_rho", "eta_rho"], group="Land")

# Bathymetry image
topo = hv.Image(data=-np.log10(H), kdims=["xi_rho", "eta_rho"], group="Topo")

# Particle distribution
spread = hv.Scatter(data=(X, Y))

# Overlay
h = topo * land * spread

# --- Plot options ---

h.opts(frame_width=scale * imax, frame_height=scale * jmax)
h.opts("Scatter", color="red")
h.opts("Image.Topo", cmap="blues_r", alpha=0.7)
h.opts("Image.Land", cmap=["#80B040"])

# --- Save output ---

if output_file.endswith("png"):
    h.opts(toolbar=None)
hv.save(h, filename=output_file)
