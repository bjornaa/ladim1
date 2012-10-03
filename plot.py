import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date

f = Dataset('a.nc')

t = 6


p0 = f.variables['pStart'][t]
Npart = f.variables['pCount'][t]
tid = f.variables['time'][t]
tunit = f.variables['time'].units
print p0, Npart

timestr = num2date(tid, tunit)

X = f.variables['X'][p0:p0+Npart]
Y = f.variables['Y'][p0:p0+Npart]

plt.plot(X, Y)
plt.title(timestr)

plt.show()

