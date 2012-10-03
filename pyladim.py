#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np    # Midlertidig, unødvendig når skikkelig initiering
from netCDF4 import num2date
from trackpart import Euler_Forward 
from input import ROMS_input
from setup import readsup, writesup
from output import OutPut

# ==================
# Initiate the model
# ==================

# Read the setup file
# --------------------

setup_file = 'ladim.sup'      # take from command line
setup = readsup('ladim.sup')

print " --- pyladim setup ----"
print "setup file: ", setup_file
writesup(setup)
print " --- end of setup ---\n"

nsteps = setup['nsteps']
dt = setup['dt']


# Ta dette fra setup             
roms_file = "./data/ocean_avg_0014.nc"


# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(roms_file, roms_file, setup)

tunits = inp.nc.variables['ocean_time'].units

# --------------------
# Init some particles
# --------------------

Npart = 10
particle_id = np.arange(1, Npart+1, dtype='int')
X = np.linspace(96.0, 122.0, num=Npart)
Y = 100.0 + np.zeros_like(X)

# -----------
# Init output
# -----------

out = OutPut(setup)
 
# ==============
# Main time loop
# ==============

for i in range(nsteps+1):
    print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
    inp.update(i)
    #print "F = ", inp.F, num2date(inp.F, tunits)

    # Save to file 
    if i % setup['output_period'] == 0:
        out.write(i, X, Y)
    
    # Only use surface forcing presently
    Euler_Forward(inp, inp.U[-1,:,:], inp.V[-1,:,:], X, Y, dt=dt)

 
# ========
# Clean up
# ========

inp.close()
out.close()

    
    
