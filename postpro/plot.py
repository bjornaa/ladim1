import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date

f0 = Dataset('../input/ocean_avg_0014.nc')
f  = Dataset('../output/pyladim_out.nc')

t = 6

p0 = f.variables['pstart'][t]
Npart = f.variables['pcount'][t]
tid = f.variables['time'][t]
tunit = f.variables['time'].units
print p0, Npart

timestr = num2date(tid, tunit)

X = f.variables['X'][p0:p0+Npart]
Y = f.variables['Y'][p0:p0+Npart]

H = f0.variables['h'][:,:]

plt.plot(X, Y, 'o', color='blue')
plt.title(timestr)


plt.contour(H, levels = [50.0, 100.0, 200.0, 500.0], colors='black')
plt.contour(H, levels = [10.0], colors='black', linewidths=2.5)

plt.axis('image')

plt.show()

