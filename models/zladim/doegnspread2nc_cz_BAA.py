# -*- coding: utf-8 -*-
# Compute a particle concentration
# and save as netCDF

import os
import glob
import datetime
import numpy as np
from numpy import array, log10, mean, median
from netCDF4 import Dataset
# import gridmap
# ----------------
# User settings
# ----------------

mnd="mar"
dag="11"

# Opr test kjøringer2015
gridfile = '/work/shared/norkyst/NorKyst-800m_Forcing/Grid/norkyst_800m_grid_full.nc'
partfile = '/work/anneds/czladim/czladim_opr_' + dag + mnd + '_40dager_2017.nc'

output_file = 'czladim_opr_' + dag + mnd + '_50_150.nc'

# anlegg = "all" eller liste av type [10264, 12727, ...]
# ett anlegg, bruk liste med ett element
anlegg = "all"
# anlegg = [22775]

dogn = 40  # 1. april til 1 August for 2014 NFD

# Min, max day-degrees to consider
ddmin, ddmax = 50, 150


# ---------------------------
# Håndter anleggsliste
# ---------------------------


pf = Dataset(partfile)

# All release areas, indexed by the pid
release_area = pf.variables['Release_area'][:]

if anlegg == "all":
    all_farms = True  # Can shortcut some tests later
    # N_farms = pf.variables['N_areas'].getValue()
    # Use set() to get the unique farms
    anlegg = list(set(release_area))
    # Remove unset value
    for a in anlegg:
        if a < 0:
            anlegg.remove(a)
    anlegg.sort()
    print "alle anlegg = ", len(anlegg)

else:
    all_farms = False
    anlegg = np.array(anlegg)
    print "anleggsnummere: ", anlegg

    # Finn de pid's som kommer fra anleggslisten
    fra_anlegg = np.in1d(release_area, anlegg)
    print "Laget from_framlist"


N_farms = len(anlegg)


# ----------------
# Read grid file
# ----------------

f = Dataset(gridfile)
H = f.variables['h'][:, :]
M = f.variables['mask_rho'][:, :]
lon = f.variables['lon_rho'][:, :]
lat = f.variables['lat_rho'][:, :]
f.close()
print 'Gridfile ok...'

jmax, imax = H.shape

# --------------------------
# Define output NetCDF file
# --------------------------

nc = Dataset(output_file, mode='w', format='NETCDF3_CLASSIC')

# Dimensions
nc.createDimension('xi_rho',  imax)
nc.createDimension('eta_rho', jmax)
nc.createDimension('release_area', N_farms)
nc.createDimension('time', None)

# Add coordinate variables

v = nc.createVariable('time', 'float64', ('time',))
v.standard_name = 'time'
v.units = pf.variables['Time'].units

v = nc.createVariable('xi_rho', 'float32', ('xi_rho',))
v.standard_name = "projection_x_coordinate"
v.units = "meter"

v = nc.createVariable('eta_rho', 'float32', ('eta_rho',))
v.standard_name = "projection_y_coordinate"
v.units = "meter"

v = nc.createVariable('release_area', 'i', ('release_area',))
v.long_name = "Fish farm identifier"


v = nc.createVariable('conc', 'f', ('time', 'eta_rho', 'xi_rho'))
v.long_name = "Particle concentration"
v.units = "number of particles in grid cell"
v.coordinates = "lon lat"
v.grid_mapping = "grid_mapping"


v = nc.createVariable('lon', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Longitude"
v.units = "degrees east"

v = nc.createVariable('lat', 'f', ('eta_rho', 'xi_rho'))
v.long_name = "Latitude"
v.units = "degrees north"

# Mapping variable
v = nc.createVariable('grid_mapping', 'i', ())
v.long_name = 'grid mapping'
v.grid_mapping_name = "polar_stereographic"
v.ellipsoid = "sphere"
v.earth_radius = 6371000.
v.latitude_of_projection_origin = 90.
v.straight_vertical_longitude_from_pole = 70.
v.standard_parallel = 60.
v.false_easting = 3192800.
v.false_northing = 1784000.
v.dx = 800.
v.proj4string = "+proj=stere +R=6371000.0 +lat_0=90 +lat_ts=60 +x_0=3192800.0 +y_0=1784000.0 +lon_0=70"


# v = nc.createVariable('release_y', 'f', ('release_locations',))
# v.long_name = "longitude y pos of particle release"
# v.units = "degrees east"
#
# v = nc.createVariable('release_x', 'f', ('release_locations',))
# v.long_name = "latitude of particle release"
# v.units = "degrees east"
#
# v = nc.createVariable('release_depth', 'f', ('release_locations',))
# v.long_name = "depth of particle release"
# v.units = "meter"
print 'Variabler ok...'

# Global variables
nc.institution = "Institute of Marine Research"
nc.grid_file = gridfile
nc.particle_file = partfile
nc.history = "Created %s by timespread2nc.py" % datetime.date.today()

# ------------------
# Save variables
# ------------------


# Coordinate variables
nc.variables['xi_rho'][:] = np.arange(len(nc.dimensions['xi_rho'])) * 800.0
nc.variables['eta_rho'][:] = np.arange(len(nc.dimensions['eta_rho'])) * 800.0


nc.variables['lon'][:, :] = lon
nc.variables['lat'][:, :] = lat

# nc.variables['release_y'][:] = lon_release
# nc.variables['release_x'][:] = lat_release
# nc.variables['release_depth'][:] = z_release

nc.variables['release_area'][:] = anlegg

print 'Faste variable lagret...'


times = pf.variables['Time'][:]
pstart = pf.variables['pStart'][:]
pcount = pf.variables['pCount'][:]

for d in range(dogn):
    # for d in range(1):

    print d, ' av ', dogn
    # ---------------------
    # Read particle files
    # ---------------------

    nc.variables['time'][d] = d
    C = np.zeros((jmax, imax))

    tind, = np.nonzero((d <= times) & (times < d + 1))
    time_slice = slice(pstart[tind[0]], pstart[tind[-1]] + pcount[tind[-1]])

    x = pf.variables['px'][time_slice]
    y = pf.variables['py'][time_slice]
    age = pf.variables['page'][time_slice]  # day-degrees
    print "max av age", max(age)
    sup = pf.variables['psuper'][time_slice]
    salt = pf.variables['psalt'][time_slice]
    temp = pf.variables['ptemp'][time_slice]
    z = pf.variables['pz'][time_slice]
    print "Anne Salt : min, max = ", salt.min(), salt.max()
    if all_farms:
        I = (ddmin <= age) & (age < ddmax)
    else:
        pid = pf.variables['pid'][time_slice]
        I = (ddmin <= age) & (age < ddmax) & (fra_anlegg[pid])

    x = x[I]
    y = y[I]
    sup = sup[I]
    salt = salt[I]
    temp = temp[I]
    z = z[I]
    if len(x) > 1:
        print " Time "
        print " Time Salt : min, max = ", salt.min(), salt.max()
        print " Time Temp : min, max = ", temp.min(), temp.max()
        print " Time pz : min, mean,median = ", z.min(), mean(z), median(z)

    # ------------------------
    # Count particles
    # ------------------------
    # Uses histogram2d for computational speed
    if len(x) > 1:
        cb, Xb, Yb = np.histogram2d(y, x, (jmax, imax),
                                    range=[[-0.5, jmax - 0.5],
                                           [-0.5, imax - 0.5]],
                                    weights=sup, normed=False)
        C = C + cb

    nc.variables['conc'][d, :, :] = C

# ------------------
# CLEAN UP
# ------------------

pf.close()
nc.close()
