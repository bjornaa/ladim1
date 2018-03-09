# Make an particles.in file

import numpy as np

# End points of line in grid coordinates
x0, x1 = 68, 145
y0, y1 = 188, 188
Npart = 1000

# Fixed particle depth
Z = 5

X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

f = open('outline.rls', mode='w')

for i, (x, y) in enumerate(zip(X, Y)):
    f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

f.close()
