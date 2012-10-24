# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset, num2date
#import roppy

class ParticleFile(object):

    def __init__(self, filename):
        self.nc = Dataset(filename)
        # Change Time to time (or allow both)
        self.nFrames = len(self.nc.dimensions['time'])

    def get_time(self, n):
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)
        
        
    def get_position(self, n):
        """Get particle positions at n-th time frame"""
        f = self.nc
        p0 = f.variables['pstart'][n]
        Npart = f.variables['pcount'][n]
        X = f.variables['X'][p0:p0+Npart]
        Y = f.variables['Y'][p0:p0+Npart]
        return X, Y

    def get_variable(self, n, vname):
        f = self.nc
        p0 = f.variables['pStart'][n]
        Npart = f.variables['pCount'][n]
        # put in some error control
        return f.variables[vname][p0:p0+Npart]

    def read_track(self, pid0):
        """Get particle positions along a track"""

        # Tips, returner array med indeks-verdier
        # kanskje bare indeks verdier i hovedarray
        # => kan lese vilkårlige verdier
        # også ha en variant, 

        nc = self.nc


        X, Y = [], []
        first_time = None  
        last_time  = None  

        # After loop
        # particle is alive for n in [first_time:last_time]
        # or to the end if last_time == 0

        for n in xrange(self.nFrames):
            pstart = nc.variables['pstart'][n]
            pcount = nc.variables['pcount'][n]
            pid = nc.variables['pid'][pstart:pstart+pcount][:]

            if pid[-1] < pid0: # particle not released yet
                cycle

            if first_time != None:
                first_time = n

            #index = sum(pid < pid0) # eller lignende
            index = pid.searchsorted(pid0)
            if pid[index] < pid0: # pid0 is missing
                last_time = n     # 
                break             # No need for more cycles
    
            X.append(nc.variables['X'][pstart + index])
            Y.append(nc.variables['Y'][pstart + index])

        return X, Y, first_time, last_time

    def close(self):
        self.nc.close()


