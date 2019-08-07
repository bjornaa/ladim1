import numpy as np


def cellcount(X, Y, W=None, gridspec=None, return_edges=False):
    """Count the (weighted) number of particles in grid cells

    Parameters
    ----------
    X, Y : 1D arrays, length = n
        Particle position in grid coordinates
    W : 1D array, length = n
        Weight of particles, default=None for unweighted
    gridspec : 4-tuple (i0, i1, j0, j1)
        Limitation of grid to consider,
        Default=None gives the bounding box of the particles
    return_edges : boolean
        If True: returns x_edges and y_edges suitable for pcolor plot
        Default = False
    Returns
    -------
    C : 2D array, shape = (j1-j0, i1-i0)
        Particle counts

    """

    # Subgrid specification
    if gridspec is None:
        i0 = int(round(X.min()))
        i1 = int(round(X.max())) + 1
        j0 = int(round(Y.min()))
        j1 = int(round(Y.max())) + 1
    else:
        i0, i1, j0, j1 = gridspec
    # imax = i1-i0
    # jmax = j1-j0
    # C = np.zeros((jmax, imax))

    # Count
    x_edges = np.arange(i0 - 0.5, i1)
    y_edges = np.arange(j0 - 0.5, j1)
    if W is None:
        C = np.histogram2d(Y, X, bins=[y_edges, x_edges])
    else:
        C = np.histogram2d(Y, X, weights=W, bins=[y_edges, x_edges])

    if return_edges is True:
        return C[0], x_edges, y_edges
    else:
        return C[0]
