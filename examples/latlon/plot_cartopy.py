import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
#from roppy.mpl_util import LevelColormap

from postladim import ParticleFile

# ---------------
# User settings
# ---------------

# Files
particle_file = "latlon.nc"

# time step to plot
t = 90

# Geographical extent
lon0, lat0, lon1, lat1 = -6, 54, 12, 62

# --------------------
# Read particle_file
# --------------------

with ParticleFile(particle_file) as pf:
    lon = pf["lon"][t]
    lat = pf["lat"][t]

# -------------------------
# Make background map
# -------------------------

lonlat = ccrs.PlateCarree()
proj = ccrs.NorthPolarStereo(central_longitude=0.5 * (lon0 + lon1))
ax = plt.axes(projection=proj)
eps = 0.06 * (lat1 - lat0)  # Extend slightly southwards
ax.set_extent([lon0, lon1, lat0 - eps, lat1], lonlat)

# Set up the wedge-shaped boundary
south = proj.transform_points(
    lonlat, np.linspace(lon0, lon1, 100), np.array(100 * [lat0])
)
north = proj.transform_points(
    lonlat, np.linspace(lon1, lon0, 100), np.array(100 * [lat1])
)
boundary = np.vstack((north[:, :2], south[:, :2]))
ax.set_boundary(Path(boundary), transform=proj)

# --- Add land feature
ax.add_feature(cfeature.GSHHSFeature(scale="i"), facecolor="Khaki")

# --- Add graticule
ax.gridlines(xlocs=range(lon0, lon1 + 2, 2), ylocs=range(lat0, lat1 + 1))

# ---------------------
# Plot the particles
# ---------------------
ax.plot(lon, lat, "o", color="red", transform=lonlat)

plt.show()
