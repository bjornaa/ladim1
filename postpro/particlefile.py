# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset, num2date

# Methods:
#  get_positions : all positions at time n (flag for lon, lat?)
#  get_variable_distribution : all variables at time n
#  
#  active(p, n) : 1  if p is active at time n
#                 0  if p is not released (yet)
#                 -1 if p is deactivated
# Bedre navn: status?, activity_status 
#  first_time(p) : First time frame it is active
#  last_time(p)  : Last time it is active
#


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
        """Get values of a particle variable"""
        f = self.nc
        p0 = f.variables['pStart'][n]
        Npart = f.variables['pCount'][n]
        # put in some error control
        return f.variables[vname][p0:p0+Npart]

    # Alternativ: gi en default verdi om ikke aktiv
    #    Evt. raise exception
    # ha en separat sjekk på aktivitet
    def get_particle_variable(self, p, n, vname):
        """Get variable vname at time step n at particle p

        Returns value, active
        where: active = 0  if particle is not released (yet)
                      = -1 if particle has been active but is now closed
                      = 1  if particle is active
               value = value at particle at time n, if active
                     = ha en fill value if not active

        """
        
        pid = self.get_variable(n, 'pid')
        
        if pid[-1] < p: # particle not released yet
            active = 0

        index = pid.searchsorted(p)
        if pid[index] < p:      # p is missing, but has been active
            active = -1

        A = self.get_variable(n, vname)

# ------------------------------

    def read_track(self, p):
        """Get particle positions along a single track"""


        f = self.nc


        X, Y = [], []
        first_time = None  
        last_time  = None  

        # After loop
        # particle is alive for n in [first_time:last_time]
        # or to the end if last_time == 0

        for n in xrange(self.nFrames):
            pstart = f.variables['pstart'][n]
            pcount = f.variables['pcount'][n]
            pid = f.variables['pid'][pstart:pstart+pcount][:]

            if pid[-1] < p: # particle not released yet
                cycle

            if first_time != None:
                first_time = n

            #index = sum(pid < pid0) # eller lignende
            index = pid.searchsorted(p)
            if pid[index] < p   : # p is missing
                last_time = n     # 
                break             # No need for more cycles
    
            X.append(f.variables['X'][pstart + index])
            Y.append(f.variables['Y'][pstart + index])

        return X, Y, first_time, last_time

    def close(self):
        self.nc.close()

# ----------------------------------

# Ikke testet nok for udefinerte partikler
# f.eks. for store => I[J] blir upassende


    def read_tracks(self, P):
        """Get particle positions along tracks

        Returns an array of shape (len(P),nFrames)
        with NaN where particles are undefined

        """

        P = np.asarray(P)
        nP = len(P)

        f = self.nc

        X = np.nan + np.zeros((self.nFrames, nP))
        Y = np.nan + np.zeros((self.nFrames, nP))


        for n in xrange(self.nFrames):
            
            pstart = f.variables['pstart'][n]
            pcount = f.variables['pcount'][n]
            tslice = slice(pstart, pstart+pcount)   # time slice
            pid = f.variables['pid'][tslice]        

            I = pid.searchsorted(P+1)               
            J, = np.nonzero(I == pid[I-1])

            Xn = f.variables['X'][tslice]
            Yn = f.variables['Y'][tslice]

            X[n,J] = Xn[I[J]]
            Y[n,J] = Yn[I[J]]

        return X, Y

    def close(self):
        self.nc.close()


