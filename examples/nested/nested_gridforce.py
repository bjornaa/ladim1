import numpy as np
from netCDF4 import Dataset
from ladim.gridforce import ROMS
from ladim.sample import sample2D


class Grid(object):

    def __init__(self, config):

        # Make a virtual grid, subgrid of original
        i0, i1 = 80, 175
        j0, j1 = 30, 110

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
        self.coarse_config = coarse_config
        print("Coarse grid OK")

        # Initiate fine grid
        # subgrid: i0, i1 = 135, 172, j0, j1 = 42, 81 of orginal
        fine_config = config.copy()
        fine_config['grid_file'] = 'forcing_skagerrak.nc'
        coarse_config['input_file'] = 'forcing_skagerrak.nc'
        self.fine_grid = ROMS.Grid(fine_config)
        self.fine_config = fine_config
        print("Fine grid OK")

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

    # NOTE: Could perhaps be developed into a decorator
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

    def sample_depth(self, X, Y):
        return self.delegate(X, Y, 'sample_depth')

    def lonlat(self, X, Y):
        """Return the longitude and latitude from grid coordinates"""
        return (sample2D(self.lon, X, Y),
                sample2D(self.lat, X, Y))

    def ingrid(self, X, Y):
        # Hva med endepunkyrt i C-grid, er her konservativ
        # utelukker siste grid-celle
        """Returns True for points inside the subgrid"""
        return ((0.5 <= X) & (X <= self.imax-1.5) &
                (0.5 <= Y) & (Y <= self.jmax-1.5))

    def onland(self, X, Y):
        return self.delegate(X, Y, 'onland') > 0.5

    def atsea(self, X, Y):
        return self.delegate(X, Y, 'atsea') > 0.5


class Forcing:

    def __init__(self, config, grid):

        # May adjust coonfig
        self.coarse_forcing = ROMS.Forcing(
            grid.coarse_config, grid.coarse_grid)
        print("Coarse forcing OK")

        self.fine_forcing = ROMS.Forcing(
            grid.fine_config, grid.fine_grid)
        print("Fine forcing OK")

        # steps, hva gjøres her. Enkelt hvis samme
        # Anta: fine step deler grove
        # F.eks. fin hver time, grov hver tredje.
        # Bruk fine steg.s
        self.steps = self.fine_forcing.steps
        self._grid = grid

    # Note: cleaner with name first?
    # Tidskontroll?
    def field(self, X, Y, Z, name):
        grid = self._grid
        X, Y = np.asarray(X), np.asarray(Y)
        X1, Y1 = grid.xy2fine(X, Y)
        fine = grid.fine_grid.ingrid(X1, Y1)
        # need more conservative ingrid?
        X1, Y1 = grid.xy2fine(X[fine], Y[fine])
        Z1 = Z[fine]
        X2, Y2= grid.xy2coarse(X[~fine], Y[~fine])
        Z2 = Z[~fine]

        A = np.empty(len(X), dtype=float)
        A[fine] = self.fine_forcing.field(X1, Y1, Z1, name)
        A[~fine] = self.coarse_forcing.field(X2, Y2, Z2, name)
        return A

    def velocity(self, X, Y, Z, tstep=0):
        print("Starting velocity")
        grid = self._grid
        X, Y = np.asarray(X), np.asarray(Y)
        X1, Y1 = grid.xy2fine(X, Y)
        fine = grid.fine_grid.ingrid(X1, Y1)
        # need more conservative ingrid?
        X1, Y1 = grid.xy2fine(X[fine], Y[fine])
        Z1 = Z[fine]
        X2, Y2= grid.xy2coarse(X[~fine], Y[~fine])
        Z2 = Z[~fine]

        U = np.empty(len(X), dtype=float)
        V = np.empty(len(X), dtype=float)
        print("Foran fimne")
        U[fine], V[fine] = self.fine_forcing.velocity(
            X1, Y1, Z1, tstep=tstep)
        print("U fine OK")
        U[~fine], V[~fine] = self.coarse_forcing.velocity(
            X2, Y2, Z2, tstep=tstep)
        return U, V