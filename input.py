# -*- coding: utf-8 -*-

import datetime
from netCDF4 import Dataset, num2date
from roppy import SGrid



def total_seconds(tdelta):
    """Total time in seconds of a timedelta"""
    # Method in python 2.7 
    # Included as a function here for older version
    return tdelta.days*86400 + tdelta.seconds

class ROMS_input(SGrid):
    """
    Class for ROMS input, updated fields and static grid info


    """

    def __init__(self, grid_file, input_file, setup, 
                 subgrid=None, Vinfo=None, verbose=True):

        self.verbose = verbose

        nc0 = Dataset(grid_file)
        SGrid.__init__(self, nc0, subgrid, Vinfo)
        nc0.close()

        nc = Dataset(input_file)
        self.nc = nc
        
        self.timevar = nc.variables['ocean_time']
        self.time_units = self.timevar.units
        time0 = num2date(self.timevar[0],  self.time_units)
        time1 = num2date(self.timevar[-1], self.time_units)
        start_time = setup['start_time']
        self.dt = setup['dt']

        # Check that the times match
        assert(time0 <= start_time)
        assert(setup['stop_time'] <= time1)

        self.step = []
        # "for t in timevar" 
        # does not work with netcdf4-python before 1.0
        # workaround with numeric index j
        for j in range(len(self.timevar)):
            t = self.timevar[j]
            #print t
            otime = num2date(self.timevar[j], self.time_units)
            self.step.append(
                      float(total_seconds(otime - start_time)) / self.dt)

        #print self.step

        # Find j, step[j] <= 0 < step[j+1]
        j = 0
        while self.step[j+1] <= 0:
            j = j + 1
        self.fieldnr = j-1
        T1 = self.timevar[self.fieldnr+1]
        self.T1 = T1
        if self.verbose:
            print "Reading ROMS input, input time = ",   \
                  num2date(self.timevar[self.fieldnr+1], self.time_units)
        self.F = T1             # Read at fieldnr+1
        self.U1 = self.nc.variables['u'][
                      self.fieldnr+1, :, self.Ju, self.Iu]
        self.V1 = self.nc.variables['v'][
                      self.fieldnr+1, :, self.Jv, self.Iv]
        #self.dF = 0.0
        # Has step[fieldnr+1] <= 0 < step[fieldnr+2]
        # F is field at step = step[fieldnr+1]
        # If self.step[fieldnr+1] == 0, this is start
        # otherwise, update reads new field


    def update(self, t):
        """Update the fields to time step t"""
        dt = self.dt
        step = self.step
        if t > step[self.fieldnr+1]:  # Need new fields
            self.fieldnr = self.fieldnr + 1
            j = self.fieldnr
            self.T0 = self.T1
            self.U0 = self.U1
            self.V0 = self.V1
            if self.verbose:
                print "Reading ROMS input, input time = ",   \
                       num2date(self.timevar[self.fieldnr+1], self.time_units)
            self.T1 = self.nc.variables['ocean_time'][j+1]  # Read new fields
            self.U1 = self.nc.variables['u'][
                          self.fieldnr+1, :, self.Ju, self.Iu]
            self.V1 = self.nc.variables['v'][
                          self.fieldnr+1, :, self.Jv, self.Iv]
            print "=== Reading, field nr = ", j+1
            print step[self.fieldnr], " < ", t, " <= ", step[self.fieldnr+1]
            self.timespan = step[self.fieldnr+1] - step[self.fieldnr]
            #self.dF = (step[j+1]-step[j]) * dt / timespan
        else:  # update old fields
            pass

        # Linear interpolation in time
        a = (step[self.fieldnr+1]-t) / self.timespan
        b = (t-step[self.fieldnr]) / self.timespan
        self.F = a*self.T0 + b*self.T1
        self.U = a*self.U0 + b*self.U1
        self.V = a*self.V0 + b*self.V1

    # --------------

    def close(self):

        # Close the ROMS grid file
        self.nc.close()





