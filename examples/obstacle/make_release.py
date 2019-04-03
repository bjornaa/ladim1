# Make an particles.in file

import numpy as np

# N = 10000
N = 1000

X = 3 + np.zeros(N)
Y = 0.45 + 0.045 * np.arange(1, N + 1)
Z = 5

f = open("obstacle.rls", mode="w")

for (x, y) in zip(X, Y):
    f.write("2000-01-01 {:7.3f} {:7.3f} {:6.1f}\n".format(x, y, Z))

f.close()
