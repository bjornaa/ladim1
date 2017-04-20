# Compute a particle concentration
# and save as netCDF

import datetime
import numpy as np
from netCDF4 import Dataset
from postladim import ParticleFile
# import gridmap

# ----------------
# User settings
# ----------------


particle_file = '/hexagon/vol1/bjorn_rhea/out.nc'
grid_file = '/data/model_data006/anneds/Lusedata/Gridfiler/norkyst_800m_grid_full.nc'

output_file = "c2.nc"

# Min, max day-degrees to consider
ddmin, ddmax = 50, 150

# First/last day to consider
date0 = datetime.datetime(2017, 3, 1)
date1 = datetime.datetime(2017, 3, 11)
# date1 = datetime.datetime(2017, 3, 1)


# ----------------
# Read grid file
# ----------------

f = Dataset(grid_file)
H = f.variables['h'][:,:]
M = f.variables['mask_rho'][:,:]
lon = f.variables['lon_rho'][:,:]
lat = f.variables['lat_rho'][:,:]
f.close()

jmax, imax = H.shape

# ---------------------
# Read particle file
# ---------------------

pf = ParticleFile(particle_file)

# Find record numbers

n0 = -99
# n1 = -99
for n in range(pf.num_times):
    if pf.time(n) < date0:
        continue
    if n0 < 0:   # First time
        n0 = n
        n1 = n
    if pf.time(n) < date1:
        n1 = n

print("start: ", n0, pf.time(n0))
print("stop : ", n1, pf.time(n1))

C = np.zeros((jmax, imax))
for n in range(n0, n1+1):
    print(n)
    X0, Y0 = pf.position(n)
    S0 = pf['super', n]
    A = pf['age', n]
    I = (ddmin <= A) & (A < ddmax)
    C0, Yb, Xb = np.histogram2d(
        Y0[I], X0[I], weights=S0[I],
        bins=(jmax, imax),
        range=[[-0.5,jmax-0.5], [-0.5,imax-0.5]])
    C += C0


# pf.close()

C = C / (n1 + 1 - n0)

# --------------------------
# Define output NetCDF file
# --------------------------

nc = Dataset(output_file, mode='w',
             format='NETCDF3_CLASSIC')

# Dimensions
nc.createDimension('xi_rho',  imax)
nc.createDimension('eta_rho', jmax)
# nc.createDimension('release_locations', N_release)


# Variables
v = nc.createVariable('conc', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Particle concentration"
v.units = "number of particles in grid cell"

# Global variables
nc.institution = "Institute of Marine Research"
nc.grid_file = grid_file
nc.particle_file = particle_file
nc.history = "Created %s by spreading2nc.py" %  datetime.date.today()

# ------------------
# Save variables
# ------------------

nc.variables['conc'][:,:] = C


# -------------
# Clean up
# -------------

nc.close()
