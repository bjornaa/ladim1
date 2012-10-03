# -*- coding: utf-8 -*-

from netCDF4 import Dataset

class OutPut(object):

    def __init__(self, setup, outfile, outper, Nout):

        nc = Dataset(outfile, mode='w', format="NETCDF3_CLASSIC")
    
        nc.createDimension('Particle_Index', None)
        nc.createDimension('Time', Nout)

        v = nc.createVariable('time', 'float64', ('Time'))
        v.units = 'seconds since %s' % setup['start_time']
        v = nc.createVariable('pStart', 'int', ('Time'))
        v = nc.createVariable('pCount', 'int', ('Time'))

        v = nc.createVariable('pid', 'int', ('Particle_Index', 'Time'))
        v = nc.createVariable('X', 'float32', ('Particle_Index', 'Time'))
        v = nc.createVariable('Y', 'float32', ('Particle_Index', 'Time'))
        #v = nc.createVariable('Z', 'float32', ('Particle_Index', 'Time'))

        self.nc = nc
        self.Nout = Nout
        self.outcount = 0
        self.pStart   = 0
        self.outstep  =  outper*setup['dt']      # Ta fra setup

    def write(self, step, X, Y):
        
        Npar = 10
        t = self.outcount
        nc = self.nc
        nc.variables['pStart'][t] = self.pStart
        nc.variables['pCount'][t] = Npar           # Gjøre dette bedre
        #nc.variables['X'][self.pStart:self.pStart+Npar] = X
        #nc.variables['Y'][self.pStart:self.pStart+Npar] = Y
        # Må ta en og en for å legge til ubegrenset dimensjon
        nc.variables['time'][t] = t * self.outstep
        for p in range(Npar):
            nc.variables['X'][self.pStart+p] = X[p]
            nc.variables['Y'][self.pStart+p] = Y[p]
  
        self.pStart += Npar
        self.outcount += 1

    def close(self):

        self.nc.close()




    
