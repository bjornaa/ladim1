# Make a particles.in file for a streak line
# Continuos release from single source

from numpy import arange, datetime64

start_time = datetime64('1989-05-24 12')
stop_time = datetime64('1989-06-15 13')   # Extra hour to get last time

# Release point in grid coordinates
x, y = 115, 100
z = 5

times = arange(start_time, stop_time, dtype='datetime64[h]')
with open('streak.rls', mode='w') as f:
    for t in times:
        f.write('1 {:s} {:7.3f} {:7.3f} {:6.1f}\n'.format(t, x, y, z))
