# import datetime
from dateutil import parser

fid = open('lice.in')

line = next(fid)
release_variables = line.split()
Nvar = len(release_variables)
var_type = {}
for i, var in enumerate(release_variables[1:]):
    n = var.find(':')
    if n < 0:  # Default type = float
        var_type[var] = float
    else:
        var0 = var[:n]
        var_type[var0] = int
        release_variables[i+1] = var0

for line in fid:
    release = dict()
    w = line.split()
    release['time'] = parser.parse('T'.join(w[:2]))
    for i, var in enumerate(release_variables[1:]):
        release[var] = var_type[var](w[i+2])
    print(release)
