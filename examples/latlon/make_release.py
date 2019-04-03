# Make a release file with position in longitude/latitude.
# Instantaneous release along the 59 degN parallel.

import numpy as np
from netCDF4 import Dataset
from ladim.gridforce.ROMS import Grid

# End points of line, lon, lat
lon0, lat0 = -2.5, 59.0
lon1, lat1 = 5.2, 59.0

# Number of particles along the line
Npart = 500

# Constant particle depth
Z = 5

# Geographical positions along line
lons = np.linspace(lon0, lon1, Npart)
lats = np.linspace(lat0, lat1, Npart)

# Write the release file
with open("latlon.rls", mode="w") as f:
    for (lon, lat) in zip(lons, lats):
        f.write(f"1989-05-24T12 {lon:8.5f} {lat:8.5f} {Z:4.1f}\n")
