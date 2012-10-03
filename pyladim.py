#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import num2date
from trackpart import Euler_Forward
from input import ROMS_input
from setup import readsup
from output import OutPut
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

outstep = 12 * 3600     # 12 hourly output
outper = outstep // dt  # output periodicity
Nout = nsteps // outper  # Er dette altid riktig?
out = OutPut(setup, 'a.nc', outper, Nout+2)  # for sikkerhets skyld
 
print "outper, Nout = ", outper, Nout



# ---------------
# Main time loop
# ---------------

for i in range(nsteps+1):
    print "i = ", i, num2date(i*dt,
             'seconds since %s' % str(setup['start_time']))
    inp.update(i)
    #print "F = ", inp.F, num2date(inp.F, tunits)

    # Save to file 
    if i % outper == 0:
        out.write(i, X, Y)
    
    # Only use surface forcing presently
    Euler_Forward(inp, inp.U[-1,:,:], inp.V[-1,:,:], X, Y, dt=dt)




# ---------------
# Clean up
# ---------------

#print "dryrun finished"

inp.close()
out.close()

#import matplotlib.pyplot as plt
#plt.contour(inp.h, levels=[12])
#plt.plot(X, Y, '*')
#plt.axis('image')
#plt.show()
    
    
