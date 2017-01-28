
# import numpy as np
# import matplotlib.pyplot as plt
# from netCDF4 import Dataset

# from roppy import SGrid, sample2DU, sample2DV
# from roppy import SGrid, sample2D
# from roppy import sample2D
# from sample_roms import Z2S, sample3DU, sample3DV, sample2D
# from ladim.sample_roms import Z2S
# from ladim.configuration import config

# ---------------------

# TODO: Change so that advection routines returns a velocity
#       so that we can add diffusion and check landing before
#       moving


class TrackPart:

    def __init__(self, config):
        self.dt = config.dt
        if config.advection:
            self.advect = getattr(self, config.advection)
        else:
            self.advect = None

    def move(self, grid, forcing, state):

        if self.advect:
            self.advect(grid, forcing, state)

    def EF(self, grid, forcing, state):

        X, Y, Z = state['X'], state['Y'], state['Z']
        dt = self.dt
        pm, pn = grid.sample_metric(X, Y)

        U, V = forcing.sample_velocity(X, Y, Z)
        X += U * pm * dt
        Y += V * pm * dt

    def RK2(self, grid, forcing, state):

        X, Y, Z = state['X'], state['Y'], state['Z']
        dt = self.dt
        pm, pn = grid.sample_metric(X, Y)

        U, V = forcing.sample_velocity(X, Y, Z)
        X1 = X + 0.5 * U * pm * dt
        Y1 = Y + 0.5 * V * pn * dt

        U, V = forcing.sample_velocity(X1, Y1, Z, tstep=0.5)
        X += U * pm * dt
        Y += V * pn * dt

    def RK4(self, grid, forcing, state):

        X, Y, Z = state['X'], state['Y'], state['Z']
        dt = self.dt
        pm, pn = grid.sample_metric(X, Y)

        U1, V1 = forcing.sample_velocity(X, Y, Z, tstep=0.0)
        X1 = X + 0.5 * U1 * pm * dt
        Y1 = Y + 0.5 * V1 * pn * dt

        U2, V2 = forcing.sample_velocity(X1, Y1, Z, tstep=0.5)
        X2 = X + 0.5 * U2 * pm * dt
        Y2 = Y + 0.5 * V2 * pn * dt

        U3, V3 = forcing.sample_velocity(X2, Y2, Z, tstep=0.5)
        X3 = X + U3 * pm * dt
        Y3 = Y + V3 * pn * dt

        U4, V4 = forcing.sample_velocity(X3, Y3, Z, tstep=1.0)

        X += (U1 + 2*U2 + 2*U3 + U4) * pm * dt / 6.0
        Y += (V1 + 2*V2 + 2*V3 + V4) * pn * dt / 6.0
