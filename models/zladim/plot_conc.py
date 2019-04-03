import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

grid_file = "/data/model_data006/anneds/Lusedata/Gridfiler/norkyst_800m_grid_full.nc"
conc_file = "c2.nc"

with Dataset(grid_file) as f:
    M = f.variables["mask_rho"][:, :]

with Dataset(conc_file) as f:
    C = f.variables["conc"][:, :]

C /= 800 ** 2

C = C.clip(0, 1)

# C = np.ma.masked_where(M == 0, C)
C = np.ma.masked_where(C == 0, C)

jmax, imax = C.shape

Xb = np.arange(-0.5, imax)
Yb = np.arange(-0.5, jmax)

plt.pcolormesh(Xb, Yb, C, cmap=plt.get_cmap("plasma_r"))

plt.colorbar()

# Land mask
constmap = plt.matplotlib.colors.ListedColormap([0.2, 0.6, 0.4])
M = np.ma.masked_where(M > 0, M)
plt.pcolormesh(Xb, Yb, M, cmap=constmap)

plt.axis("image")

plt.show()
