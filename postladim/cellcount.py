import numpy as np     # type:ignore
import xarray as xr    # type: ignore
from typing import Union, Optional, Tuple, List

Array = Union[List[float], np.ndarray, xr.DataArray]
Limits = Union[Tuple[int, int], Tuple[int, int, int, int]]

def cellcount(
    X: Array,
    Y: Array,
    W: Optional[Array] = None,
    grid_limits: Optional[Limits] = None,
) -> xr.DataArray:
    """Count the (weighted) number of particles in grid cells

    Parameters
    ----------
    X, Y : 1D arrays, length = n
        Particle position in grid coordinates
    W : 1D array, length = n
        Weight of particles, default=None for unweighted
    grid_limits : 4-tuple (i0, i1, j0, j1) or 2-tuple (i1, j1)
        Limitation of grid to consider,
        If 2-tuple, i0 and j0 default to zero.
        Default=None gives the bounding box of the particle positions

    Returns
    -------
    C : 2D xarray.DataArray, shape = (j1-j0, i1-i0)
        Particle counts

    Note: particles outside the grid limits are silently ignored

    """

    # Possible improvement.
    #   If xarray is not installed, return a numpy.ndarray

    # X = np.asarray(X)
    # Y = np.asarray(Y)

    # Subgrid specification

    i0: int
    i1: int
    j0: int
    j1: int

    if grid_limits is None:
        i0 = int(round(np.min(X)))
        i1 = int(round(np.max(X))) + 1
        j0 = int(round(np.min(Y)))
        j1 = int(round(np.max(Y))) + 1
    elif len(grid_limits) == 2:
        i1, j1 = grid_limits
        i0, j0 = 0, 0
    elif len(grid_limits) == 4:
        i0, i1, j0, j1 = grid_limits
    else:
        raise TypeError("Illegal grid_limits")

    # Count
    x_edges = np.arange(i0 - 0.5, i1)
    y_edges = np.arange(j0 - 0.5, j1)
    if W is None:
        C = np.histogram2d(Y, X, bins=[y_edges, x_edges])
    else:
        C = np.histogram2d(Y, X, weights=W, bins=[y_edges, x_edges])

    coords = dict(Y=np.arange(j0, j1), X=np.arange(i0, i1))
    C = xr.DataArray(C[0], coords=coords, dims=coords.keys())

    return C
