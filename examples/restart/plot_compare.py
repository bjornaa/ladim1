import matplotlib.pyplot as plt
import roppy.mpl_util
from netCDF4 import Dataset

from postladim import ParticleFile

# ---------------
# User settings
# ---------------

# Files
unsplit_file = 'unsplit.nc'
split_file = 'split_0002.nc'
restarted_file = 'restart_0000.nc'
grid_file = '../data/ocean_avg_0014.nc'

# Subgrid definition
i0, i1 = 113, 119
j0, j1 = 97, 102

# Comparable records,split by 4
t0 = 9  # tenth record in unsplit file
t1 = 1  # second record in third split file
t2 = 1  # second record in first restarted file

# ----------------

# particle_file
pf0 = ParticleFile(unsplit_file)
pf1 = ParticleFile(split_file)
pf2 = ParticleFile(restarted_file)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1)

# Make bathymetry background
with Dataset(grid_file) as f0:
    H = f0.variables['h'][j0:j1, i0:i1]
cmap = plt.get_cmap('Blues')
ax.contourf(range(i0, i1), range(j0, j1), H, cmap=cmap, alpha=0.3)

# Plot initial particle distribution
X0, Y0 = pf0.position(t0)
X1, Y1 = pf1.position(t1)
X2, Y2 = pf2.position(t2)

ax.plot(X0, Y0, 'o', color='green', label='unsplit')
ax.plot(X1, Y1, 'o', color='red', label='split')
ax.plot(X2, Y2, 'o', color='blue', label='restart')

# Show the results
plt.legend()
plt.axis('image')
plt.axis((i0+1, i1-1, j0+1, j1-1))
plt.show()
