# Surface ligth module
# After A. Skartveit & J.A. Olseth,1988
# Varighetstabeller for timevis belysning mot 5 flater
# på 16 norske stasjoner
# Meteorological report series, 1988-7
# University of Bergen

import numpy as np

pi = np.pi
rad = pi / 180.0
deg = 180 / pi
sin = np.sin
cos = np.cos


def surface_light(dtime, lon, lat):
    """Surface light in absence of clouds"""

    maxlight = 1500  # value between 200 and 2000
    twilight = 5.76

    # --- Time handling ----
    # Convert from datetime64 to datetime
    dtime = dtime.astype(object)
    time_tuple = dtime.timetuple()
    # day of year, original does not consider leap years
    yday = time_tuple.tm_yday
    # hours in UTC (as output from oceanographic model)
    hours = time_tuple.tm_hour

    phi = lat*rad

    # Compute declineation = delta
    a0 = 0.3979
    a1 = 0.9856 * rad   # day-1
    a2 = 1.9171 * rad
    a3 = 0.98112
    sindelta = a0*sin(a1*(yday-80) + a2*(sin(a1*yday)-a3))
    cosdelta = (1-sindelta**2)**0.5

    # True Sun Time [degrees](=0 with sun in North, 15 deg/hour
    # b0 = 0.4083
    # b1 = 1.7958
    # b2 = 2.4875
    # b3 = 1.0712 * rad   # day-1
    # TST = (hours*15 + lon - b0*np.cos(a1*(yday-80)) -
    #        b1*np.cos(a1*(yday-80)) + b2*np.sin(b3*(yday-80)))

    # TST = 15 * hours  # Recover values from the fortran code

    # Simplified formula
    # correct at spring equinox (yday=80) neglecting +/- 3 deg = 12 min
    TST = hours*15 + lon

    # Sun height  [degrees]
    # sinheight = sindelta*sin(phi) - cosdelta*cos(phi)*cos(15*hours*rad)
    sinheight = sindelta*sin(phi) - cosdelta*cos(phi)*cos(TST*rad)
    height = np.arcsin(sinheight) * deg

    # sine of sun height at noon, h12
    sinh12 = sindelta*sin(phi) + cosdelta*cos(phi)

    # Do we need the surface light?
    # a treshold on sun heigth might be enough

    # Surface light
    slight = np.zeros_like(lat, dtype=float)
    I0 = (height >= 0)
    I1 = (height >= -6) & (height < 0)
    I2 = (height >= -12) & (height < -6)
    I3 = (height >= -18) & (height < -12)
    I4 = (height < -18)

    # Is this from Skagseth & Olset ?  Where?
    slight[I0] = maxlight*(sinheight[I0]/sinh12[I0]) + twilight
    slight[I1] = ((twilight - 0.048)/6)*(6+height[I1])+0.048
    slight[I2] = ((0.048 - 1.15e-4)/6)*(12+height[I2])+1.15e-4
    slight[I3] = ((1.15e-4 - 1.15e-5)/6)*(18+height[I3])+1.15e-5
    slight[I4] = 1.15e-5

    return slight


if __name__ == '__main__':

    dtime = np.datetime64('2014-06-23 12')
    lon, lat = 0, 60
    print(surface_light(dtime, lon, lat))

    dtime = np.datetime64('2014-06-23 18')
    lon, lat = 0, 60
    print(surface_light(dtime, lon, lat))
