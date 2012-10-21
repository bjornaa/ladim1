# -*- coding: utf-8 -*-

from netCDF4 import Dataset

# For each possible variable, provide a
# netcdf type and a dictionary of netcdf attributes 
# Example:
#  ('f4', dict(standard_name='longitude', units='degrees_east'))

variables_ncdef = dict(
    pid = ('i', dict(longname='particle identifier')),
    X = ('f4', dict(longname='grid X-coordinate of particles')),
    Y = ('f4', dict(longname='grid Y-coordinate of particles')),
    )
    





class OutPut(object):

    def __init__(self, setup):

        nc = Dataset(setup['output_filename'], mode='w', 
                     format="NETCDF3_CLASSIC")
    
        nc.createDimension('Particle_Index', None)
        nc.createDimension('Time', setup['Nout'])

        v = nc.createVariable('time', 'f8', ('Time',))
        v.units = 'seconds since %s' % setup['start_time']
        v = nc.createVariable('pStart', 'i', ('Time',))
        v = nc.createVariable('pCount', 'i', ('Time',))

        for var in setup['output_variables']:
            nctype = variables_ncdef[var][0]
            atts = variables_ncdef[var][1]
            v = nc.createVariable(var, nctype, ('Particle_Index',))
            for att in atts:
                setattr(v, att, atts[att])

        self.nc = nc
        #self.Nout = Nout
        self.outcount = 0
        self.pStart   = 0
        self.outstep  =  setup['output_period']*setup['dt']      
        self.output_variables = setup['output_variables'] 
        self.pvars = setup['output_variables']
        
    # --------------
 
    def write(self, state):
        """
        Write a particle distribution
        """

        Npar = len(state['X']) 
        t = self.outcount
        nc = self.nc

        # Write to time variables
        nc.variables['pStart'][t] = self.pStart
        nc.variables['pCount'][t] = Npar     
        nc.variables['time'][t] = t * self.outstep

        # Write to particle properties
        T = slice(self.pStart, self.pStart + Npar)
        for var in self.output_variables:
            nc.variables[var][T] = state[var]

        # Write 
        self.pStart += Npar
        self.outcount += 1

    # --------------

    def close(self):

        self.nc.close()




    
