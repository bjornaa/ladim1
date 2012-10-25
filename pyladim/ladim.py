#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np    # Midlertidig, unødvendig når skikkelig initiering
from netCDF4 import num2date
from trackpart import Euler_Forward 
from input import ROMS_input
from release import ParticleReleaser
from setup import readsup, writesup
from output import OutPut
from behaviour import behaviour

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


# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(setup)

tunits = inp.nc.variables['ocean_time'].units

# ----------------------
# Particle release file
# ----------------------

partini = ParticleReleaser(setup)

# Initial (empty state)
state = partini.state

# ------------------
# Init output file
# -----------------

out = OutPut(setup)
 
# ==============
# Main time loop
# ==============

for i in range(nsteps+1):
    inp.update(i)

    # Read particles ?
    if i == partini.release_step:
        # Tips: Gjøre begge delet i read_particles
        partini.read_particles()
        state.addstate(partini.state)

        
    # Save to file 
    if i % setup['output_period'] == 0:
        print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
        out.write(state)
    
    # Only use surface forcing presently
    # Redundant to give both inp, and inp.U ...
    Euler_Forward(inp, inp.U, inp.V, state.X, state.Y, state.Z, dt=dt)
    
    # Behaviour
    behaviour(state)


# ========
# Clean up
# ========

inp.close()
out.close()

    
    
