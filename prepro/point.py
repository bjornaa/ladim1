# Make a particles.in file
# Single position, varying depth

import numpy as np

x, y = 115, 100


zmax = 100

Z = np.linspace(0, zmax, Npart)

with open('../input/point.in', mode='w') as f:
    f.write('TR 0 hours\n')
    for z in Z:
        f.write('G %8.3f %8.3f % 8.3f\n' % (x, y, z))
