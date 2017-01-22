
# import numpy as np
# import matplotlib.pyplot as plt
# from netCDF4 import Dataset

# from roppy import SGrid, sample2DU, sample2DV
# from roppy import SGrid, sample2D
from roppy import sample2D
# from sample_roms import Z2S, sample3DU, sample3DV, sample2D
from ladim.sample_roms import Z2S
# from ladim.configuration import config

# ---------------------


def Euler_Forward(config, U, V, X, Y, Z, dt=3600, nstep=1):

    """Particle tracking with Euler Forward method
    grid   : SGrid object
    U, V   : 3D horizontal current field
    X0, Y0 : 1D arrays with grid coordinates of start positions
    dt     : timestep [seconds]
    nstep  : number of time steps

    Move particles in a time independent horizontal current field,
    grid must (presently) be a subgrid (i0, i1, j0, j1)
    U must be sliced to the grid
    Domain is limited by: i0 <= x < i1-1 and j0 <= y < j1-1
    Particles outside the domain are not moved

"""
    grid = config.grid
    i0, i1, j0, j1 = grid.i0, grid.i1, grid.j0, grid.j1

    pm = sample2D(grid.pm, X[:]-i0, Y[:]-j0)
    pn = sample2D(grid.pn, X[:]-i0, Y[:]-j0)

    # Particle tracking loop

    # TODO:  Handle i0, j0 properly
    # include it in the sample routines
    for t in range(nstep):
        K, A = Z2S(grid.z_r, X-i0, Y-j0, Z)
        Up, Vp = config.grid.sample3DUV(U, V, X, Y, K, A)
        # Up = sample2D(U[-1,:,:], X[:]-i0+0.5, Y[:]-j0)
        # Vp = sample2D(V[-1,:,:], X[:]-i0, Y[:]-j0+0.5)

        X += Up * dt * pm
        Y += Vp * dt * pn

    return X, Y
