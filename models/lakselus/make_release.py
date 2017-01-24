import datetime

# Continuos release,
# 1 particle per hour from 2 locations
# Fixed depth at 5 m

f1 = open('release.in', mode='w')

mult = 1

time0 = datetime.datetime(2015, 3, 31, 13)
hour = datetime.timedelta(seconds=3600)

times = [time0 + n*hour for n in range(24)]

format1 = "5 {:s} 379 539 5\n"  
format2 = "5 {:s} 381 523 5\n"  

for t in times:
    print(t)
    tt = 'T'.join(str(t).split())
    f1.write(format1.format(tt))
    f1.write(format2.format(tt))
