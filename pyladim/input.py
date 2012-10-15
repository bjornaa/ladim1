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

    def __init__(self, setup, subgrid=None, Vinfo=None, verbose=True):

        self.verbose = verbose

        # Initiate the SGrid part
        # -----------------------
        nc0 = Dataset(setup['grid_file'])
        SGrid.__init__(self, nc0, subgrid, Vinfo)
        nc0.close()

        # Open the forcing file
        # ---------------------
        nc = Dataset(setup['input_file'])
        self.nc = nc

        # Find first/last forcing times
        # -----------------------------
        timevar = nc.variables['ocean_time']
        self._time_units = timevar.units
        time0 = num2date(timevar[0],  self._time_units)
        time1 = num2date(timevar[-1], self._time_units)
        start_time = setup['start_time']

        # Check that forcing period covers the simulation period
        # ------------------------------------------------------
        assert(time0 <= start_time)
        assert(setup['stop_time'] <= time1)

        # Make a list "step" of the forcing time steps
        # --------------------------------------------
        step = []
        #self.dt = setup['dt']
        for j in range(len(timevar)):
            t = timevar[j]
            otime = num2date(timevar[j], self._time_units)
            step.append(
                 int(float(total_seconds(otime - start_time)) / setup['dt']))

        # From asserts above: step[0] <= 0 < nsteps <= step[-1]
        # Find fieldnr, step[fieldnr] <= 0 < step[fieldnr+1]
        # --------------------------------------------------
        n = 0
        while step[n+1] <= 0:
            n = n + 1
        fieldnr = n
        #print step[fieldnr], step[fieldnr+1]
        self._timespan = step[fieldnr+1] - step[fieldnr]

        # Read old input
        # --------------
        self.T1 = timevar[fieldnr]
        self.U1 = self.nc.variables['u'][
                      fieldnr, :, self.Ju, self.Iu]
        self.V1 = self.nc.variables['v'][
                      fieldnr, :, self.Jv, self.Iv]

        if self.verbose:
            print "Reading ROMS input, input time = ",   \
                  num2date(timevar[fieldnr], self._time_units)

            print step[n-1], " < ", t, " <= ", step[n]
            print "U[100,80] ", self.U1[-1,100,80]


        # Variables needed by update
        self._timevar = timevar
        self._step    = step
        self._fieldnr = fieldnr

    # ==============================================

    def update(self, t):
        """Update the fields to time step t"""
        #dt = self.dt
        step = self._step
        fieldnr = self._fieldnr
        
        if t == step[fieldnr]: # No interpolation necessary
            self.F = self.T1
            self.U = self.U1
            self.V = self.V1
            return None
        if t > step[fieldnr]:  # Need new fields
            n = fieldnr + 1
            self.T0 = self.T1
            self.U0 = self.U1
            self.V0 = self.V1
            if self.verbose:
                print "Reading ROMS input, input time = ",   \
                       num2date(self._timevar[n], self._time_units)
            self.T1 = self.nc.variables['ocean_time'][n]  # Read new fields
            self.U1 = self.nc.variables['u'][n, :, self.Ju, self.Iu]
            self.V1 = self.nc.variables['v'][n, :, self.Jv, self.Iv]
            print step[n-1], " < ", t, " <= ", step[n]
            print "U[100,80] ", self.U1[-1,100,80]
            self._timespan = step[n] - step[n-1]
            self._fieldnr = n

        # Linear interpolation in time
        a = (step[fieldnr]-t) / self._timespan
        #b = (t-step[n-1]) / self.timespan
        self.F = a*self.T0 + (1-a)*self.T1
        self.U = a*self.U0 + (1-a)*self.U1
        self.V = a*self.V0 + (1-a)*self.V1

    # --------------

    def close(self):

        # Close the ROMS grid file
        self.nc.close()





