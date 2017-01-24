
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


class TrackPart():

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





# def Euler_Forward(config, U, V, X, Y, Z, dt=3600, nstep=1):
#
#     """Particle tracking with Euler Forward method
#     grid   : SGrid object
#     U, V   : 3D horizontal current field
#     X0, Y0 : 1D arrays with grid coordinates of start positions
#     dt     : timestep [seconds]
#     nstep  : number of time steps
#
#     Move particles in a time independent horizontal current field,
#     grid must (presently) be a subgrid (i0, i1, j0, j1)
#     U must be sliced to the grid
#     Domain is limited by: i0 <= x < i1-1 and j0 <= y < j1-1
#     Particles outside the domain are not moved
#
# """
#     grid = config.grid
#     i0, i1, j0, j1 = grid.i0, grid.i1, grid.j0, grid.j1
#
#     pm = sample2D(grid.pm, X[:]-i0, Y[:]-j0)
#     pn = sample2D(grid.pn, X[:]-i0, Y[:]-j0)
#
#     # Particle tracking loop
#
#     # TODO:  Handle i0, j0 properly
#     # include it in the sample routines
#     for t in range(nstep):
#         K, A = Z2S(grid.z_r, X-i0, Y-j0, Z)
#         Up, Vp = config.grid.sample3DUV(U, V, X, Y, K, A)
#         # Up = sample2D(U[-1,:,:], X[:]-i0+0.5, Y[:]-j0)
#         # Vp = sample2D(V[-1,:,:], X[:]-i0, Y[:]-j0+0.5)
#
#         X += Up * dt * pm
#         Y += Vp * dt * pn
#
#     return X, Y
