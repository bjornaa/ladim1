import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt

with Dataset("../data/ocean_avg_0014.nc") as f:
    M0 = f.variables["mask_rho"][:, :]
M0 = np.ma.masked_where(M0 > 0, M0)

jmax, imax = M0.shape
Xb = np.arange(-0.5, imax)
Yb = np.arange(-0.5, jmax)


# Original grid
plt.pcolormesh(Xb, Yb, M0, alpha=0.3, cmap="Greens_r")

# Virtual grid
i0, i1 = 80, 175
j0, j1 = 30, 110
Xb0 = np.arange(i0 - 0.5, i1)
Yb0 = np.arange(j0 - 0.5, j1)
plt.plot(Xb0[[0, -1, -1, 0, 0]], Yb0[[0, 0, -1, -1, 0]], color="red", lw=2)

# Fine grid
i0, i1 = 135, 172
j0, j1 = 42, 81
Xb1 = np.arange(i0 - 0.5, i1)
Yb1 = np.arange(j0 - 0.5, j1)

plt.plot(Xb1[[0, -1, -1, 0, 0]], Yb1[[0, 0, -1, -1, 0]], color="red", lw=2)

# Coarse grid
Xb2 = np.arange(-0.5, imax - 1, 3)
Yb2 = np.arange(-0.5, jmax - 1, 3)
with Dataset("forcing_northsea.nc") as f:
    M2 = f.variables["mask_rho"][:, :]
M2 = np.ma.masked_where(M2 > 0, M2)

plt.plot(Xb2[[0, -1, -1, 0, 0]], Yb2[[0, 0, -1, -1, 0]], color="red", lw=2)
plt.pcolormesh(Xb2, Yb2, M2, alpha=0.3, cmap="Reds_r")

# Test positions used in testnest.py
# add offset (80, 30) to transform from virtual to original
X = np.array([60, 80, 50, 30]) + 80
Y = np.array([40, 30, 50, 20]) + 30

plt.scatter(X, Y, marker="o", edgecolor="black", color="yellow")


plt.axis("image")
plt.show()
