import numpy as np
from ladim.gridforce import ROMS
from ladim.sample import sample2D


class Grid(object):

    def __init__(self, config):

        # Make a virtual grid, subgrid of original
        i0, i1 = 80, 175
        j0, j1 = 30, 100

        self._i0 = i0
        self._j0 = j0

        self.imax = i1 - i0
        self.jmax = j1 - j0

        # Geographic coordinates
        # Not generally available from real grids
        # For this example, get from original
        #
        # dx and dy can be estimated from lon/lat
        # but for the example use the original grid
        from netCDF4 import Dataset
        orig_file = '../data/ocean_avg_0014.nc'
        with Dataset(orig_file) as nc:
            self.lon = nc.variables['lon_rho'][j0: j1, i0: i1]
            self.lat = nc.variables['lat_rho'][j0: j1, i0: i1]
            self.dx = 1. / nc.variables['pm'][j0: j1, i0: i1]
            self.dy = 1. / nc.variables['pn'][j0: j1, i0: i1]

        # Initiate coarse grid
        # Original grid, subsampled 3x3
        coarse_config = config.copy()
        coarse_config['grid_file'] = 'forcing_northsea.nc'
        coarse_config['input_file'] = 'forcing_northsea.nc'
        self.coarse_grid = ROMS.Grid(coarse_config)

        # Initiate fine grid
        # subgrid: i0, i1 = 135, 172, j0, j1 = 42, 81 of orginal
        fine_config = config.copy()
        fine_config['grid_file'] = 'forcing_skagerrak.nc'
        coarse_config['input_file'] = 'forcing_skagerrak.nc'
        self.fine_grid = ROMS.Grid(fine_config)

    # Must manually define transformation from virtual to real grids
    def xy2fine(self, X, Y):
        X, Y = np.asarray(X), np.asarray(Y)
        return X + self._i0 - 135, Y + self._j0 - 42

    def xy2coarse(self, X, Y):
        X, Y = np.asarray(X), np.asarray(Y)
        return (X + self._i0 - 1) / 3, (Y + self._j0 - 1) / 3

    def sample_metric(self, X, Y):
        """Sample the metric coefficients

        Changes slowly, so using neareast neighbour
        """
        I = X.round().astype(int)
        J = Y.round().astype(int)

        return self.dx[J, I], self.dy[J, I]

    # Could perhaps be developed into a decorator
    def delegate(self, X, Y, method):
        """Delegate computation of field to the real grids"""
        X, Y = np.asarray(X), np.asarray(Y)
        X1, Y1 = self.xy2fine(X, Y)
        fine = self.fine_grid.ingrid(X1, Y1)
        # need more conservative ingrid?
        X1, Y1 = X1[fine], Y1[fine]
        X2, Y2 = self.xy2coarse(X[~fine], Y[~fine])

        A = np.empty(len(X), dtype=float)
        A[fine] = getattr(self.fine_grid, method)(X1, Y1)
        A[~fine] = getattr(self.coarse_grid, method)(X2, Y2)
        return A

    def sample_depth2(self, X, Y):
        X, Y = np.asarray(X), np.asarray(Y)
        H = np.empty_like(X)
        X1, Y1 = self.xy2fine(X, Y)
        fine = self.fine_grid.ingrid(X1, Y1)
        X1, Y1 = X1[fine], Y1[fine]
        H[fine] = self.fine_grid.sample_depth(X1, Y1)
        # Funker det under selv om alle partikler i fine område?
        X2, Y2 = self.xy2coarse(X[~fine], Y[~fine])
        H[~fine] = self.coarse_grid.sample_depth(X2, Y2)
        return H

    # Lag litt tester, se at dette fungerer.
    def sample_depth(self, X, Y):
        return self.delegate(X, Y, 'sample_depth')

    # Unødig, siden virtuelle grid har lon/lat ?
    # vil ikke gi nøyaktig samme verdier, avrundingsfeil
    def lonlat2(self, X, Y):
        """Return the longitude and latitude from grid coordinates"""
        lon = np.empty(len(X), dtype=float)
        lat = np.empty(len(X), dtype=float)
        X1, Y1 = self.xy2fine(X, Y)
        fine = self.fine_grid.ingrid(X1, Y1)
        lon[fine], lat[fine] = self.fine_grid.lonlat(X1[fine], Y1[fine])
        X2, Y2 = self.xy2coarse(X[~fine], Y[~fine])
        lon[~fine], lat[~fine] = self.coarse_grid.lonlat(X2, Y2)
        return lon, lat

    def lonlat(self, X, Y):
        """Return the longitude and latitude from grid coordinates"""
        return (sample2D(self.lon, X, Y),
                sample2D(self.lat, X, Y))

    def ingrid(self, X, Y):
        # Hva med endepunkyrt i C-grid, er her konservativ
        # utelukker siste grid-celle
        """Returns True for points inside the subgrid"""
        return ((0.5 <= X) & (X <= imax-1.5) &
                (0.5 <= Y) & (Y <= jmax-1.5))

    def onland(self, X, Y):
        return self.delegate(X, Y, 'onland') > 0.5

    def atsea(self, X, Y):
        return self.delegate(X, Y, 'atsea') > 0.5
