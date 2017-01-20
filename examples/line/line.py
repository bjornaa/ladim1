# Make an particles.in file

import numpy as np

x0, x1 = 80, 125
y0, y1 = 100, 100

Npart = 10000
# Npart = 12

Z0 = 0.0

X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

f = open('../input/line.in', mode='w')

for i, (x, y) in enumerate(zip(X, Y)):
    f.write('1 1989-06-01T12 {:7.3f} {:7.3f} 0 {:d} 1\n'.format(x, y, i))

f.close()
