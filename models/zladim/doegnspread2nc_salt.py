# Compute a particle concentration
# and save as netCDF

from __future__ import print_function

# import os
# import glob
import datetime
import numpy as np
# from numpy import array, log10, mean, median
from netCDF4 import Dataset
from postladim import ParticleFile

# ----------------
# User settings
# ----------------

gridfile = "/nethome/laksemod/anne/norkyst_800m_grid_full_WGS84.nc"

fil = "/nethome/laksemod/anne/out.nc"
print("LADiM output fil:", fil)

output_file = "Lus_2016_1apr_anlegg-0100-0150.nc"

# Grid mapping
# xp, yp, dx, ylon = 3991.0, 2230.0, 800.0, 70.0   #  Lus WGS84

# Min, max day-degrees to consider
ddmin, ddmax = 40, 170

# Antal døgn
dogn = 40

# z_release = []

# Open the particle file
pf = ParticleFile(fil)

# -----------------------------
# Particle release positions
# -----------------------------

# Release positions:
# x_release = pf.variables['X'][0]
# y_release


# N_release = len(z_release)
print('Utsleppspunkt ok...')

# ----------------
# Read grid file
# ----------------

f = Dataset(gridfile)
print('gridfile')
H = f.variables['h'][:, :]
M = f.variables['mask_rho'][:, :]
lon = f.variables['lon_rho'][:, :]
lat = f.variables['lat_rho'][:, :]
f.close()
print('Gridfile ok...')

jmax, imax = H.shape

# --------------------------
# Define output NetCDF file
# --------------------------

nc = Dataset(output_file, mode='w', format='NETCDF3_CLASSIC')

# Dimensions
nc.createDimension('xi_rho',  imax)
nc.createDimension('eta_rho', jmax)
# nc.createDimension('release_locations', N_release)
nc.createDimension('time', None)

# Variables
v = nc.createVariable('conc', 'f', ('time', 'eta_rho', 'xi_rho'))
v.long_name = "Particle concentration"
v.units = "number of particles in grid cell"

v = nc.createVariable('lon', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Longitude"
v.units = "degrees east"

v = nc.createVariable('lat', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Latitude"
v.units = "degrees north"

# v = nc.createVariable('release_y', 'f', ('release_locations',))
# v.long_name = "longitude y pos of particle release"
# v.units = "degrees east"

# v = nc.createVariable('release_x', 'f', ('release_locations',))
# v.long_name = "latitude of particle release"
# v.units = "degrees east"

# v = nc.createVariable('release_depth', 'f', ('release_locations',))
# v.long_name = "depth of particle release"
# v.units = "meter"
print('Variabler ok...')

# Global variables
nc.institution = "Institute of Marine Research"
nc.grid_file = gridfile
nc.history = "Created %s by timespread2nc.py" % datetime.date.today()

# ------------------
# Save variables
# ------------------

nc.variables['lon'][:, :] = lon
nc.variables['lat'][:, :] = lat

# nc.variables['release_y'][:] = lon_release
# nc.variables['release_x'][:] = lat_release
# nc.variables['release_depth'][:] = z_release
print('Faste variable lagret...')

# for d in range(dogn):
for d in range(dogn):
    print(d, ' av ', dogn)
    # ---------------------
    # Read particle files
    # ---------------------
    C = np.zeros((jmax, imax))
    # pf = Dataset(fil)

    times = pf.nc.variables['time'][:]/86400
    # pstart = pf.particle
    # pcount = pf.variables['pCount'][:]

    tind, = np.nonzero((d <= times) & (times < d+1))
    # time_slice = slice(, pstart[tind[-1]]+pcount[tind[-1]])
    t0 = tind[0]
    t1 = tind[-1] + 1
    print("   t0 t1 = ", t0, t1)
    time_slice = slice(t0, t1)

    x = pf.variables['X'][t0:t1]
    print("  ", x.min(), x.max())
    y = pf.variables['Y'][t0:t1]
    age = pf.variables['age'][t0:t1]  # day-degrees
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

    nc.variables['conc'][d, :, :] = C
    # print "Max conc : ", np.amax(sup)
    # print "Min conc : ", np.amin(sup)

# ------------------
# CLEAN UP
# ------------------

nc.close()
