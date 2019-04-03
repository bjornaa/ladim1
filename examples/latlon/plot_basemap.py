import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

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

# Polarstereographic projection, northern North Sea
m = Basemap(
    projection="stere",
    resolution="i",
    llcrnrlon=lon0,
    llcrnrlat=lat0,
    urcrnrlon=lon1,
    urcrnrlat=lat1,
    lon_0=0.5 * (lon0 + lon1),
    lat_0=90,
)

# Land
m.drawcoastlines()
m.fillcontinents(color="Khaki")

# Minor graticule
m.drawparallels(
    np.arange(lat0, lat1 + 1), color="grey", labels=[True, False, False, False]
)
m.drawmeridians(
    np.arange(lon0, lon1, 2), color="grey", labels=[False, False, False, True]
)
# Major graticule
m.drawparallels([55, 60], dashes=[2000, 1], color="black")
m.drawmeridians([0, 10], dashes=[2000, 1], color="black")

# ---------------------
# Plot the particles
# ---------------------
m.plot(lon, lat, "o", color="red", latlon=True)

plt.show()
