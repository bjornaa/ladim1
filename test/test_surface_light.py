# Testing Skartveit & Olseth 1988 light radiation model
# against values from the old fortran code.

import datetime
from ladim.ibms import surface_light

test_values = [(2014, 6, 23, 12, 0, 0, 23.0,  1505.76001),    
               (2014, 6, 23, 12, 0, 0, 60.0,  1505.76001),   
               (2014, 6, 23, 18, 0, 0, 60.0,  649.136475),  
               (2014, 6, 23, 18, 0, 0, 80.0,  1072.13538),  
               (2014, 6, 23, 0, 0, 0, 60.0,  4.35530655E-02),
               (2014, 6, 23, 0, 0, 0, 80.0,  638.511169),
               (2014, 12, 24, 12, 0, 0, 80.0,  9.02698666E-05),
               (2014, 12, 24, 12, 0, 0, 60.0,  1505.76001)]

for y, d, m, h, _, _, lat, value in test_values:
    dtime = datetime.datetime(y, d, m, h)
    result = surface_light.surface_light(dtime, lat)
    print(result)
    assert(abs(result - value) < 1.0e-3)

