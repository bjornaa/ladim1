# Make a particle release file for ladim
# Two concentric circles for the Stommel example

import numpy as np
from gridforce_stommel import Grid

grd = Grid(None)

km = 1000
x0 = grd.lambda_ / 3.0
y0 = grd.b / 3.0
r1 = 800 * km  # Radius inner circle
r2 = 1600 * km  # Radius outer circle

N = 1000  # Number of particles per circle
T = np.linspace(0, 2 * np.pi, N)
X1 = x0 + r1 * np.cos(T)
Y1 = y0 + r1 * np.sin(T)
X2 = x0 + r2 * np.cos(T)
Y2 = y0 + r2 * np.sin(T)

X = np.concatenate((X1, X2))
Y = np.concatenate((Y1, Y2))

with open("stommel.rls", mode="w") as fid:
    for x, y in zip(X, Y):
        fid.write(f"2000-01-01 {x:11.2f} {y:11.2f}  5\n")
