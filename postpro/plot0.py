import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date

t = 20

f0 = Dataset('../input/ocean_avg_0014.nc')  # For bathymetry and land contour
# f = Dataset('../output/pyladim_out.nc')     # Particle output file
f = Dataset('../output/streak.nc')     # Particle output file

timevar = f.variables['time']

timestr = str(num2date(timevar[t], timevar.units))

# Indirect addressing
acount = f.variables['particle_count'][:t+1]
start = acount[:-1].sum()
count = acount[-1]

# Particle positions
X = f.variables['X'][start:start+count]
Y = f.variables['Y'][start:start+count]

H = f0.variables['h'][:, :]

plt.plot(X, Y, '.', color='blue')
plt.title(timestr)

plt.contour(H, levels=[10.0], colors='black', linewidths=2.5)

plt.axis('image')

plt.show()
