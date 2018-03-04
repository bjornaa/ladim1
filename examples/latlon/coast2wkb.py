# Make a wkb file from a npy coast file

import numpy as np
from shapely.geometry import MultiPolygon, asPolygon
from shapely.wkb import dumps

infile = 'coast.npy'
outfile = 'coast.wkb'

# Make a list of the polygons as shapely geometries
V = []
polys = np.load(infile)
for p in polys:
    V.append(asPolygon(np.vstack(p).T))

with open(outfile, 'bw') as f:
    f.write(dumps(MultiPolygon(V)))
