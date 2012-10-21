#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np    # Midlertidig, unødvendig når skikkelig initiering
from netCDF4 import num2date
from trackpart import Euler_Forward 
from input import ROMS_input
from release import ParticleReleaser
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


# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(setup)

tunits = inp.nc.variables['ocean_time'].units

# --------------------
# Init some particles
# --------------------

# Lage et objekt som holder partiklene ??

# Initiate the model state
# unødvendig, gjøres av ParticleReleaser
#state = dict(
#    pid   = np.array([], dtype='int32'),
#    X     = np.array([], dtype='float32'),
#    Y     = np.array([], dtype='float32'),
#    Z     = np.array([], dtype='float32'),
#   start = np.array([], dtype='int32')
#)


#particle_release_file = 'particles.in'
#particle_release_file = 'line.in'
# Bare gi setup som argument ??
partini = ParticleReleaser(setup)

# Initial (empty state)
state = partini.state

# -----------
# Init output
# -----------

out = OutPut(setup)
 
# ==============
# Main time loop
# ==============

for i in range(nsteps+1):
    inp.update(i)
    #print "F = ", inp.F, num2date(inp.F, tunits)

    # Read particles ?
    if i == partini.release_step:
        partini.read_particles()
        # Trenger ikke partini.state
        # Kan bruke getattr(partini, v)
        for v in ['pid', 'X', 'Y', 'Z', 'start']:
            state[v] = np.concatenate((state[v], partini.state[v]))
        
    # Save to file 
    if i % setup['output_period'] == 0:
        print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
        out.write(state)
    
    # Only use surface forcing presently
    Euler_Forward(inp, inp.U, inp.V, state['X'], state['Y'], state['Z'], dt=dt)
    

 
# ========
# Clean up
# ========

inp.close()
out.close()

    
    
