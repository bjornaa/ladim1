"""
Grid and Forcing for LADiM for the Regional Ocean Model System (ROMS)

"""

# -----------------------------------
# Bjørn Ådlandsvik, <bjorn@imr.no>
# Institute of Marine Research
# Bergen, Norway
# 2017-03-01
# -----------------------------------

# import sys
import glob
import logging
import numpy as np
from netCDF4 import Dataset, num2date

from ladim.sample import sample2D, bilin_inv


class Grid:
    """Simple ROMS grid object

    Possible grid arguments:
      subgrid = [i0, i1, j0, j1]
        Ordinary python style, start points included, not end points
        Each of the elements can be replaced with None, for no limitation
      Vinfo: dictionary with N, hc, theta_s and theta_b

    """

    # Lagrer en del unødige attributter

    def __init__(self, config):

        logging.info("Initializing ROMS-type grid object")
        try:
            ncid = Dataset(config['grid_file'])
        except OSError:
            logging.error('Grid file {} not found'.format(config['grid_file']))
            raise SystemExit(1)

        # Subgrid, only considers internal grid cells
        # 1 <= i0 < i1 <= imax-1, default=end points
        # 1 <= j0 < j1 <= jmax-1, default=end points
        # Here, imax, jmax refers to whole grid
        jmax, imax = ncid.variables['h'].shape
        whole_grid = [1, imax - 1, 1, jmax - 1]
        if 'subgrid' in config['grid_args']:
            limits = list(config['grid_args']['subgrid'])
        else:
            limits = whole_grid
        # Allow None if no imposed limitation
        for ind, val in enumerate(limits):
            if val is None:
                limits[ind] = whole_grid[ind]

        self.i0, self.i1, self.j0, self.j1 = limits
        self.imax = self.i1 - self.i0
        self.jmax = self.j1 - self.j0
        # print('Grid : imax, jmax, size = ',
        #      self.imax, self.jmax, self.imax*self.jmax)

        # Limits for where velocities are defined
        self.xmin = float(self.i0)
        self.xmax = float(self.i1-1)
        self.ymin = float(self.j0)
        self.ymax = float(self.j1-1)

        # Slices
        #   rho-points
        self.I = slice(self.i0, self.i1)
        self.J = slice(self.j0, self.j1)
        #   U and V-points
        self.Iu = slice(self.i0 - 1, self.i1)
        self.Ju = self.J
        self.Iv = self.I
        self.Jv = slice(self.j0 - 1, self.j1)

        # Vertical grid

        if 'Vinfo' in config['grid_args']:
            Vinfo = config['grid_args']['Vinfo']
            self.N = Vinfo['N']
            self.hc = Vinfo['hc']
            self.Vstretching = Vinfo.get('Vstretching', 1)
            self.Vtransform = Vinfo.get('Vtransform', 1)
            self.Cs_r = s_stretch(self.N, Vinfo['theta_s'], Vinfo['theta_b'],
                                  stagger='rho', Vstretching=self.Vstretching)
            self.Cs_w = s_stretch(self.N, Vinfo['theta_s'], Vinfo['theta_b'],
                                  stagger='w', Vstretching=self.Vstretching)

        else:
            self.hc = ncid.variables['hc'].getValue()
            self.Cs_r = ncid.variables['Cs_r'][:]
            self.Cs_w = ncid.variables['Cs_w'][:]
            self.N = len(self.Cs_r)
            # Vertical transform
            try:
                self.Vtransform = ncid.variables['Vtransform'].getValue()
            except KeyError:
                self.Vtransform = 1  # Default = old way

        # Read some variables
        self.H = ncid.variables['h'][self.J, self.I]
        self.M = ncid.variables['mask_rho'][self.J, self.I].astype(int)
        # self.Mu = ncid.variables['mask_u'][self.Ju, self.Iu]
        # self.Mv = ncid.variables['mask_v'][self.Jv, self.Iv]
        self.dx = 1. / ncid.variables['pm'][self.J, self.I]
        self.dy = 1. / ncid.variables['pn'][self.J, self.I]
        self.lon = ncid.variables['lon_rho'][self.J, self.I]
        self.lat = ncid.variables['lat_rho'][self.J, self.I]
        self.angle = ncid.variables['angle'][self.J, self.I]

        self.z_r = sdepth(self.H, self.hc, self.Cs_r,
                          stagger='rho', Vtransform=self.Vtransform)
        self.z_w = sdepth(self.H, self.hc, self.Cs_w,
                          stagger='w', Vtransform=self.Vtransform)

        # Land masks at u- and v-points
        M = self.M
        Mu = np.zeros((self.jmax, self.imax + 1), dtype=int)
        Mu[:, 1:-1] = M[:, :-1] * M[:, 1:]
        Mu[:, 0] = M[:, 0]
        Mu[:, -1] = M[:, -1]
        self.Mu = Mu

        Mv = np.zeros((self.jmax + 1, self.imax), dtype=int)
        Mv[1:-1, :] = M[:-1, :] * M[1:, :]
        Mv[0, :] = M[0, :]
        Mv[-1, :] = M[-1, :]
        self.Mv = Mv

        # Close the file(s)
        ncid.close()

    def sample_metric(self, X, Y):
        """Sample the metric coefficients

        Changes slowly, so using nearest neighbour
        """
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0

        # Metric is conform for PolarStereographic
        A = self.dx[J, I]
        return A, A

    def sample_depth(self, X, Y):
        """Return the depth of grid cells"""
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0
        return self.H[J, I]

    def lonlat(self, X, Y, method='bilinear'):
        """Return the longitude and latitude from grid coordinates"""
        if method == 'bilinear':   # More accurate
            return self.xy2ll(X, Y)
        else:  # containing grid cell, less accurate
            I = X.round().astype('int') - self.i0
            J = Y.round().astype('int') - self.j0
            return self.lon[J, I], self.lat[J, I]

    def ingrid(self, X, Y):
        """Returns True for points inside the subgrid"""
        return ((self.xmin < X) & (X < self.xmax) &
                (self.ymin < Y) & (Y < self.ymax))

    def onland(self, X, Y):
        """Returns True for points on land"""
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0
        return self.M[J, I] < 1

    # Error if point outside
    def atsea(self, X, Y):
        """Returns True for points at sea"""
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0
        return self.M[J, I] > 0

    def xy2ll(self, X, Y):
        return (sample2D(self.lon, X-self.i0, Y-self.j0),
                sample2D(self.lat, X-self.i0, Y-self.j0))

    def ll2xy(self, lon, lat):
        Y, X = bilin_inv(lon, lat, self.lon, self.lat)
        return X + self.i0, Y + self.j0

# -----------------------------------------------
# The Forcing class from the old forcing module
# -----------------------------------------------


class Forcing:
    """
    Class for ROMS forcing

    """

    def __init__(self, config, grid):

        logging.info("Initiating forcing")

        self._grid = grid  # Get the grid object, make private?

        self.ibm_forcing = config['ibm_forcing']

        # Forcing file(s)
        files = glob.glob(config['input_file'])
        files.sort()
        numfiles = len(files)
        if numfiles == 0:
            logging.error("No input file: {}".format(config['input_file']))
            raise SystemExit(3)
        logging.info('Number of available forcing files = {}'.format(numfiles))

        # ----------------------------------------
        # Open first file for some general info
        # must be valid for all the files
        # ----------------------------------------

        with Dataset(files[0]) as nc:

            time_units = nc.variables['ocean_time'].units

            # self.scaled = dict()
            # self.scale_factor = dict()
            # self.add_offset = dict()

            # if hasattr(nc.variables['u'], 'scale_factor'):
            #     self.scaled['U'] = True
            #     self.scale_factor['U'] = np.float32(
            #         nc.variables['u'].scale_factor)
            #     self.add_offset['U'] = np.float32(
            #         nc.variables['u'].add_offset)
            #     self.scaled['V'] = True
            #     self.scale_factor['V'] = np.float32(
            #         self.scale_factor['U'])
            #     self.add_offset['V'] = np.float32(
            #         self.add_offset['U'])
            # else:
            #     self.scaled['U'] = False
            #     self.scaled['V'] = False

            # for key in self.ibm_forcing:
            #     if hasattr(nc.variables[key], 'scale_factor'):
            #         self.scaled[key] = True
            #         self.scale_factor[key] = np.float32(
            #             nc.variables[key].scale_factor)
            #         self.add_offset[key] = np.float32(
            #             nc.variables[key].add_offset)
            #     else:
            #         self.scaled[key] = False

        # ---------------------------
        # Overview of all the files
        # ---------------------------

        times = []  # list of times of all frames
        num_frames = []  # Available time frames in each file
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
        time0 = num2date(times[0], time_units)
        time1 = num2date(times[-1], time_units)
        logging.info('time0 = {}'.format(str(time0)))
        logging.info('time1 = {}'.format(str(time1)))
        start_time = np.datetime64(config['start_time'])
        # self.time = start_time
        self.dt = np.timedelta64(int(config['dt']), 's')  # or use

        # Check that forcing period covers the simulation period
        # ------------------------------------------------------
        # Use logging module for this

        if time0 > start_time:
            logging.error("No forcing at start time")
            raise SystemExit(3)
        if time1 < config['stop_time']:
            logging.error("No forcing at stop time")
            raise SystemExit(3)

        # Make a list steps of the forcing time steps
        # --------------------------------------------
        steps = []  # Model time step of forcing
        for t in times:
            otime = np.datetime64(num2date(t, time_units))
            dtime = np.timedelta64(otime - start_time, 's').astype(int)
            steps.append(int(dtime / config['dt']))

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
        # prestep = last forcing step < 0
        #
        V = [step for step in steps if step < 0]
        if V:     # Forcing available before start time
            prestep = max(V)
            stepdiff = self.stepdiff[steps.index(prestep)]
            nextstep = prestep + stepdiff
            self.U, self.V = self._read_velocity(prestep)
            self.Unew, self.Vnew = self._read_velocity(nextstep)
            self.dU = (self.Unew - self.U) / stepdiff
            self.dV = (self.Vnew - self.V) / stepdiff
            # Interpolate to time step = -1
            self.U = self.U - (prestep+1)*self.dU
            self.V = self.V - (prestep+1)*self.dV
            # Other forcing
            for name in self.ibm_forcing:
                self[name] = self._read_field(name, prestep)
                self[name+'new'] = self._read_field(name, nextstep)
                self['d'+name] = (self[name+'new'] - self[name]) / prestep
                self[name] = self[name] - (prestep+1)*self['d'+name]

        elif steps[0] == 0:
            # Simulation start at first forcing time
            # Runge-Kutta needs dU and dV in this case as well
            self.U, self.V = self._read_velocity(0)
            self.Unew, self.Vnew = self._read_velocity(steps[1])
            self.dU = (self.Unew - self.U) / steps[1]
            self.dV = (self.Vnew - self.V) / steps[1]
            # Synchronize with start time
            self.Unew = self.U
            self.Vnew = self.V
            # Extrapolate to time step = -1
            self.U = self.U - self.dU
            self.V = self.V - self.dV
            # Other forcing:
            for name in self.ibm_forcing:
                self[name] = self._read_field(name, 0)
                self[name+'new'] = self._read_field(name, steps[1])
                self['d'+name] = (self[name+'new'] - self[name]) / steps[1]
                self[name] = self[name] - self['d'+name]

        else:
            # No forcing at start, should already be excluded
            raise SystemExit(3)

        self.steps = steps
        self._files = files

    # ==============================================

    # Turned off time interpolation of scalar fields
    # TODO: Implement a switch for turning it on again if wanted
    def update(self, t):
        """Update the fields to time step t"""

        # Read from config?
        interpolate_velocity_in_time = True
        interpolate_ibm_forcing_in_time = False

        logging.debug("Updating forcing, time step = {}".format(t))
        if t in self.steps:  # No time interpolation
            self.U = self.Unew
            self.V = self.Vnew
            for name in self.ibm_forcing:
                self[name] = self[name + 'new']
        else:
            if t - 1 in self.steps:  # Need new fields
                stepdiff = self.stepdiff[self.steps.index(t - 1)]
                nextstep = t - 1 + stepdiff
                self.Unew, self.Vnew = self._read_velocity(nextstep)
                for name in self.ibm_forcing:
                    self[name + 'new'] = self._read_field(name, nextstep)
                if interpolate_velocity_in_time:
                    self.dU = (self.Unew - self.U) / stepdiff
                    self.dV = (self.Vnew - self.V) / stepdiff
                if interpolate_ibm_forcing_in_time:
                    for name in self.ibm_forcing:
                        self['d' + name] = (
                            (self[name + 'new'] - self[name]) / stepdiff)

            # "Ordinary" time step (including self.steps+1)
            if interpolate_velocity_in_time:
                self.U += self.dU
                self.V += self.dV
            if interpolate_ibm_forcing_in_time:
                for name in self.ibm_forcing:
                    self[name] += self['d' + name]

    # --------------

    def _read_velocity(self, n):
        """Read fields at time step = n"""
        # Need a switch for reading W
        # T = self._nc.variables['ocean_time'][n]  # Read new fields

        # Handle file opening/closing
        # Always read velocity before other fields
        logging.info('Reading velocity for time step = {}'.format(n))
        first = True
        if first:  # Open file initiallt
            self._nc = Dataset(self._files[self.file_idx[n]])
            # self._nc.set_auto_maskandscale(False)
            first = False
        else:
            if self.frame_idx[n] == 0:  # New file
                self._nc.close()  # Close previous file
                self._nc = Dataset(self._files[self.file_idx[n]])
                # self._nc.set_auto_maskandscale(False)

        frame = self.frame_idx[n]

        # Read the velocity
        U = self._nc.variables['u'][frame, :, self._grid.Ju, self._grid.Iu]
        V = self._nc.variables['v'][frame, :, self._grid.Jv, self._grid.Iv]
        # Scale if needed
        # Assume offset = 0 for velocity
        # if self.scaled['U']:
        #    U = self.scale_factor['U'] * U
        #    V = self.scale_factor['U'] * V
            # U = self.add_offset['U'] + self.scale_factor['U']*U
            # V = self.add_offset['U'] + self.scale_factor['U']*V

        # If necessary put U,V = zero on land and land boundaries
        # Stay as float32
        np.multiply(U, self._grid.Mu, out=U)
        np.multiply(V, self._grid.Mv, out=V)
        return U, V

    def _read_field(self, name, n):
        """Read a 3D field"""
        frame = self.frame_idx[n]
        F = self._nc.variables[name][frame, :, self._grid.J, self._grid.I]
        # if self.scaled[name]:
        #    F = self.add_offset[name] + self.scale_factor[name] * F
        return F

    # Allow item notation
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # ------------------

    def close(self):

        self._nc.close()

    def velocity(self, X, Y, Z, tstep=0, method='bilinear'):

        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = z2s(self._grid.z_r, X - i0, Y - j0, Z)
        if tstep < 0.001:
            U = self.U
            V = self.V
        else:
            U = self.U + tstep*self.dU
            V = self.V + tstep*self.dV
        return sample3DUV(U, V, X-i0, Y-j0, K, A, method=method)

    # Simplify to grid cell
    def field(self, X, Y, Z, name):
        # should not be necessary to repeat
        i0 = self._grid.i0
        j0 = self._grid.j0
        K, A = z2s(self._grid.z_r, X-i0, Y-j0, Z)
        F = self[name]
        return sample3D(F, X-i0, Y-j0, K, A, method='nearest')

# ---------------------------------------------
#      Low-level vertical functions
#      more or less from the roppy package
#      https://github.com/bjornaa/roppy
# ----------------------------------------------


def s_stretch(N, theta_s, theta_b, stagger='rho', Vstretching=1):
    """Compute a s-level stretching array

    *N* : Number of vertical levels

    *theta_s* : Surface stretching factor

    *theta_b* : Bottom stretching factor

    *stagger* : "rho"|"w"

    *Vstretching* : 1|2|4

    """

    if stagger == 'rho':
        S = -1.0 + (0.5 + np.arange(N)) / N
    elif stagger == "w":
        S = np.linspace(-1.0, 0.0, N + 1)
    else:
        raise ValueError("stagger must be 'rho' or 'w'")

    if Vstretching == 1:
        cff1 = 1.0 / np.sinh(theta_s)
        cff2 = 0.5 / np.tanh(0.5 * theta_s)
        return ((1.0 - theta_b) * cff1 * np.sinh(theta_s * S) +
                theta_b * (cff2 * np.tanh(theta_s * (S + 0.5)) - 0.5))

    elif Vstretching == 2:
        a, b = 1.0, 1.0
        Csur = (1 - np.cosh(theta_s * S)) / (np.cosh(theta_s) - 1)
        Cbot = np.sinh(theta_b * (S + 1)) / np.sinh(theta_b) - 1
        mu = (S + 1) ** a * (1 + (a / b) * (1 - (S + 1) ** b))
        return mu * Csur + (1 - mu) * Cbot

    elif Vstretching == 4:
        C = (1 - np.cosh(theta_s * S)) / (np.cosh(theta_s) - 1)
        C = (np.exp(theta_b * C) - 1) / (1 - np.exp(-theta_b))
        return C

    else:
        raise ValueError("Unknown Vstretching")


def sdepth(H, Hc, C, stagger="rho", Vtransform=1):
    """Return depth of rho-points in s-levels

    *H* : arraylike
      Bottom depths [meter, positive]

    *Hc* : scalar
       Critical depth

    *cs_r* : 1D array
       s-level stretching curve

    *stagger* : [ 'rho' | 'w' ]

    *Vtransform* : [ 1 | 2 ]
       defines the transform used, defaults 1 = Song-Haidvogel

    Returns an array with ndim = H.ndim + 1 and
    shape = cs_r.shape + H.shape with the depths of the
    mid-points in the s-levels.

    Typical usage::

    >>> fid = Dataset(roms_file)
    >>> H = fid.variables['h'][:, :]
    >>> C = fid.variables['Cs_r'][:]
    >>> Hc = fid.variables['hc'].getValue()
    >>> z_rho = sdepth(H, Hc, C)

    """
    H = np.asarray(H)
    Hshape = H.shape  # Save the shape of H
    H = H.ravel()  # and make H 1D for easy shape maniplation
    C = np.asarray(C)
    N = len(C)
    outshape = (N,) + Hshape  # Shape of output
    if stagger == 'rho':
        S = -1.0 + (0.5 + np.arange(N)) / N  # Unstretched coordinates
    elif stagger == 'w':
        S = np.linspace(-1.0, 0.0, N)
    else:
        raise ValueError("stagger must be 'rho' or 'w'")

    if Vtransform == 1:  # Default transform by Song and Haidvogel
        A = Hc * (S - C)[:, None]
        B = np.outer(C, H)
        return (A + B).reshape(outshape)

    elif Vtransform == 2:  # New transform by Shchepetkin
        N = Hc * S[:, None] + np.outer(C, H)
        D = (1.0 + Hc / H)
        return (N / D).reshape(outshape)

    else:
        raise ValueError("Unknown Vtransform")


# ------------------------
#   Sampling routines
# ------------------------


def z2s(z_w, X, Y, Z):
    """
    Find s-level and coefficients for vertical interpolation

    input: X, Y, Z is 3D position, Z positive

    Returns K and A where:

    K is a 2D integer array such that
       -H  <= z_w[K] <= -Z < z_w[K+1] <= 0

    A is a 2D float array such that
        -Z = A*z_rho[K] + (1-A)*z_rho[K+1]

    """

    kmax = z_w.shape[0] - 1  # Number of vertical
    # jmax, imax = z_w.shape[1:]  # Number of horizontal cells

    # Find rho-based horizontal grid cell
    # i.e. closest rho-point
    I = np.around(X).astype('int')
    J = np.around(Y).astype('int')

    K = np.sum(z_w[:, J, I] < -Z, axis=0) - 1
    K = K.clip(0, kmax - 1)

    A = (z_w[K + 1, J, I] + Z) / (z_w[K + 1, J, I] - z_w[K, J, I])
    A = A.clip(0, 1)

    return K, A


def sample3D(F, X, Y, K, A, method='bilinear'):
    """
    Sample a 3D field on the (sub)grid

    F = 3D field
    S = depth structure matrix
    X, Y = 1D arrays of horizontal grid coordinates
    Z = 1D array of depth [m, positive downwards]

    Everything in rho-points

    F.shape = S.shape = (kmax, jmax, imax)
    S.shape = (kmax, jmax, imax)
    X.shape = Y.shape = Z.shape = (pmax,)

    # Interpolation = 'bilinear' for trilinear Interpolation
    # = 'nearest' for value in 3D grid cell

    """

    if method == 'bilinear':
        # Find rho-point as lower left corner
        I = X.astype('int')
        J = Y.astype('int')
        P = X - I
        Q = Y - J
        W000 = (1 - P) * (1 - Q) * (1 - A)
        W010 = (1 - P) * Q * (1 - A)
        W100 = P * (1 - Q) * (1 - A)
        W110 = P * Q * (1 - A)
        W001 = (1 - P) * (1 - Q) * A
        W011 = (1 - P) * Q * A
        W101 = P * (1 - Q) * A
        W111 = P * Q * A

        return (W000 * F[K, J, I] + W010 * F[K, J + 1, I] +
                W100 * F[K, J, I + 1] + W110 * F[K, J + 1, I + 1] +
                W001 * F[K - 1, J, I] + W011 * F[K - 1, J + 1, I] +
                W101 * F[K - 1, J, I + 1] + W111 * F[K - 1, J + 1, I + 1])

    else:  # method == 'nearest'
        I = X.round().astype('int')
        J = Y.round().astype('int')
        return F[K, J, I]


def sample3DUV(U, V, X, Y, K, A, method='bilinear'):
    return (sample3D(U, X+0.5, Y, K, A, method=method),
            sample3D(V, X, Y+0.5, K, A, method=method))
