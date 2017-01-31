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
# import numpy as np
from netCDF4 import Dataset

from roppy import s_stretch, sdepth
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

    Typical usage::

    >>> fid = Dataset(roms_file)
    >>> grd = SGrid(fid)

    More arguments::

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
        self.M = ncid.variables['mask_rho'][self.J, self.I]
        self.pm = ncid.variables['pm'][self.J, self.I]
        self.pn = ncid.variables['pn'][self.J, self.I]
        self.lon = ncid.variables['lon_rho'][self.J, self.I]
        self.lat = ncid.variables['lat_rho'][self.J, self.I]

        self.z_r = sdepth(self.H, self.hc, self.Cs_r,
                          stagger='rho', Vtransform=self.Vtransform)
        self.z_w = sdepth(self.H, self.hc, self.Cs_w,
                          stagger='w', Vtransform=self.Vtransform)

        # Close the file(s)
        ncid.close()

    def sample_metric(self, X, Y):
        """Sample the metric coefficients

        Changes slowly, so using neareast neighbour
        """
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0

        # Metric is conform for PolarStereographic
        A = self.pm[J, I]
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

    # Feil ?, skal være pluss
    def ingrid(self, X, Y):
        """Returns True for points inside the subgrid"""
        return ((self.i0-0.5 <= X) & (X <= self.i1-0.5) &
                (self.j0-0.5 <= Y) & (Y <= self.j0-0.5))

    def onland(self, X, Y):
        """Returns True for points on land"""
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0
        return (self.M[J, I] < 1)

    # Funker ikke ??
    def atsea(self, X, Y):
        """Returns True for points at sea"""
        I = X.round().astype(int) - self.i0
        J = Y.round().astype(int) - self.j0
        return (self.M[J, I] > 0)
