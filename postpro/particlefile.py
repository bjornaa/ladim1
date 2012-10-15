import numpy as np
from netCDF4 import Dataset, num2date
#import roppy

class ParticleFile(object):

    def __init__(self, filename):
        self.nc = Dataset(filename)
        # Change Time to time (or allow both)
        self.nFrames = len(self.nc.dimensions['Time'])

    def get_time(self, n):
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)
        
        
    def get_position(self, n):
        """Get particle positions at n-th time frame"""
        f = self.nc
        p0 = f.variables['pStart'][n]
        Npart = f.variables['pCount'][n]
        X = f.variables['X'][p0:p0+Npart]
        Y = f.variables['Y'][p0:p0+Npart]
        return X, Y

    def get_variable(self, n, vname):
        f = self.nc
        p0 = f.variables['pStart'][n]
        Npart = f.variables['pCount'][n]
        # put in some error control
        return f.variables[vname][p0:p0+Npart]

    def read_track(self, pid):
        """Get particle positions along a track"""
        pass

    def close(self):
        self.nc.close()


