import pytest

# import numpy as np
# Use cellcount from cellcount2 (xarray version)
from postladim import cellcount


def test_default():
    X = [11.2, 11.8, 12.2, 12.3]
    Y = [0.8, 1.2, 1.4, 3.1]
    C = cellcount(X, Y)
    assert C.shape == (3, 2)
    assert C.sum() == len(X)  # 4
    assert (C == [[1, 2], [0, 0], [0, 1]]).all()
    assert C.sel(X=11, Y=1) == 1
    assert C.sel(X=12, Y=1) == 2
    assert C.sel(X=12, Y=3) == 1


def test_gridspec():
    X = [11.2, 11.8, 12.2, 12.3]
    Y = [0.8, 1.2, 1.4, 3.1]
    i0, i1, j0, j1 = 10, 14, 0, 2
    C = cellcount(X, Y, gridspec=(i0, i1, j0, j1))
    assert C.shape == (j1 - j0, i1 - i0)  # (2, 4)
    assert C.sum() == len(X) - 1  # 3, one point outside
    assert (C == [[0, 0, 0, 0], [0, 1, 2, 0]]).all()
    assert C.sel(X=11, Y=1) == 1
    assert C.sel(X=12, Y=1) == 2
    assert C.sel(X=11, Y=0) == 0


def test_weight():
    X = [11.2, 11.8, 12.2, 12.3]
    Y = [0.8, 1.2, 1.4, 3.1]
    W = [1, 2, 3, 4]
    C = cellcount(X, Y, W)
    assert C.shape == (3, 2)
    assert C.sum() == sum(W)
    assert (C == [[W[0], W[1] + W[2]], [0, 0], [0, W[3]]]).all()
    assert C.sel(X=11, Y=1) == W[0]
    assert C.sel(X=12, Y=1) == W[1] + W[2]
    assert C.sel(X=12, Y=3) == W[3]
