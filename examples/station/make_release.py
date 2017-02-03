# Make a particles.in file for a streak line
# Continuos release from single source

from numpy import linspace

start_time = '1989-05-24T12'

num_particles = 20001
# Release point in grid coordinates
x, y = 115, 100
zmax = 200

mult = 1

Z = linspace(0, zmax, num_particles)

with open('station.rls', mode='w') as f:
    for z in Z:
        f.write('{:d} {:s} {:7.3f} {:7.3f} {:6.2f}\n'.
                format(mult, start_time, x, y, z))
