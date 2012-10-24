# -*- coding: utf-8 -*-

# Make a track of one particle

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import roppy.mpl_util

pid0 = 8222 

particle_file = "../output/pyladim_out.nc"
roms_file     = '../input/ocean_avg_0014.nc'

# Subgrid definition
i0, j0 = 70,   80
i1, j1 = 150, 133

# ----------------

# ROMS grid, plot domain

f0 = Dataset(roms_file)
g = roppy.SGrid(f0, subgrid=(i0,i1,j0,j1))
f0.close()



f = Dataset(particle_file)

Ntimes = len(f.dimensions['time'])

X, Y = [], []
first_time = None  
last_time  = None  
# After loop
# particle is alive for n in [first_time:last_time]
# or to the end if last_time == 0

for n in xrange(Ntimes):
    pstart = f.variables['pstart'][n]
    pcount = f.variables['pcount'][n]
    pid = f.variables['pid'][pstart:pstart+pcount][:]

    if pid[-1] < pid0: # particle not released yet
        cycle

    if first_time != None:
        first_time = n

    #index = sum(pid < pid0) # eller lignende
    index = pid.searchsorted(pid0)
    if pid[index] < pid0: # pid0 is missing
        last_time = n     # 
        break             # No need for more cycles
    
    X.append(f.variables['X'][pstart + index] - i0)
    Y.append(f.variables['Y'][pstart + index] - j0)

# Make plot

cmap = plt.get_cmap('Blues')
plt.contourf(g.h, cmap=cmap, alpha=0.3)
roppy.mpl_util.landmask(g.mask_rho, (0.6, 0.8, 0.0))

plt.plot(X[0], Y[0], 'rx')
plt.plot(X, Y, '-')

plt.axis('image')
plt.show()

    


