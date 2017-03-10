# Continuos release,
# 1 particle per hour from 2 locations
# Fixed depth at 5 m

f0 = open('multifarm_Lus_29jan.dat')
f1 = open('lice_2917-01.29.rls', mode='w')

mult = 5

next(f0)  # Skip initial line
for line in f0:
    w = line.split(',')
    if len(w) == 1:
        continue
    farmid = int(w[0])
    print(farmid)
    x = float(w[1])
    y = float(w[2])
    z = 5
    super = float(w[4])
    timestamp = w[5].strip()
    f1.write("{:d} {:s} {:f} {:f} {:f} {:d} {:f}\n".format(
             mult, timestamp, x, y, z, farmid, super))

f1.close()
