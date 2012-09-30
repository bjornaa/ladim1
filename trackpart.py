
import numpy as np
#import matplotlib.pyplot as plt
#from netCDF4 import Dataset

#from roppy import SGrid, sample2DU, sample2DV
#from roppy import SGrid, sample2D
from roppy import sample2D

# ---------------------

def Euler_Forward(grid, U, V, X, Y, dt=3600, nstep=1):
    """Particle tracking with Euler Forward method

    grid   : SGrid object
    U, V   : 2D Current field
    X0, Y0 : 1D arrays with grid coordinates of start positions
    dt     : timestep [seconds]
    nstep  : number of time steps

    Move particles in a time independent horizontal current field,
    grid must (presently) be a subgrid (i0, i1, j0, j1)
    U must be sliced to the grid 
    Domain is limited by: i0 <= x < i1-1 and j0 <= y < j1-1
    Particles outside the domain are not moved

"""
    i0, i1, j0, j1 = grid.i0, grid.i1, grid.j0, grid.j1

    # Initalize
    #X = np.zeros((nstep, len(X0)))
    #Y = np.zeros((nstep, len(X0)))
    #X[0,:] = X0
    #Y[0,:] = Y0

     
    pm = sample2D(grid.pm, X[:]-i0, Y[:]-j0)
    pn = sample2D(grid.pn, X[:]-i0, Y[:]-j0)

    # Particle tracking loop

    for t in xrange(nstep):
        Up = sample2D(U, X[:]-i0+0.5, Y[:]-j0)
        Vp = sample2D(V, X[:]-i0, Y[:]-j0+0.5)
        #X[:] = X[:] + Up * dt * pm
        X += Up * dt* pm
        Y[:] = Y[:] + Vp * dt * pn

        print X[0], Y[0], Up[0], Vp[0]
    return X, Y

