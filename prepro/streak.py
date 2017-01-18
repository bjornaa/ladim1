# Make a particles.in file for a streak line
# Continuos release from single source

from numpy import arange, datetime64, timedelta64

start_time = datetime64('1989-06-01 12')
stop_time = datetime64('1989-06-15 13')   # Extra hour to get last time

x, y = 115, 100

times = arange(start_time, stop_time, dtype='datetime64[h]')

# print(times)

with open('../input/streak.in', mode='w') as f:
    for t in times:
        f.write('1 {:s} {:7.3f} {:7.3f} 0 0 1\n'.format(t, x, y))
