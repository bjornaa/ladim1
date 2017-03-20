import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

grid_file = '/data/model_data006/anneds/Lusedata/Gridfiler/norkyst_800m_grid_full.nc'
conc_file = 'c2.nc'

with Dataset(grid_file) as f:
    M = f.variables['mask_rho'][:, :]

with Dataset(conc_file) as f:
    C = f.variables['conc'][1:-1, 1:-1]

C = C / 800**2

C = C.clip(0, 0.5)

#C = np.ma.masked_where(M == 0, C)
C = np.ma.masked_where(C == 0, C)

jmax, imax = C.shape

plt.pcolormesh(C)

plt.colorbar()

plt.axis('image')

plt.show()
