# Make an particles.in file

import numpy as np
from nested_gridforce import Grid

# End points of line in grid coordinates (orginal grid)
x0, x1 = 148, 148
y0, y1 = 51, 65

# Number of particles along the line
Npart = 1000

# Fixed particle depth
Z = 5

# Define the grids
g = Grid(dict(grid_args=[]))

# Original grid
X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)
with open('original.rls', mode='w') as f:
    for x, y in zip(X, Y):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

# Virtual (nested) grid
X0 = X - g._i0
Y0 = Y - g._j0
with open('nested.rls', mode='w') as f:
    for x, y in zip(X0, Y0):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

# Same section in fine grid
X1, Y1 = g.xy2fine(X0, Y0)
with open('fine.rls', mode='w') as f:
    for x, y in zip(X1, Y1):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

# Same section in coarse grid
X2, Y2 = g.xy2coarse(X0, Y0)
with open('coarse.rls', mode='w') as f:
    for x, y in zip(X2, Y2):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))
