# Compute a particle concentration
# and save as netCDF

from __future__ import print_function

import datetime
import numpy as np
from netCDF4 import Dataset
from postladim import ParticleFile

# ----------------
# User settings
# ----------------

gridfile = "/nethome/laksemod/anne/norkyst_800m_grid_full_WGS84.nc"

ladimfile = "/nethome/laksemod/anne/out.nc"
print("LADiM output file:", ladimfile)

concentration_file = "Lus_2016_1apr_anlegg-0100-0150.nc"

# Aggregation period (number of output time frames)
aggper = 24   # Daily given hourly output from LADiM

# Min, max day-degrees to consider
ddmin, ddmax = 40, 170

# ----------------
# Read grid file
# ----------------

with Dataset(gridfile) as f:
    H = f.variables['h'][:, :]
    M = f.variables['mask_rho'][:, :]
    lon = f.variables['lon_rho'][:, :]
    lat = f.variables['lat_rho'][:, :]
jmax, imax = H.shape
# ---------------------------
# Open the particle file
# ---------------------------

pf = ParticleFile(ladimfile)

# --------------------------
# Define output NetCDF file
# --------------------------

nc = Dataset(concentration_file, mode='w', format='NETCDF3_CLASSIC')

# Dimensions
nc.createDimension('xi_rho',  imax)
nc.createDimension('eta_rho', jmax)
nc.createDimension('time', None)

# Variables
v = nc.createVariable('time', 'd', ('time',))
v.standard_name = 'Time'
v.units = pf.nc.variables['time'].units

v = nc.createVariable('conc', 'f', ('time', 'eta_rho', 'xi_rho'))
v.long_name = "Particle concentration"
v.units = "aggregated number of particles in grid cell"

v = nc.createVariable('lon', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Longitude"
v.units = "degrees east"

v = nc.createVariable('lat', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Latitude"
v.units = "degrees north"

# Global variables
nc.institution = "Institute of Marine Research"
nc.grid_file = gridfile
nc.ladim_output = ladimfile
nc.history = "Created {:s} by aggregate_concentration.py".format(
    datetime.date.today())

# ---------------------
# Save fixed variables
# ---------------------

nc.variables['lon'][:, :] = lon
nc.variables['lat'][:, :] = lat


# Set up time loop
Ntimes = pf.num_times           # Time steps in LADiM file
Nagg = pf.num_times // aggper   # Number of whole aggregation periods

agg_times = list(range(Nagg))   # Aggregation time frames

for n in agg_times:
    print("Aggregation period nr: {:3d} /{:3d}".format(n, Nagg))

    C = np.zeros((jmax, imax))

    # Get time slice
    time_slice = slice(n*aggper, (n+1)*aggper)

    # Mean time in agg period
    atime = np.sum(pf.nc.variables['time'][time_slice]) / aggper

    x = pf.variables['X'][time_slice]
    y = pf.variables['Y'][time_slice]
    age = pf.variables['age'][time_slice]  # day-degrees
    sup = pf.variables['super'][time_slice]
    # salt = pf.variables['salt'][time_slice]
    # temp = pf.variables['temp'][time_slice]
    z = pf.variables['Z'][time_slice]
    # print("Salt : min, max = ", salt.min(), salt.max())
    # print("Temp : min, max = ", temp.min(), temp.max())
    # print("Z : min, median = ", z.min(), median(z))
    # pf.close()

    # Get positions of particles considered
    # I = (ddmin <= age) & (age < ddmax) & (salt > 20) & (z > -2)
    I = (ddmin <= age) & (age < ddmax)
    x = x[I]
    y = y[I]
    sup = sup[I]

    # ------------------------
    # Count particles
    # ------------------------
    # Uses histogram2d for computational speed
    if len(x) > 1:
        cb, Xb, Yb = np.histogram2d(
            y, x, (jmax, imax),
            range=[[-0.5, jmax-0.5], [-0.5, imax-0.5]],
            weights=sup, normed=False)
        C = C + cb

    # ----------------
    # Save to file
    # ----------------

    nc.variables['time'][n] = atime
    nc.variables['conc'][n, :, :] = C

# ------------------
# Clean up
# ------------------

nc.close()
pf.close()
