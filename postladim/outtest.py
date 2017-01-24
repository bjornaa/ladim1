from netCDF4 import Dataset, num2date

f = Dataset('../output/pyladim_out.nc')     # Particle output file

t = 2

timevar = f.variables['time']
ntimes = len(timevar)
if t >= ntimes:
    print("ERROR: t = {:d} må være <= {:d}".format(t, ntimes))
    import sys
    sys.exit(1)

print("time =", num2date(timevar[t], timevar.units))

# Indirect addressing
acount = f.variables['particle_count'][:t+1]
start = acount[:-1].sum()
count = acount[-1]

print("start, count =", start, count)

pid = f.variables['pid'][start:start+count]
print("pids =", pid)
