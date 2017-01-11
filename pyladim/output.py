# -*- coding: utf-8 -*-

"""Output module for the (py)ladim particle tracking model"""

# ------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2013-01-04
# ------------------------------------

import datetime
from netCDF4 import Dataset


class OutPut():

    def __init__(self, config):

        nc = Dataset(config.output_file, mode='w',
                     format="NETCDF3_CLASSIC")
        # --- Dimensions
        nc.createDimension('particle_instance', None)  # unlimited
        nc.createDimension('particle', 100)
        nc.createDimension('time', 10)

        # ---- Coordinate variable for time
        v = nc.createVariable('time', 'f8', ('time',))
        v.long_name = 'time'
        v.standard_name = 'time'
        v.units = 'seconds since {:s}'.format(str(config.reference_time))

        # Particle variables
        for name in config['output_particle']:
            v = nc.createVariable(
                name, config['nc_attributes'][name]['ncformat'],
                ('particle',))
            for attr, value in config['nc_attributes'][name].items():
                if attr != 'ncformat':
                    setattr(v, attr, value)
        print('particle finshed')

        # Instance variables
        for name in config['output_instance']:
            v = nc.createVariable(
                name, config['nc_attributes'][name]['ncformat'],
                ('particle_instance',))
            for attr, value in config['nc_attributes'][name].items():
                if attr != 'ncformat':
                    setattr(v, attr, value)

        # --- Global attributes
        nc.Conventions = "CF-1.5"
        nc.institution = "Institute of Marine Research"
        nc.source = "Lagrangian Advection and DIffusion Model, python version"
        nc.history = "Created by pyladim"
        nc.date = str(datetime.date.today())

        nc.close()

        # --- Initialize
        # self.nc = nc
        # self.outcount = 0
        # self.pstart = 0
        # self.outstep = config.output_period * config.dt
        # self.output_variables = config.output_variables
        # self.pvars = config.output_variables

    # --------------
    #
    # def _write_particle_vars(self):
    #     """
    #     Write time independent particle variables
    #     """
    #
    #     nc = self.nc
    #     nc.variables['farmid'][:]) = particle_vars['farmid']
    #
    #
    #
    # def write(self, state):
    #     """
    #     Write a particle distribution
    #     """
    #
    #     Npar = len(state)
    #     t = self.outcount
    #     nc = self.nc
    #
    #     # Write to time variables
    #     # nc.variables['pstart'][t] = self.pstart
    #     nc.variables['particle_count'][t] = Npar
    #     nc.variables['time'][t] = t * self.outstep
    #
    #     # Write to particle properties
    #     T = slice(self.pstart, self.pstart + Npar)
    #     nc.variables['pid'][T] = getattr(state, 'pid')
    #     for var in self.output_variables:
    #         nc.variables[var][T] = getattr(state, var)
    #
    #     # Write
    #     self.pstart += Npar
    #     self.outcount += 1
    #
    # # --------------
    #
    # def close(self):
    #
    #     self.nc.close()

if __name__ == '__main__':

    import ladim_config

    config_file = '../ladim.yaml'
    config = ladim_config.read_config(config_file)
    config.output_file = '../output/a.nc'
    out = OutPut(config)
