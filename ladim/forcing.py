# -*- coding: utf-8 -*-

# import datetime
import glob
import logging
import numpy as np
from netCDF4 import Dataset, num2date
# from ladim.grid import Grid
from ladim.grid import z2s, sample3DUV, sample3D


class ROMS_forcing:
    """
    Class for ROMS forcing

    """

    def __init__(self, config, grid):

        logging.basicConfig(level=logging.INFO)
        logging.info("Initiating forcing")

        self._grid = grid  # Get the grid object, make private?

        self.ibm_forcing = config.ibm_forcing

        # Test for glob, use MFDataset if needed
        files = glob.glob(config.input_file)
        numfiles = len(files)
        if numfiles == 0:
            print("No input file:", config.input_file)
            raise SystemExit(3)
        logging.info('Number of forcing files = {}'.format(numfiles))

        # ----------------------------------------
        # Open first file for some general info
        # must be valid for all the files
        # ----------------------------------------

        with Dataset(files[0]) as nc:

            time_units = nc.variables['ocean_time'].units

            self.scaled = dict()
            self.scale_factor = dict()
            self.add_offset = dict()

            if hasattr(nc.variables['u'], 'scale_factor'):
                self.scaled['U'] = True
                self.scale_factor['U'] = np.float32(
                    nc.variables['u'].scale_factor)
                self.add_offset['U'] = np.float32(
                    nc.variables['u'].add_offset)
                self.scaled['V'] = True
                self.scale_factor['V'] = np.float32(
                    self.scale_factor['U'])
                self.add_offset['V'] = np.float32(
                    self.add_offset['U'])
            else:
                self.scaled['U'] = False
                self.scaled['V'] = False

            for key in self.ibm_forcing:
                if hasattr(nc.variables[key], 'scale_factor'):
                    self.scaled[key] = True
                    self.scale_factor[key] = np.float32(
                        nc.variables[key].scale_factor)
                    self.add_offset[key] = np.float32(
                        nc.variables[key].add_offset)
                else:
                    self.scaled[key] = False

        # ---------------------------
        # Overview of all the files
        # ---------------------------

        times = []              # list of times of all frames
        num_frames = []         # Available time frames in each file
        # change_times = []     # Times for change of file
        for fname in files:
            with Dataset(fname) as nc:
                new_times = nc.variables['ocean_time'][:]
                times.extend(new_times)
                num_frames.append(len(new_times))
        logging.info("Number of available forcing times = {:d}".
                     format(len(times)))

        # Find first/last forcing times
        # -----------------------------
        time0 = num2date(times[0],  time_units)
        time1 = num2date(times[-1], time_units)
        logging.info('time0 = {}'.format(str(time0)))
        logging.info('time1 = {}'.format(str(time1)))
        # print(time0)
        # print(time1)
        start_time = np.datetime64(config.start_time)
        # self.time = start_time
        self.dt = np.timedelta64(int(config.dt), 's')  # or use

        # Check that forcing period covers the simulation period
        # ------------------------------------------------------
        # Use logging module for this

        if time0 > start_time:
            logging.error("No forcing at start time")
            raise SystemExit(3)
        if time1 < config.stop_time:
            logging.error("No forcing at stop time")
            raise SystemExit(3)

        # Make a list steps of the forcing time steps
        # --------------------------------------------
        steps = []     # Model time step of forcing
        for t in times:
            otime = np.datetime64(num2date(t, time_units))
            dtime = np.timedelta64(otime - start_time, 's').astype(int)
            steps.append(int(dtime / config.dt))

        # print(steps)

        # change_steps = [steps[t] for t in change_times]

        file_idx = dict()
        frame_idx = dict()
        step_counter = -1
        for i, fname in enumerate(files):
            for frame in range(num_frames[i]):
                step_counter += 1
                step = steps[step_counter]
                # print(step_counter, step, i, frame)
                file_idx[step] = i
                frame_idx[step] = frame

        self._files = files
        self.stepdiff = np.diff(steps)
        self.file_idx = file_idx
        self.frame_idx = frame_idx

        # Read old input
        # requires at least one input before start
        # to get Runge-Kutta going
        # --------------
        # Last step < 0
        #
        V = [step for step in steps if step < 0]
        if V:
            prestep = max(V)
        elif steps[0] == 0:
            prestep = 0
        else:
            # No forcing at start, should alreadu be
            raise SystemExit(3)

        self.U, self.V = self._read_velocity(prestep)
        stepdiff = self.stepdiff[steps.index(prestep)]
        nextstep = prestep + stepdiff
        self.Unew, self.Vnew = self._read_velocity(nextstep)
        self.dU = (self.Unew - self.U) / stepdiff
        self.dV = (self.Vnew - self.V) / stepdiff
        if prestep == 0:
            # Hold back to be in phase
            self.U = self.Unew
            self.V = self.Vnew

        # Do more elegant
        for name in self.ibm_forcing:
            print(self.ibm_forcing)
            # print("XXX", name)
            # print(name+'old')
            self[name] = self._read_field(name, prestep)
            self[name+'new'] = self._read_field(name, 0)
            self['d'+name] = (self[name] - self[name+'new']) / prestep

        # print step[fieldnr], " < ", 0, " <= ", step[fieldnr+1]

        # Variables needed by update
        # timevar = timevar
        # self._step = step
        # self._fieldnr = fieldnr
        self.steps = steps
        self._files = files
        # stepdiff[i] = steps[i+1] - step[i]
        # self.last_field = -1  #

    # ==============================================

    def update(self, t):
        """Update the fields to time step t"""
        # dt = self.dt
        # steps = self.steps
        # fieldnr = self._fieldnr
        # self.time += self.dt  # et tidsteg for tidlig ??
        # print('forcing-update: tid = ', self.time)
        logging.debug("Updating forcing, time step = {}".format(t))
        if t in self.steps:  # No time interpolation
            self.U = self.Unew
            self.V = self.Vnew
            for name in self.ibm_forcing:
                self[name] = self[name+'new']
        else:
            if t-1 in self.steps:   # Need new fields
                stepdiff = self.stepdiff[self.steps.index(t-1)]
                nextstep = t-1 + stepdiff
                self.Unew, self.Vnew = self._read_velocity(nextstep)
                for name in self.ibm_forcing:
                    self[name+'new'] = self._read_field(name, nextstep)
                # Kan slås sammen med testen øverst
                self.dU = (self.Unew - self.U) / stepdiff
                self.dV = (self.Vnew - self.V) / stepdiff
                for name in self.ibm_forcing:
                    self['d'+name] = (self[name+'new'] - self[name]) / stepdiff

            self.U += self.dU
            self.V += self.dV
            # May suppose changes slowly, use value until new?
            for name in self.ibm_forcing:
                self[name] += self['d'+name]

    # --------------

    def _read_velocity(self, n):
        """Read fields at time step = n"""
        # Need a switch for reading W
        # T = self._nc.variables['ocean_time'][n]  # Read new fields

        # Handle file opening/closing
        # Always read velocity before other fields
        logging.info('Reading velocity for time step = {}'.format(n))
        first = True
        if first:   # Open file initiallt
            self._nc = Dataset(self._files[self.file_idx[n]])
            self._nc.set_auto_maskandscale(False)
            first = False
        else:
            if self.frame_idx[n] == 0:  # New file
                self._nc.close()  # Close previous file
                self._nc = Dataset(self._files[self.file_idx[n]])
                self._nc.set_auto_maskandscale(False)

        frame = self.frame_idx[n]

        # Read the velocity
        U = self._nc.variables['u'][frame, :, self._grid.Ju, self._grid.Iu]
        V = self._nc.variables['v'][frame, :, self._grid.Jv, self._grid.Iv]
        # Scale if needed
        if self.scaled['U']:
            U = self.add_offset['U'] + self.scale_factor['U']*U
            V = self.add_offset['U'] + self.scale_factor['U']*V

        # If necessary put U,V = zero on land and land boundaries
        # Stay as float32
        np.multiply(U, self._grid.Mu, out=U)
        np.multiply(V, self._grid.Mv, out=V)
        return U, V

    def _read_field(self, name, n):
        """Read a 3D field"""
        print("IBM-forcing:", name)
        frame = self.frame_idx[n]
        F = self._nc.variables[name][frame, :, self._grid.J, self._grid.I]
        if self.scaled[name]:
            F = self.add_offset[name] + self.scale_factor[name]*F
        return F

    # Allow item notation
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # ------------------

    def close(self):

        self._nc.close()

    # def sample_velocity(self, X, Y, Z, tstep=0, method='bilinear'):
    def sample_velocity(self, X, Y, Z, tstep=0, method='nearest'):

        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = z2s(self._grid.z_r, X-i0, Y-j0, Z)
        if tstep < 0.001:
            return sample3DUV(self.U, self.V,
                              X-i0, Y-j0, K, A, method=method)
        else:
            return sample3DUV(self.U+tstep*self.dU, self.V+tstep*self.dV,
                              X-i0, Y-j0, K, A, method=method)

    # Simplify to grid cell
    def sample_field(self, X, Y, Z, name):
        # should not be necessary to repeat
        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = z2s(self._grid.z_r, X-i0, Y-j0, Z)
        F = self[name]
        return sample3D(F, X-i0, Y-j0, K, A, method='nearest')
