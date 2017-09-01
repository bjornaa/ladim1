# Testing the nested_gridforce

import numpy as np
from nested_gridforce import Grid

config = dict(grid_args=[])

g = Grid(config)

# Two first in fine grid, land, sea
# Two next outside, land, sea
X = np.array([60, 80, 50, 30])
Y = np.array([40, 30, 50, 20])

print("X,  Y = ", X, Y)
X1, Y1 = g.xy2fine(X, Y)
print("X1, Y1 =", X1, Y1)
X2, Y2 = g.xy2coarse(X, Y)
print("X2, Y2 = ", X2.round(2), Y2.round(2))

fine = g.fine_grid.ingrid(X1, Y1)
print('fine = ', fine)

print("")
H = g.sample_depth(X, Y)
print('depth = ', H)
H1 = g.fine_grid.sample_depth(X1[fine], Y1[fine])
print('depth1 = ', H1)
H2 = g.coarse_grid.sample_depth(X2, Y2)
print('depth2 = ', H2)

print()
# All particles in fine
H = g.sample_depth(X[fine], Y[fine])
print("All in fine", H)
# All particles in coarse
H = g.sample_depth(X[~fine], Y[~fine])
print("All in coarse", H)

print('')
lon0, lat0 = g.lonlat(X, Y)
lon1, lat1 = g.fine_grid.lonlat(X1[fine], Y1[fine])
lon2, lat2 = g.coarse_grid.lonlat(X2, Y2)
print('lon0 = ', lon0)
print('lon1 = ', lon1)
print('lon2 = ', lon2)
print('lat0 = ', lat0)
print('lat1 = ', lat1)
print('lat2 = ', lat2)

print('')
onland = g.onland(X, Y)
print('on land = ', onland)
onland = g.fine_grid.onland(X1[fine], Y1[fine])
print('fine:  ', onland)
onland = g.coarse_grid.onland(X2, Y2)
print('coarse:  ', onland)
