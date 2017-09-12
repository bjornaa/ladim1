"""Output module for the (py)ladim particle tracking model"""

# ------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2013-01-04
# ------------------------------------

import logging
import datetime
from typing import Any, Dict
from netCDF4 import Dataset
from .state import State                  # For mypy
from .release import ParticleReleaser     # For mypy


# Gjør til en iterator
class OutPut:

    def __init__(self,
                 config: Dict[str, Any],
                 release: ParticleReleaser) -> None:

        logging.info('Initializing output')

        self.nc = self._define_netcdf(config, release)
        self.instance_variables = config['output_instance']
        self.instance_count = 0
        self.outcount = 0    # No output yet
        self.dt = config['dt']

    def close(self):
        self.nc.close()

    def _define_netcdf(self, config: Dict[str, Any],
                       release: ParticleReleaser) -> Dataset:
        """Define a NetCDF output file"""

        logging.debug("Defining netCDF file")
        # nc = Dataset(config['output_file'], mode='w',
        nc = Dataset(config['output_file'], mode='w',
                     format="NETCDF3_64BIT_DATA")
        # --- Dimensions
        nc.createDimension('particle', release.total_particle_count)
        nc.createDimension('particle_instance', None)  # unlimited
        # Sett output-period i config (bruk naturlig enhet)
        # regne om til antall tidsteg og få inn under
        nc.createDimension('time', config['num_output'])

        # ---- Coordinate variable for time
        v = nc.createVariable('time', 'f8', ('time',))
        v.long_name = 'time'
        v.standard_name = 'time'
        v.units = 'seconds since {:s}'.format(str(config['reference_time']))

        # Particle count
        v = nc.createVariable('particle_count', 'i4', ('time',))
        v.long_name = "number of particles in a given timestep"
        v.ragged_row_count = "particle count at nth timestep"

        # Particle variables
        for name in config['output_particle']:
            v = nc.createVariable(
                name, config['nc_attributes'][name]['ncformat'],
                ('particle',))
            for attr, value in config['nc_attributes'][name].items():
                if attr != 'ncformat':
                    setattr(v, attr, value)

        # Instance variables
        for name in config['output_instance']:
            v = nc.createVariable(
                name, config['nc_attributes'][name]['ncformat'],
                ('particle_instance',))
            for attr, value in config['nc_attributes'][name].items():
                if attr != 'ncformat':
                    setattr(v, attr, value)

        # --- Global attributes
        # Burde ta f.eks. source fra setup
        # hvis andre skulle bruke
        nc.Conventions = "CF-1.5"
        nc.institution = "Institute of Marine Research"
        nc.source = "Lagrangian Advection and Diffusion Model, python version"
        nc.history = "Created by pyladim"
        nc.date = str(datetime.date.today())

        logging.debug("Netcdf output file defined")

        # Save particle variables
        for name in config['output_particle']:
            nc.variables[name][:] = release.particle_variables[name][:]

        return nc

    def write(self, state: State) -> None:
        """Write the model state to NetCDF"""

        logging.debug("Writing: timestep, timestamp = {} {}".
                      format(state.timestep, state.timestamp))
        t = self.outcount
        pcount = len(state)            # Present number of particles
        pstart = self.instance_count

        logging.debug("Writing {} particles".format(pcount))
        self.nc.variables['time'][t] = float(state.timestep * self.dt)

        self.nc.variables['particle_count'][t] = pcount

        for name in self.instance_variables:
            self.nc.variables[name][pstart:pstart+pcount] = state[name]

        # Flush the data to the file
        self.nc.sync()

        # Update counters
        self.outcount += 1
        self.instance_count += pcount
