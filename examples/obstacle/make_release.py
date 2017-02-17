# Make an particles.in file

import numpy as np

N = 10000

X = 3 + np.zeros(N)
Y = 0.45 + 0.0045*np.arange(1, N+1)
Z = 5

f = open('obstacle.rls', mode='w')

for (x, y) in zip(X, Y):
    f.write('1 1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

f.close()
