# Surface ligth module
# After Skartveit & Olseth 1988
# import datetime
import numpy as np

pi = np.pi
sin = np.sin
cos = np.cos
rad = np.pi / 180.0
deg = 180/pi


def surface_light(dtime, lat):

    maxlight = 1500  # value between 200 and 2000

    # Convert from datetime64 to datetime
    dtime = dtime.astype(object)

    time_tuple = dtime.timetuple()
    # day of year, original does not consider leap years
    yday = time_tuple.tm_yday
    # hours in local time ot UTC???
    hours = time_tuple.tm_hour

    twilight = 5.76

    phi = lat*rad

    a0 = 0.3979
    a1 = 0.9856 * rad   # day-1
    a2 = 1.9171 * rad
    a3 = 0.98112
    delta = a0*sin(a1*(yday-80) + a2*(sin(a1*yday)-a3))
    h12 = delta*sin(phi) + np.sqrt(1.-delta**2)*cos(phi)
    height = delta*sin(phi) - np.sqrt(1.-delta**2)*cos(phi)*cos(15*hours*rad)

    v = np.arcsin(height) * deg  # sun height [deg]

    slig = np.zeros_like(lat, dtype=float)
    I0 = (v >= 0)
    I1 = (v >= -6) & (v < 0)
    I2 = (v >= -12) & (v < -6)
    I3 = (v >= -18) & (v < -12)
    I4 = (v < -18)

    slig[I0] = maxlight*(height[I0]/h12[I0]) + twilight
    slig[I1] = ((twilight - 0.048)/6)*(6+v[I1])+0.048
    slig[I2] = ((0.048 - 1.15e-4)/6)*(12+v[I2])+1.15e-4
    slig[I3] = ((1.15e-4 - 1.15e-5)/6)*(18+v[I3])+1.15e-5
    slig[I4] = 1.15e-5

    return slig

if __name__ == '__main__':

    dtime = np.datetime64('2014-06-23 12')
    lat = 60
    print(surface_light(dtime, lat))

    dtime = np.datetime64('2014-06-23 18')
    lat = 60
    print(surface_light(dtime, lat))
