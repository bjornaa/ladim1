import numpy as np

# Discretized version of the experiment

# --------------------
# Geometric setting
# --------------------


class Grid:

    def __init__(self, config):
        km = 1000           # abbrev
        self.L = 100*km     # Length of channel [m]
        self.W = 50*km      # Width of channel [m]
        self.dx = 1*km      # Grid spacing along channel [m]
        self.dy = 1*km      # Grid spacing cross channel [m]
        X0 = 0.5*self.L     # Center location of peninsular obstacle [m]
        R = 0.32*self.W     # Radius of peninsular obstacle [m]
        self.H = 100        # Depth of channel [m]
        self.U0 = 1         # Undisturbed along-channel velocity [m/s]

        # Convert to grid coordinates
        self.imax = int(self.L / self.dx)
        self.jmax = int(self.W / self.dy)
        self.X0 = X0 / self.dx
        self.R = R / self.dy

        # Make the sea mask
        self.II, self.JJ = np.meshgrid(
            np.arange(self.imax), np.arange(self.jmax))
        M = np.ones((self.jmax, self.imax), dtype=int)
        M[(self.II-self.X0)**2 + self.JJ**2 < self.R**2] = 0
        self.M = M

    def sample_metric(self, X, Y):
        null = np.zeros_like(X)
        return self.dx + null, self.dy + null

    def sample_depth(self, X, Y):
        # i = np.round(X).astype(int)
        # j = np.round(Y).astype(int)
        # return H*self.M[j, i]
        return self.H + np.zeros_like(X)

    def atsea(self, X, Y):
        i = np.round(X).astype(int)
        j = np.round(Y).astype(int)
        return self.M[j, i] == 1


class Forcing:

    def __init__(self, config, grid):
        denom = ((grid.II-grid.X0)**2 + grid.JJ**2)**2 + 0.00001
        self.U = grid.U0 - grid.U0*grid.R**2*(
             (grid.II-grid.X0)**2 - grid.JJ**2) / denom
        self.V = - 2*grid.U0*grid.R**2*(grid.II-grid.X0)*grid.JJ / denom

    def velocity(self, X, Y, Z, tstep=0):
        i = np.round(X).astype(int)
        j = np.round(Y).astype(int)
        return self.U[j, i], self.V[j, i]

    def update(self, step):
        pass

    def close(self):
        pass
