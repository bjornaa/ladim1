"""
Grid class for LADIM, simplified from roppy

"""

# -----------------------------------
# Bjørn Ådlandsvik, <bjorn@imr.no>
# Institute of Marine Research
# Bergen, Norway
# 2010-09-30
# -----------------------------------

# import sys
import logging
import numpy as np
from netCDF4 import Dataset

# from ladim.sample_roms import s_stretch, sdepth
# from roppy import s_stretch, sdepth
# from roppy.depth import sdepth, zslice, s_stretch
# from roppy.sample import sample2D, bilin_inv
# import ladim.sample_roms as sample_roms
from ladim.sample import sample2D

alogger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
alogger.addHandler(ch)


# Make this a ROMS_grid class
# Inherit from a more general grid class
class Grid:

    """Simple ROMS grid object

    Simple, minimal ROMS 3D grid object, for keeping important
    information together.

    Note: Can not (yet) be initialized from a standard grd-file,
    use initial, history or average file or supply extra vertical
    information by Vinfo or Vfile.

    >>> fid = Dataset(roms_file)
    >>> Vinfo = {'N': 32, 'hc': 10, 'theta_s': 0.8, 'theta_b': 0.4}
    >>> grd = SGrid(fid, subgrid=(100, 121, 60, 161), Vinfo=Vinfo)

    """

    # Lagrer en del unødige attributter

    def __init__(self, config):
        # def __init__(self, grid_file, subgrid=[], Vinfo=None, Vfile=None):

        try:
            ncid = Dataset(config.grid_file)
        except OSError:
            alogger.error('Grid file {} not found'.format(config.grid_file))
            raise SystemExit(1)

        # Subgrid, only considers internal grid cells
        # 1 <= i0 < i1 <= imax-1, default=end points
        # 1 <= j0 < j1 <= jmax-1, default=end points
        # Here, imax, jmax refers to whole grid
        jmax, imax = ncid.variables['h'].shape
        whole_grid = [1, imax-1, 1, jmax-1]
        if config.subgrid:
            limits = list(config.subgrid)
        else:
            limits = whole_grid
        # Allow None if no imposed limitation
        for ind, val in enumerate(limits):
            if val is None:
                limits[ind] = whole_grid[ind]

        self.i0, self.i1, self.j0, self.j1 = limits
        self.imax = self.i1 - self.i0
        self.jmax = self.j1 - self.j0
        print('Grid : imax, jmax, size = ',
              self.imax, self.jmax, self.imax*self.jmax)

        # Slices
        #   rho-points
        self.I = slice(self.i0, self.i1)
        self.J = slice(self.j0, self.j1)
        #   U and V-points
        self.Iu = slice(self.i0-1, self.i1)
        self.Ju = self.J
        self.Iv = self.I
        self.Jv = slice(self.j0-1, self.j1)

        # Vertical grid

        if config.Vinfo:
            Vinfo = config.Vinfo
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
                self.Vtransform = 1   # Default = old way

        # Read some variables
        self.H = ncid.variables['h'][self.J, self.I]
        self.M = ncid.variables['mask_rho'][self.J, self.I].astype(int)
        # self.Mu = ncid.variables['mask_u'][self.Ju, self.Iu]
        # self.Mv = ncid.variables['mask_v'][self.Jv, self.Iv]
        self.dx = 1./ncid.variables['pm'][self.J, self.I]
        self.dy = 1./ncid.variables['pn'][self.J, self.I]
        self.lon = ncid.variables['lon_rho'][self.J, self.I]
        self.lat = ncid.variables['lat_rho'][self.J, self.I]

        self.z_r = sdepth(self.H, self.hc, self.Cs_r,
                          stagger='rho', Vtransform=self.Vtransform)
        self.z_w = sdepth(self.H, self.hc, self.Cs_w,
                          stagger='w', Vtransform=self.Vtransform)

        # Land masks at u- and v-points
        M = self.M
        Mu = np.zeros((self.jmax, self.imax+1), dtype=int)
        Mu[:, 1:-1] = M[:, :-1] * M[:, 1:]
        Mu[:, 0] = M[:, 0]
        Mu[:, -1] = M[:, -1]
        self.Mu = Mu

        Mv = np.zeros((self.jmax+1, self.imax), dtype=int)
        Mv[1:-1, :] = M[:-1, :] * M[1:, :]
        Mv[0, :] = M[0, :]
        Mv[-1, :] = M[-1, :]
        self.Mv = Mv

        # Close the file(s)
        ncid.close()

    def sample_metric(self, X, Y):
        """Sample the metric coefficients

        Changes slowly, so using neareast neighbour
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

    def lonlat(self, X, Y):
        """Return the longitude and latitude from grid coordinates"""
        return (sample2D(self.lon, X-self.i0, Y-self.j0),
                sample2D(self.lat, X-self.i0, Y-self.j0))

    def ingrid(self, X, Y):
        """Returns True for points inside the subgrid"""
        return ((self.i0-0.5 <= X) & (X <= self.i1-0.5) &
                (self.j0-0.5 <= Y) & (Y <= self.j0-0.5))

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
        S = -1.0 + (0.5+np.arange(N))/N
    elif stagger == "w":
        S = np.linspace(-1.0, 0.0, N+1)
    else:
        raise ValueError("stagger must be 'rho' or 'w'")

    if Vstretching == 1:
        cff1 = 1.0 / np.sinh(theta_s)
        cff2 = 0.5 / np.tanh(0.5*theta_s)
        return ((1.0-theta_b)*cff1*np.sinh(theta_s*S) +
                theta_b*(cff2*np.tanh(theta_s*(S+0.5))-0.5))

    elif Vstretching == 2:
        a, b = 1.0, 1.0
        Csur = (1 - np.cosh(theta_s * S))/(np.cosh(theta_s) - 1)
        Cbot = np.sinh(theta_b * (S+1)) / np.sinh(theta_b) - 1
        mu = (S+1)**a * (1 + (a/b)*(1-(S+1)**b))
        return mu*Csur + (1-mu)*Cbot

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
    >>> H = fid.variables['h'][:,:]
    >>> C = fid.variables['Cs_r'][:]
    >>> Hc = fid.variables['hc'].getValue()
    >>> z_rho = sdepth(H, Hc, C)

    """
    H = np.asarray(H)
    Hshape = H.shape      # Save the shape of H
    H = H.ravel()         # and make H 1D for easy shape maniplation
    C = np.asarray(C)
    N = len(C)
    outshape = (N,) + Hshape       # Shape of output
    if stagger == 'rho':
        S = -1.0 + (0.5+np.arange(N))/N    # Unstretched coordinates
    elif stagger == 'w':
        S = np.linspace(-1.0, 0.0, N)
    else:
        raise ValueError("stagger must be 'rho' or 'w'")

    if Vtransform == 1:         # Default transform by Song and Haidvogel
        A = Hc * (S - C)[:, None]
        B = np.outer(C, H)
        return (A + B).reshape(outshape)

    elif Vtransform == 2:       # New transform by Shchepetkin
        N = Hc*S[:, None] + np.outer(C, H)
        D = (1.0 + Hc/H)
        return (N/D).reshape(outshape)

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

    kmax = z_w.shape[0]-1          # Number of vertical
    jmax, imax = z_w.shape[1:]     # Number of horizontal cells

    # Find rho-based horizontal grid cell
    # i.e. closest rho-point
    I = np.around(X).astype('int')
    J = np.around(Y).astype('int')

    K = np.sum(z_w[:, J, I] < -Z, axis=0) - 1
    K = K.clip(0, kmax-1)

    A = (z_w[K+1, J, I] + Z) / (z_w[K+1, J, I] - z_w[K, J, I])
    A = A.clip(0, 1)

    return K, A


def sample3D(F, X, Y, K, A, method='bilinear'):
    """
    Sample a 3D field on the (sub)grid

    F = 3D field
    S = depth structure matrix
    X, Y = 1D arrays of horizontal grid coordinates
    Z = 1D arryay of depth [m, positive downwards]

    Everything in rho-points

    F.shape = S.shape = (kmax, jmax, imax)
    S.shape = (kmax, jmax, imax)
    X.shape = Y.shape = Z.shape = (pmax,)

    # Interpolation = 'bilinear' for trilinear Interpolation
    # = 'nearest' for value in 3D grid cell

    """

    # print('sample3D: method =', method)

    if method == 'bilinear':
        # Find rho-point as lower left corner
        I = X.astype('int')
        J = Y.astype('int')
        P = X - I
        Q = Y - J
        W000 = (1-P)*(1-Q)*(1-A)
        W010 = (1-P)*Q*(1-A)
        W100 = P*(1-Q)*(1-A)
        W110 = P*Q*(1-A)
        W001 = (1-P)*(1-Q)*A
        W011 = (1-P)*Q*A
        W101 = P*(1-Q)*A
        W111 = P*Q*A

        return (W000*F[K, J, I] + W010*F[K, J+1, I] +
                W100*F[K, J, I+1] + W110*F[K, J+1, I+1] +
                W001*F[K-1, J, I] + W011*F[K-1, J+1, I] +
                W101*F[K-1, J, I+1] + W111*F[K-1, J+1, I+1])

    else:   # method == 'nearest'
        I = X.round().astype('int')
        J = Y.round().astype('int')
        return F[K, J, I]


def sample3DUV(U, V, X, Y, K, A, method='bilinear'):
    return (sample3D(U, X-0.5, Y, K, A, method=method),
            sample3D(V, X, Y-0.5, K, A, method=method))
