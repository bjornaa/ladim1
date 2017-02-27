import numpy as np

km = 1000    # abbrev
L = 100*km   # Length of channel [m]
W = 50*km    # Width of channel [m]
U0 = 1       # Undisturbed along-channel velocity [m/s]
dx = 1*km    # Grid spacing along channel [m]
dy = 1*km    # Grid spacing cross channel [m]

# imax = 100
# jmax = 50

X0 = 0.5*L     # Center location of peninsula
R = 0.32*W     # Radius of peninsula

H = 100           # Depth of channel [m]

# Convert to grid coordinates
X0 = X0 / dx
R = R / dy

class Grid:

    def __init__(self):
        pass

    def sample_metric(self, X, Y):
        return dx + np.zeros_like(X), dy + np.zeros_like(Y)

    def sample_depth(self, X, Y):
        return H + np.zeros_like(X)

    def atsea(self, X, Y):
        # return (X-X0)**2 + Y**2 > R**2
        return np.ones_like(X, dtype='bool')


class Forcing:

    def __init__(self):
        pass

    def velocity(self, X, Y, Z, tstep=0):
        U = U0 - U0*R**2*((X-X0)**2 - Y**2) / ((X-X0)**2 + Y**2)**2
        V = - 2*U0*R**2*(X-X0)*Y / ((X-X0)**2 + Y**2)**2
        return U, V

    def update(self, step):
        pass

    def close(self):
        pass
