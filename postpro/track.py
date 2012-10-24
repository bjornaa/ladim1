# -*- coding: utf-8 -*-

# Make a track of one particle


from netCDF4 import Dataset


pid0 = 1222 

particle_file = "../output/pyladim_out.nc"



f = Dataset(particle_file)

Ntimes = len(f.dimension['time'])

X, Y = [], []
first_time = None  
last_time  = None  
# After loop
# particle is alive for n in [first_time:last_time]
# or to the end if last_time == 0

for n in Ntimes:
    pstart = f.variables['pstart'][n]
    pcount = f.variables['pcount'][n]
    pid = f.variables[pstart:pstart+pcount][:]

    if pid[-1] < pid0: # particle not released yet
        cycle

    if first_time != None:
        first_time = n

    #index = sum(pid < pid0) # eller lignende
    index = pid.searchsorted(pid0)
    if pid[index] < pid0: # pid0 is missing
        last_time = n     # 
        break             # No need for more cycles
    
    X.append(f.variables

    


