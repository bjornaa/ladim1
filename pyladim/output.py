# -*- coding: utf-8 -*-

"""Output module for the (py)ladim particle tracking model"""

# ------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2013-01-04
# ------------------------------------

import datetime
from netCDF4 import Dataset

# For each possible variable, provide a
# netcdf type and a dictionary of netcdf attributes
# Example:
#  ('f4', dict(standard_name='longitude', units='degrees_east'))

# NetCDF data types for the variables
variables_nctype = dict(
    # pid = 'i4',
    X='f4', Y='f4', Z='f4',
    lon='f4', lat='f4')


# NetCDF attributes
variables_ncatt = dict(
    # pid = dict(long_name     = 'particle identifier',
    #           cf_role       = 'trajectory_id'),
    X=dict(long_name='particle X-coordinate'),
    Y=dict(long_name='particle Y-coordinate'),
    Z=dict(long_name='particle depth',
           standard_name='depth',
           units='m',
           positive='down'),
    lon=dict(long_name='particle longitude',
             standard_name='longitude',
             units='degrees_east'),
    lat=dict(long_name='particle latitude',
             standard_name='latitude',
             units='degrees_north'),
    )


class OutPut(object):

    def __init__(self, setup):

        nc = Dataset(setup.output_filename, mode='w',
                     format="NETCDF3_CLASSIC")

        # --- Dimensions
        nc.createDimension('particle_instance', None)  # unlimited
        nc.createDimension('particle', setup.particle_count_max)
        nc.createDimension('time', setup.Nout)

        # ---- Coordinate variable for time
        v = nc.createVariable('time', 'f8', ('time',))
        v.long_name = 'time'
        v.standard_name = 'time'
        v.units = 'seconds since {:s}'.format(setup.reference_time)

        v = nc.createVariable('pid', 'i4', ('particle_instance',))
        v.long_name = 'particle identifier'
        v.cf_role = 'trajectory_id'

        v = nc.createVarable('particle_count', 'i4', ('time',))
        v.long_name = "number of particles at a given time step"
        v.ragged_row_count = "particle count at nth timestep"

        # v = nc.createVariable('pstart', 'i4', ('time',))
        # v.long_name = 'start index for particle distribution'

        # --- Particle variables

        v = nc.createVariable('farmid', 'i4', ('particle',))
        v.long_name = "Fish farm location id"

        v = nc.createVariable('release_time', 'f8', ('particle',))
        v.long_name = 'Time of release'
        v.units = 'seconds since {:s}'.format(setup.reference_time)

        # --- Particle instance variables
        for var in setup.output_variables:
            print(var)
            v = nc.createVariable(var, 'f4', ('particle_instance',))
            atts = variables_ncatt[var]
            for att in atts:
                setattr(v, att, atts[att])

        # --- Global attributes
        nc.Conventions = "CF-1.5"
        nc.institution = "Institute of Marine Research"
        nc.source = "Lagrangian Advection and DIffusion Model, python version"
        nc.history = "%s created by pyladim" % datetime.date.today()

        # --- Initialize
        self.nc = nc
        self.outcount = 0
        self.pstart = 0
        self.outstep = setup.output_period * setup.dt
        self.output_variables = setup.output_variables
        self.pvars = setup.output_variables

    # --------------

    def _write_particle_vars(self):
        """
        Write time independent particle variables
        """




    def write(self, state):
        """
        Write a particle distribution
        """

        Npar = len(state)
        t = self.outcount
        nc = self.nc

        # Write to time variables
        # nc.variables['pstart'][t] = self.pstart
        nc.variables['particle_count'][t] = Npar
        nc.variables['time'][t] = t * self.outstep

        # Write to particle properties
        T = slice(self.pstart, self.pstart + Npar)
        nc.variables['pid'][T] = getattr(state, 'pid')
        for var in self.output_variables:
            nc.variables[var][T] = getattr(state, var)

        # Write
        self.pstart += Npar
        self.outcount += 1

    # --------------

    def close(self):

        self.nc.close()
