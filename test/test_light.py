# Testing Skartveit & Olseth 1988 light radiation model
# against values from the old fortran code.

from numpy import array, datetime64
from ladim.ibms import light

# Time. longitude, latitude, fortran value
test_values = [(datetime64('2014-06-23 12'), 0.0, 23.0, 1505.76001),
               (datetime64('2014-06-23 12'), 0.0, 60.0, 1505.76001),
               (datetime64('2014-06-23 18'), 0.0, 60.0, 649.136475),
               (datetime64('2014-06-23 18'), 0.0, 80.0, 1072.13538),
               (datetime64('2014-06-23 00'), 0.0, 60.0, 4.35530655E-02),
               (datetime64('2014-06-23 00'), 0.0, 80.0, 638.511169),
               (datetime64('2014-12-24 12'), 0.0, 80.0, 9.02698666E-05),
               (datetime64('2014-12-24 12'), 0.0, 60.0, 1505.76001)]

for dtime, lon, lat, value in test_values:
    result = light.surface_light(dtime, lon, lat)
    # result = light.surface_light(dtime, lat)
    print(result, value)
    # assert(abs(result - value) < 1.0e-3)

lat = array([10, 20, 30, 40, 50, 60, 70, 80, 90])
dtime = datetime64('2014-04-01 20')
print(light.surface_light(dtime, 0, lat))

lat = array([10, 20, 30, 40, 50, 60, 70, 80, 90])
dtime = datetime64('2014-01-28 15')
print(light.surface_light(dtime, 0, lat))
