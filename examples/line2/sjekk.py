import numpy as np
from netCDF4 import Dataset

f = Dataset('../data/ocean_avg_0014.nc')

i, j = 66, 92
k = 28    # near surface
n = 3   # time step


print("i,j,k,n = ", i, j, k, n)

H = f.variables['h']
M = f.variables['mask_rho']
print('H = ', H[j, i])
print('M = ', M[j, i])

U = f.variables['u']
V = f.variables['v']
print("U = ", U[n, k, j, i-1], U[n, k, j, i])
print("V = ", V[n, k, j-1, i], V[n, k, j, i])
