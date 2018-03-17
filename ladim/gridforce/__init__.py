
# Main gridforce controller

import os
import sys
import importlib

# from ladim.configuration import config


class Grid:

    def __init__(self, config):
        # Allow gridforce module in current directory
        sys.path.insert(0, os.getcwd())
        # Import correct gridforce_module
        gridforce_module = importlib.import_module(config['gridforce_module'])
        self.grid = gridforce_module.Grid(config)
        self.xmin = self.grid.xmin
        self.xmax = self.grid.xmax
        self.ymin = self.grid.ymin
        self.ymax = self.grid.ymax

    def sample_metric(self, X, Y):
        """Sample the metric coefficients"""
        return self.grid.sample_metric(X, Y)

    def sample_depth(self, X, Y):
        """Return the depth of grid cells"""
        return self.grid.sample_depth(X, Y)

    def lonlat(self, X, Y):
        """Return the longitude and latitude from grid coordinates"""
        return self.grid.lonlat(X, Y)

    def ingrid(self, X, Y):
        """Returns True for points inside the subgrid"""
        return self.grid.ingrid(X, Y)

    def onland(self, X, Y):
        """Returns True for points on land"""
        return self.grid.onland(X, Y)

    # Error if point outside
    def atsea(self, X, Y):
        """Returns True for points at sea"""
        return self.grid.atsea(X, Y)

    def ll2xy(self, lon, lat):
        return self.grid.ll2xy(lon, lat)

    def xy2ll(self, X, Y):
        return self.grid.ll2xy(X, Y)


class Forcing:

    def __init__(self, config, grid, **args):
        # Allow gridforce module in current directory
        sys.path.insert(0, os.getcwd())
        # Import correct gridforce_module
        gridforce_module = importlib.import_module(config['gridforce_module'])
        self.forcing = gridforce_module.Forcing(config, grid.grid, **args)
        # self.steps = self.forcing.steps
        # self.U = self.forcing.U
        # self.V = self.forcing.V

    def update(self, t):
        return self.forcing.update(t)

    def velocity(self, X, Y, Z, tstep=0.0):
        return self.forcing.velocity(X, Y, Z, tstep=tstep)

    def field(self, X, Y, Z, name):
        return self.forcing.field(X, Y, Z, name)

    def close(self):
        return self.forcing.close()
