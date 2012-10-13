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

pid   = np.array([], dtype='int32')
X     = np.array([], dtype='float32')
Y     = np.array([], dtype='float32')
Z     = np.array([], dtype='float32')
start = np.array([], dtype='int32')

#particle_release_file = 'particles.in'
#particle_release_file = 'line.in'
# Bare gi setup som argument ??
partini = ParticleReleaser(setup)


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
        pid = np.concatenate((pid, partini.pid))
        X = np.concatenate((X, partini.X))
        Y = np.concatenate((Y, partini.Y))
        Z = np.concatenate((Z, partini.Z))
        start = np.concatenate((start, partini.start))
        
    # Save to file 
    if i % setup['output_period'] == 0:
        print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
        out.write(pid, X, Y)
    
    # Only use surface forcing presently
    Euler_Forward(inp, inp.U, inp.V, X, Y, Z, dt=dt)
    

 
# ========
# Clean up
# ========

inp.close()
out.close()

    
    
