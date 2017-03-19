# from netCDF4 import Dataset, num2date
from particlefile import ParticleFile

# pf = ParticleFile('../output/pyladim_out.nc')     # Particle output file
pf = ParticleFile('../output/streak.nc')     # Particle output file

t = 112

# pid = f.variables['pid'][start:start+count]
pid = pf.get_variable(t, 'pid')
print("t, len(pid) = ", t, len(pid))

print("pids =", pid)
