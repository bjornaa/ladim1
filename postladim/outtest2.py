# from netCDF4 import Dataset, num2date
from postladim import ParticleFile

# pf = ParticleFile('../output/pyladim_out.nc')     # Particle output file
pf = ParticleFile('../examples/streak/streak.nc')     # Particle output file


t = 112
pid1 = pf.variables['pid'][t]
print("t, len(pid1) = ", t, len(pid1))

t = 113
pid2 = pf.variables['pid'][t]
print("t, len(pid2) = ", t, len(pid2))

t = slice(112, 114)
pid12 = pf.variables['pid'][t]
print("t, len(pid12) = ", t, len(pid12))
# print("pid12 = ", pid12)


# print("pids =", pid)
