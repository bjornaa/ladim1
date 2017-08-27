# Testing the nested_gridforce

import numpy as np
from nested_gridforce import Grid

config = dict(grid_args=[])

g = Grid(config)

# Find last point, at sea in both grids
X = np.array([10, 60])
Y = np.array([20, 40])

X1, Y1 = g.xy2fine(X, Y)
print("X1, Y1 =", X1, Y1)
X2, Y2 = g.xy2coarse(X, Y)
print("X2, Y2 = ", X2, Y2)

fine = g.fine_grid.ingrid(X1, Y1)
print('fine = ', fine)

H = g.sample_depth(X, Y)
print('depth = ', H)

H1 = g.fine_grid.sample_depth(X1[fine], Y1[fine])
print('depth1 = ', H1)

H2 = g.coarse_grid.sample_depth(X2, Y2)
print('depth1 = ', H2)

# All particles in fine
H = g.sample_depth(X[fine], Y[fine])
print("All in fine", H)

# All particles in coarse
H = g.sample_depth(X[~fine], Y[~fine])
print("All in coarse", H)

lon, lat = g.lonlat(X, Y)
print('lon, lat = ', lon, lat)