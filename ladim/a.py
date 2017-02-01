import csv
import numpy as np

file = '../models/lakselus/release.in'

#with open(file) as csvfile:
#    reader = csv.DictReader(csvfile, delimiter=' ')
#    for row in reader:
#        print(row)

format = ['mult', 'time', 'X', 'Y', 'Z', 'farmid', 'super']
dtype = dict(mult=int, time=np.datetime64, X=float, Y=float, Z=float,
             farmid=int, super=float)
# Can use ordereddict

with open(file) as f:
    for line in f:
        w = line.split()
        row = dict()
        for i, var in enumerate(format):
            row[var] = dtype[var](w[i])
    print(row)
