import numpy as np
from numpy import pi, exp, sin, cos


class Grid:
    def __init__(self, config):
        km = 1000
        self.lambda_ = 10000 * km  # West-east extent of domain             [m]
        self.b = 6300 * km  #       South-north extent of domain           [m]
        self.D = 200

        self.imax = 101
        self.jmax = 64
        self.dx = 100 * km

        self.xmin = 0.0
        self.ymin = 0.0
        self.xmax = self.lambda_
        self.ymax = self.b

    def sample_metric(self, X, Y):
        return np.ones_like(X), np.ones_like(X)

    def sample_depth(self, X, Y):
        return self.D + np.zeros_like(X)

    def atsea(self, X, Y):
        return np.ones_like(X, dtype="bool")

    def ingrid(self, X, Y):
        return (0 <= X) & (X <= self.lambda_) & (0 <= Y) & (Y < self.b)


class Forcing:
    def __init__(self, config, grid):
        self.grid = grid

        km = 1000.0  #                                                  [m]
        D = grid.D  #  Depth                                  [m]
        r = 1.0e-6  #           Bottom friction coefficient            [s-1]
        beta = 1.0e-11  #       Coriolis derivative                    [m-1 s-1]
        alfa = beta / r  #                                             [m-1]
        lambda_ = grid.lambda_  # West-east extent of domain             [m]
        b = grid.b  #        South-north extent of domain           [m]
        F = 0.1  #              Wind stress amplitude                  [N m-2]
        rho = 1025.0  #         Density [kg/m3]

        gamma = F * pi / (r * b)  #                                    [kg m2 s-1]
        G = (1 / rho) * (1 / D) * gamma * (b / pi) ** 2  #             [m2 s-1]

        A = -0.5 * alfa + np.sqrt(0.25 * alfa ** 2 + (pi / b) ** 2)  # [m-1]
        B = -0.5 * alfa - np.sqrt(0.25 * alfa ** 2 + (pi / b) ** 2)  # [m-1]
        p = (1.0 - exp(B * lambda_)) / (exp(A * lambda_) - exp(B * lambda_))
        q = 1 - p
        self.G = G
        self.b = self.grid.b
        self.p = p
        self.q = q
        self.A = A
        self.B = B

    def velocity(self, X, Y, Z, tstep=0):
        G = self.G
        b = self.b
        p = self.p
        q = self.q
        A = self.A
        B = self.B
        U = G * (pi / b) * cos(pi * Y / b) * (p * exp(A * X) + q * exp(B * X) - 1)
        V = -G * sin(pi * Y / b) * (p * A * exp(A * X) + q * B * exp(B * X))
        return U, V

    def update(self, step):
        pass

    def close(self):
        pass
