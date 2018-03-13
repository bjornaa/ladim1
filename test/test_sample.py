# Test the sampling routines

import numpy as np
from pytest import approx

from ladim.sample import *


def test_sample2D():
    """Test the bilinear sampling routine with an offset grid"""
    i0, j0 = 5, 3
    i1, j1 = 9, 6
    # Want F(x, y) = 100*x + y
    # At grid cell centers F[j,i] = 100*(i+i0) + (j+j0)
    F = np.add.outer(np.arange(j0, j1), 100*np.arange(i0, i1))
    assert(F[2,3] == 100*(3+i0) + 2+j0)
    x, y = 7.2, 4.8
    assert(sample2D(F, x-i0, y-j0) == 100*x + y)


def test_sample2DUV():
    """Test interpolation of velocity in a C-grid"""
    i0, j0 = 5, 3
    i1, j1 = 9, 6
    # Construct U, V such that U(x, y) = x and V(x, y) = y
    # Note that U, V have values at the boundaries
    U = np.outer(np.ones(j1-j0), np.arange(i0,i1+1)) - 0.5
    V = np.outer(np.arange(j0, j1+1), np.ones(i1-i0)) - 0.5

    # Test origin of the grid
    x, y = i0, j0
    u, v = sample2DUV(U, V, x-i0, y-j0)
    assert(u == i0)
    assert(v == j0)
    # Test a "random" point
    x, y = 6.8, 4.1
    u, v = sample2DUV(U, V, x-i0, y-j0)
    assert(u == x)
    assert(v == y)

    # Close to border
    ymax = j1-1.0
    x, y = 6.8, ymax-0.1
    u, v = sample2DUV(U, V, x-i0, y-j0)
    assert(u == approx(x))
    assert(v == approx(y))
