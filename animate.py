import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date
import roppy
from roppy.mpl_util import landmask

i0, j0 = 70,   80
i1, j1 = 140, 130


f0 = Dataset('data/ocean_avg_0014.nc')
g = roppy.SGrid(f0, subgrid=(i0,i1,j0,j1))

#f  = Dataset('/tmp/pyladim_out.nc')
f  = Dataset('pyladim_out.nc')

Ntimes = len(f.dimensions['Time'])

#Xc, Yc = np.loadtxt("./data/ns8_coast.dat", unpack=True)
#Xc = Xc - i0
#Yc = Yc - j0

#H = f0.variables['h'][:,:]

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
#ax.set_xlim(70,140)
#ax.set_ylim(80,130)
#ax.axis('image')

def read(t):
    p0 = f.variables['pStart'][t]
    Npart = f.variables['pCount'][t]
    tid = f.variables['time'][t]
    tunit = f.variables['time'].units
    #print p0, Npart
    timestr = num2date(tid, tunit)
    X = f.variables['X'][p0:p0+Npart]
    Y = f.variables['Y'][p0:p0+Npart]
    # Not handling subgrids properly??
    X = X - i0
    Y = Y - j0
    return X, Y, timestr


def animate():
    for t in range(1, Ntimes):
        X, Y, tstring = read(t)
        h[0].set_xdata(X)
        h[0].set_ydata(Y)
        ax.set_title(tstring)
        fig.canvas.draw()

X, Y, tstring = read(0)

cmap = plt.get_cmap('Blues')

ax.contourf(g.h, cmap=cmap)
#ax.contour(g.h, levels = [10.0], colors='black', linewidths=2.5)
roppy.mpl_util.landmask(g.mask_rho, (0.6, 0.8, 0.0))

#plt.fill(Xc, Yc, edgecolor=(0.6, 0.8, 0.0))


h = ax.plot(X, Y, '.', color='red', markeredgewidth=0, lw=0.5)
ax.set_title(tstring)


fig.canvas.manager.window.after(100, animate)
plt.show()

