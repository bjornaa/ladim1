import numpy as np

km = 1000
L = 100*km
W = 50*km
U0 = 1
dx = 1*km
dy = 1*km

imax = 100
jmax = 50

X0 = 0.5*imax
R = 0.32*jmax

H = 100


class Grid():

    def __init__(self):
        pass

    def sample_metric(self, X, Y):
        return dx + np.zeros_like(X), dy + np.zeros_like(Y)

    def sample_depth(self, X, Y):
        return H + np.zeros_like(X)

    def atsea(self, X, Y):
        # return (X-X0)**2 + Y**2 > R**2
        return np.ones_like(X, dtype='bool')


class Forcing():

    def __init__(self):
        pass

    def sample_velocity(self, X, Y, Z, tstep=0):
        U = U0 - U0*R**2*((X-X0)**2 - Y**2) / ((X-X0)**2 + Y**2)**2
        V = - 2*U0*R**2*(X-X0)*Y / ((X-X0)**2 + Y**2)**2
        return U, V

    def update(self, step):
        pass

    def close(self):
        pass
