#! /usr/bin/env python
# -*- coding: utf-8 -*-

from netCDF4 import num2date
from trackpart import Euler_Forward
from input import ROMS_input
from setup import readsup

# ----------------------
# Initiate the model
# ----------------------

# Read the setup file
setup = readsup('ladim.sup')
             
roms_file = "./data/ocean_avg_0014.nc"


nsteps = setup['nsteps']
dt = setup['dt']

print "nsteps = ", nsteps

inp = ROMS_input(roms_file, roms_file, setup)

tunits = inp.nc.variables['ocean_time'].units


# ---------------
# Main time loop
# ---------------

for i in range(nsteps+1):
    print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
    inp.update(i)
    print "F = ", inp.F, num2date(inp.F, tunits)


# ---------------
# Clean up
# ---------------

print "dryrun finished"

inp.close()


    
    
    
