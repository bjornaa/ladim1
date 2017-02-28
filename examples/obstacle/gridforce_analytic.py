import numpy as np


class Grid:

    def __init__(self, config):
        km = 1000           # abbrev
        L = 100*km          # Length of channel [m]
        W = 50*km           # Width of channel [m]
        self.dx = 1*km      # Grid spacing along channel [m]
        self.dy = 1*km      # Grid spacing cross channel [m]
        X0 = 0.5*L          # Center location of peninsular obstacle [m]
        R = 0.32*W          # Radius of peninsular obstacle [m]
        self.H = 100        # Depth of channel [m]
        self.U0 = 1         # Undisturbed along-channel velocity [m/s]

        # Convert to grid coordinates
        self.imax = L / self.dx
        self.jmax = W / self.dy
        self.X0 = X0 / self.dx
        self.R = R / self.dy
        print("R", self.R)

    def sample_metric(self, X, Y):
        return self.dx + np.zeros_like(X), self.dy + np.zeros_like(Y)

    def sample_depth(self, X, Y):
        return self.H + np.zeros_like(X)

    def atsea(self, X, Y):
        # return (X-X0)**2 + Y**2 > R**2
        return np.ones_like(X, dtype='bool')


class Forcing:
    def __init__(self, config, grid):
        self.grid = grid

    def velocity(self, X, Y, Z, tstep=0):
        X0 = self.grid.X0
        U0 = self.grid.U0
        R = self.grid.R
        denom = ((X - X0) ** 2 + Y ** 2) ** 2
        U = U0 - U0 * R ** 2 * ((X - X0) ** 2 - Y ** 2) / denom
        V = - 2 * U0 * R ** 2 * (X - X0) * Y / denom
        return U, V

    def update(self, step):
        pass

    def close(self):
        pass
