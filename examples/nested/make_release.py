# Make an particles.in file

import numpy as np

# End points of line in grid coordinates (orginal grid)
x0, x1 = 148, 148
y0, y1 = 51, 65

# Number of particles along the line
Npart = 1000

# Fixed particle depth
Z = 5

# Original grid

X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

with open('original.rls', mode='w') as f:
    for i, (x, y) in enumerate(zip(X, Y)):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

# Same section in coarse grid

Xcoarse = (X-1)/3.0
Ycoarse = (Y-1)/3
with open('coarse.rls', mode='w') as f:
    for i, (x, y) in enumerate(zip(Xcoarse, Ycoarse)):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

Xnest = X + 80 - 135
Ynest = Y + 30 - 42
with open('nested.rls', mode='w') as f:
    for i, (x, y) in enumerate(zip(Xnest, Ynest)):
        f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))
