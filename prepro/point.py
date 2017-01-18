# Make a particles.in file
# Single position, varying depth

import numpy as np

x, y = 115, 100

zmax = 100

Npart = 1000


Z = np.linspace(0, zmax+1, Npart)

with open('../input/point.in', mode='w') as f:
    for i, z in enumerate(Z):
        f.write('1 1989-06-01T12 {:7.3f} {:7.3f} {:5.2f} {:d} 1\n'.format(
                x, y, z, i))

