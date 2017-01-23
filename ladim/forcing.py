# -*- coding: utf-8 -*-

# import datetime
import glob
import numpy as np
from netCDF4 import Dataset, MFDataset, num2date
# from ladim.grid import Grid
from ladim.sample_roms import Z2S, sample3DUV


class ROMS_forcing():
    """
    Class for ROMS forcing

    """

    def __init__(self, config, grid):

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
        start_time = np.datetime64(config.start_time)

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
            n = n + 1
        fieldnr = n
        # print step[fieldnr], step[fieldnr+1]
        self._timespan = step[fieldnr+1] - step[fieldnr]

        # Read old input
        # --------------
        self.T1, self.U1, self.V1 = self._readfield(fieldnr)

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

        if t == step[fieldnr]:  # No interpolation necessary
            self.F = self.T1
            self.U = self.U1
            self.V = self.V1
            return None
        if t > step[fieldnr]:  # Need new fields
            fieldnr = fieldnr + 1
            self.T0 = self.T1
            self.U0 = self.U1
            self.V0 = self.V1
            self.T1, self.U1, self.V1 = self._readfield(fieldnr)
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

    # --------------

    def _readfield(self, n):
        """Read fields at time frame = n"""
        T = self._nc.variables['ocean_time'][n]  # Read new fields
        U = self._nc.variables['u'][n, :, self._grid.Ju, self._grid.Iu]
        V = self._nc.variables['v'][n, :, self._grid.Jv, self._grid.Iv]
        if True:
            print("Reading ROMS input, input time = ",
                  num2date(self._timevar[n], self._time_units))
        return T, U, V

    # ------------------

    def close(self):

        # Close the ROMS grid file
        self._nc.close()

    def sample_velocity(self, state):
        X = state['X'] - self._grid.i0
        Y = state['Y'] - self._grid.j0
        Z = state['Z']   # Use negative depth (for now)
        # Save K, A for sampling of scalar fields
        K, A = Z2S(self._grid.z_r, X, Y, Z)
        return sample3DUV(self.U, self.V, state['X'], state['Y'], K, A)
