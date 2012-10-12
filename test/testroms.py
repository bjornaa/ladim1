# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset
from romsutil import *


f = Dataset('data/ocean_avg_0014.nc')

H = f.variables['h'][:,:]
Hc = f.variables['hc'][:]
C = f.variables['sc_r'][:]

z_rho = sdepth(H, Hc, C)

print "z_rho.shape = ", z_rho.shape

X = np.array([90.2, 90.2, 90.2, 90.2,  90.2,  90.8,  93.8])
Y = np.array([99.9, 99.9, 99.9, 99.9,  99.9, 100.2, 106.3])
Z = np.array([29.0, 30.0, 31.0,  1.0, 200.0,  30.0,  30.0])

print "X = ", X
print "Y = ", Y
print "Z = ", Z

K, A = Z2S(z_rho, X, Y, Z)

print sample3D_(z_rho, X, Y, K, A)

