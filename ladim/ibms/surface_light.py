# Surface ligth module
# After Skartveit & Olseth 1988
import datetime
import numpy as np

pi = np.pi
sin = np.sin
cos = np.cos
rad = np.pi / 180.0
deg = 180/pi


def sind(x):
    return np.sin(x*rad)


def cosd(x):
    return np.cos(x*rad)


def asind(v):
    return deg*np.arcsin(v)


def surface_light(dtime, lat):

    # def surface_light(timevector, B):
    # B = latitude (north)
    # B:Degrees north
    #  DELTA: sun declination
    #  D: day of the year
    #  H: hour of day
    #  HEIGHT: sin(sunheight)
    #  IRR. irradiance above sea surface uEm-2s-1
    #  P: Pi
    #  R: factor for distance variations between sun-earth
    #  SLIG:surface light
    #  V: sunheight in degrees
    #  TWLIGHT: light at 0-degree sun
    # MAXLIG: level of irradiance at midday

    maxlight = 1500  # value between 200 and 2000

    time_tuple = dtime.timetuple()
    # day of year, original does not consider leap years
    yday = time_tuple.tm_yday
    # hours in local time ot UTC???
    hours = time_tuple.tm_hour

    twilight = 5.76
    delta = .3979 * sind(.9856*(yday-80) + 1.9171*(sind(.9856*yday)-.98112))
    h12 = delta*sind(lat) - np.sqrt(1.-delta**2)*cosd(lat)*cosd(15.*12)
    height = delta*sind(lat) - np.sqrt(1.-delta**2)*cosd(lat)*cosd(15.*hours)

    # print(delta, h12)
    v = asind(height)  # sun height [deg]
    # print(height, v)

    if (v >= 0.):
        slig = maxlight*(height/h12) + twilight
    elif (v >= -6.):
        slig = ((twilight - .048)/6.)*(6.+v)+.048
    elif (v >= -12.):
        slig = ((.048 - 1.15e-4)/6.)*(12.+v)+1.15e-4
    elif (v >= -18):
        slig = (((1.15e-4)-1.15e-5)/6.)*(18.+v)+1.15e-5
    else:
        slig = 1.15e-5

    return slig

if __name__ == '__main__':

    dtime = datetime.datetime(2014, 6, 23, 12, 0, 0)
    lat = 60.0
    print(surface_light(dtime, lat))

    dtime = datetime.datetime(2014, 6, 23, 18, 0, 0)
    lat = 60.0
    print(surface_light(dtime, lat))
