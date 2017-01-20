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

alogger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
alogger.addHandler(ch)


class Grid(object):

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
    >>> Vinfo = {'N' : 32, 'hc' : 10, 'theta_s' : 0.8, 'theta_b' : 0.4}
    >>> grd = SGrid(fid, subgrid=(100, 121, 60, 161), Vinfo=Vinfo)

    """

    # Lagrer en del unødige attributter

    def __init__(self, grid_file, subgrid=[], Vinfo=None, Vfile=None):

        try:
            ncid = Dataset(grid_file)
        except OSError:
            alogger.error('Grid file {} not found'.format(grid_file))
            raise SystemExit(1)

        # Subgrid, only considers internal grid cells
        # 1 <= i0 < i1 <= imax-1, default=end points
        # 1 <= j0 < j1 <= jmax-1, default=end points
        jmax, imax = ncid.variables['h'].shape
        whole_grid = [1, imax-1, 1, jmax-1]
        if subgrid:
            limits = list(subgrid)
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

        if Vinfo:
            Vinfo = self._Vinfo
            self.N = Vinfo['N']
            self.hc = Vinfo['hc']
            self.Vstretching = Vinfo.get('Vstretching', 1)
            self.Vtransform = Vinfo.get('Vtransform', 1)
            self.Cs_r = s_stretch(self.N, Vinfo['theta_s'], Vinfo['theta_b'],
                                  stagger='rho', Vstretching=self.Vstretching)
            self.Cs_w = s_stretch(self.N, Vinfo['theta_s'], Vinfo['theta_b'],
                                  stagger='w', Vstretching=self.Vstretching)
        else:
            if Vfile:
                f0 = Dataset(self._Vfile)  # separate file
            else:
                f0 = ncid                  # use the file itself

            try:
                self.hc = f0.variables['hc'].getValue()
            except KeyError:
                print("No vertical information")
                raise SystemExit(3)

            self.Cs_r = f0.variables['Cs_r'][:]
            self.Cs_w = f0.variables['Cs_w'][:]

            # Vertical grid size
            self.N = len(self.Cs_r)

            # Vertical transform
            try:
                self.Vtransform = f0.variables['Vtransform'].getValue()
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
        if f0 != ncid:
            f0.close()
        ncid.close()

# --------------------------------------------------------

    #
    #     # Shape of the grid
    #     self.shape = (self.j1-self.j0, self.i1-self.i0)
    #

    #     # Grid cell centers
    #     self.X = np.arange(self.i0, self.i1)
    #     self.Y = np.arange(self.j0, self.j1)
    #     # Grid cell boundaries = psi-points
    #     self.Xb = np.arange(self.i0-0.5, self.i1)
    #     self.Yb = np.arange(self.j0-0.5, self.j1)
    #
    # # ------------------------------------
    #
    #
    #         # Close separate file
    #         if self._Vfile:
    #             f0.close()
    #
    # # --------------
    # # Lazy reading
    # # ---------------
    #
    # # Some 2D fields from the file
    # # Only read if (and when) needed
    #
    # # Doing the following for a list of fields
    # # @_Lazy
    # # def field(self):
    # #     return self.ncid.variables['field'][self.J, self.I]
    #
    # for _field in ['h', 'mask_rho', 'lon_rho', 'lat_rho',
    #                'pm', 'pn', 'angle', 'f']:
    #     exec("%s = lambda self: self.ncid.variables['%s'][self.J, self.I]"
    #          % (_field, _field))
    #     exec("%s = _Lazy(%s)" % (_field, _field))
    #
    # # 3D depth structure
    # @_Lazy
    # def z_r(self):
    #     if self.vertical:
    #         return sdepth(self.h, self.hc, self.Cs_r,
    #                       stagger='rho', Vtransform=self.Vtransform)
    #
    # @_Lazy
    # def z_w(self):
    #     if self.vertical:
    #         return sdepth(self.h, self.hc, self.Cs_w,
    #                       stagger='w', Vtransform=self.Vtransform)
    #
    # # ---------------------------------
    # # Wrappers for romsutil functions
    # # ---------------------------------
    #
    # def zslice(self, F, z):
    #     if self.vertical:
    #         return zslice(F, self.z_r, -abs(z))
    #
    # def xy2ll(self, x, y):
    #     return (sample2D(self.lon_rho, x-self.i0, y-self.j0),
    #             sample2D(self.lat_rho, x-self.i0, y-self.j0))
    #
    # def ll2xy(self, lon, lat):
    #     y, x = bilin_inv(lon, lat, self.lon_rho, self.lat_rho)
    #     return x + self.i0, y + self.j0
