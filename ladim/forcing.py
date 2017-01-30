# -*- coding: utf-8 -*-

# import datetime
import glob
import logging
import numpy as np
from netCDF4 import Dataset, MFDataset, num2date
# from ladim.grid import Grid
from ladim.sample_roms import Z2S, sample3DUV, sample3D


class ROMS_forcing:
    """
    Class for ROMS forcing

    """

    def __init__(self, config, grid):

        # loglevel = logging.INFO

        self._grid = grid  # Get the grid object, make private?

        # Test for glob, use MFDataset if needed
        files = glob.glob(config.input_file)
        if len(files) == 0:
            print("No input file:", config.input_file)
            raise SystemExit(3)
        elif len(files) == 1:
            nc = Dataset(files[0])
        else:   # Multiple files
            files.sort()
            nc = MFDataset(files)
        self._nc = nc

        # Find first/last forcing times
        # -----------------------------
        self._timevar = nc.variables['ocean_time']
        timevar = self._timevar
        self._time_units = timevar.units
        time0 = num2date(timevar[0],  self._time_units)
        time1 = num2date(timevar[-1], self._time_units)
        logging.info('time0 = {}'.format(str(time0)))
        logging.info('time1 = {}'.format(str(time1)))
        # print(time0)
        # print(time1)
        start_time = np.datetime64(config.start_time)
        self.time = start_time
        self.dt = np.timedelta64(int(config.dt), 's')  # or use

        # Check that forcing period covers the simulation period
        # ------------------------------------------------------
        # Use logging module for this

        assert(time0 <= start_time)
        assert(config.stop_time <= time1)

        # Make a list "step" of the forcing time steps
        # --------------------------------------------
        step = []
        for j in range(len(timevar)):
            # t = timevar[j]
            otime = np.datetime64(num2date(timevar[j], self._time_units))
            dtime = np.timedelta64(otime - start_time, 's').astype(int)
            step.append(dtime / config.dt)

        # From asserts above: step[0] <= 0 < nsteps <= step[-1]
        # Find fieldnr, step[fieldnr] <= 0 < step[fieldnr+1]
        # --------------------------------------------------
        n = 0
        while step[n+1] <= 0:
            n += 1
        fieldnr = n
        # print step[fieldnr], step[fieldnr+1]
        self._timespan = step[fieldnr+1] - step[fieldnr]

        self.ibm_forcing = config.ibm_forcing

        # Read old input
        # --------------
        self.T1, self.U1, self.V1 = self._read_velocity(fieldnr)

        for name in self.ibm_forcing:
            print(self.ibm_forcing)
            print("XXX", name)
            print(name+'1')
            self[name + '1'] = self._read_field(name, fieldnr)

        # print step[fieldnr], " < ", 0, " <= ", step[fieldnr+1]

        # Variables needed by update
        # timevar = timevar
        self._step = step
        self._fieldnr = fieldnr

    # ==============================================

    def update(self, t):
        """Update the fields to time step t"""
        # dt = self.dt
        step = self._step
        fieldnr = self._fieldnr
        self.time += self.dt  # et tidsteg for tidlig ??
        # print('forcing-update: tid = ', self.time)

        if t == step[fieldnr]:  # No interpolation necessary
            self.F = self.T1
            self.U = self.U1
            self.V = self.V1
            for name in self.ibm_forcing:
                self[name] = self[name+'1']
            # Første gang, improve
            self.dT = 0
            self.dU = 0
            self.dV = 0
            for name in self.ibm_forcing:
                self['d'+name] = 0
        if t > step[fieldnr]:  # Need new fields
            fieldnr += 1
            self.T0 = self.T1
            self.U0 = self.U1
            self.V0 = self.V1
            self.T1, self.U1, self.V1 = self._read_velocity(fieldnr)
            for name in self.ibm_forcing:
                self[name+'0'] = self[name+'1']
                self[name+'1'] = self._read_field(name, fieldnr)

            # print step[fieldnr-1], " < ", t, " <= ", step[fieldnr]
            self._timespan = step[fieldnr] - step[fieldnr-1]
            self.dT = (self.T1 - self.T0) / self._timespan
            self.dU = (self.U1 - self.U0) / self._timespan
            self.dV = (self.V1 - self.V0) / self._timespan
            self._fieldnr = fieldnr

        # Linear interpolation in time
        # print "fieldnr ... = ", fieldnr, step[fieldnr]-t, self._timespan
        self.F += self.dT
        self.U += self.dU
        self.V += self.dV
        for name in self.ibm_forcing:
            self[name] += self['d'+name]

    # --------------

    # Tåpelig å bruke T slik
    def _read_velocity(self, n):
        """Read fields at time frame = n"""
        # Need a switch for reading W
        T = self._nc.variables['ocean_time'][n]  # Read new fields
        U = self._nc.variables['u'][n, :, self._grid.Ju, self._grid.Iu]
        V = self._nc.variables['v'][n, :, self._grid.Jv, self._grid.Iv]
        if True:
            print("Reading ROMS input, input time = ",
                  num2date(self._timevar[n], self._time_units))
        return T, U, V

    def _read_field(self, name, n):
        """Read a 3D field"""
        print("IBM-forcing:", name)
        F = self._nc.variables[name][n, :, self._grid.J, self._grid.I]
        return F

    # Allow item notation
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # ------------------

    def close(self):

        # Close the ROMS grid file
        self._nc.close()

    # def sample_velocity(self, state):
    #     X = state['X'] - self._grid.i0
    #     Y = state['Y'] - self._grid.j0
    #     Z = state['Z']   # Use negative depth (for now)
    def sample_velocity(self, X, Y, Z, tstep=0):
        # Save K, A for sampling of scalar fields
        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = Z2S(self._grid.z_r, X-i0, Y-j0, Z)
        if tstep < 0.001:
            return sample3DUV(self.U, self.V, X-i0, Y-j0, K, A)
        else:
            return sample3DUV(self.U+tstep*self.dU, self.V+tstep*self.dV,
                              X-i0, Y-j0, K, A)

    def sample_field(self, X, Y, Z, name):
        # should not be necessary to repeat
        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = Z2S(self._grid.z_r, X-i0, Y-j0, Z)
        F = self[name]
        return sample3D(F, X-i0, Y-j0, K, A)
