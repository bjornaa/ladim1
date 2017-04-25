import numpy as np
import matplotlib.pyplot as plt
from postladim import ParticleFile, cellcount

pf = ParticleFile('line.nc')
X, Y = pf.position(80)

C = cellcount(X, Y)

i0 = int(round(X.min()))
j0 = int(round(Y.min()))

jmax, imax = C.shape
x_edges = np.arange(i0-0.5, i0+imax)
y_edges = np.arange(j0-0.5, j0+jmax)


plt.set_cmap('magma_r')
plt.pcolormesh(x_edges, y_edges, C)
plt.colorbar()
plt.plot(X, Y, '.k')
plt.show()
