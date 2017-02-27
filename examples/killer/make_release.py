# Make a particles.in file for a streak line
# Continuos release from single source

from numpy import datetime64

start_time = datetime64('1989-05-24 12')
# stop_time = datetime64('1989-06-15 13')   # Extra hour to get last time

# Release point in grid coordinates
x, y = 115, 100
z = 5

with open('killer.rls', mode='w') as f:
    f.write('{:s} {:7.3f} {:7.3f} {:6.1f}\n'.format(start_time, x, y, z))
