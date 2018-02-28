"""Output module for the (py)ladim particle tracking model"""

# ------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2013-01-04
# ------------------------------------

import os
import logging
import datetime
from typing import Any, Dict
import numpy as np
from netCDF4 import Dataset

from .gridforce import Grid               # For mypy
from .state import State                  # For mypy
from .release import ParticleReleaser     # For mypy


# Gjør til en iterator
class OutPut:

    def __init__(self,
                 config: Dict[str, Any],
                 release: ParticleReleaser) -> None:

        logging.info('Initializing output')

        self.instance_variables = config['output_instance']
        self.instance_count = 0
        self.outcount = -1    # No output yet
        if config['skip_initial']:
            self.outcount = -2
        self.numrec = config['output_numrec']
        if self.numrec == 0:
            self.multi_file = False
            self.numrec = 999999  # A large number
        else:
            self.multi_file = True
        self.dt = config['dt']
        self.config = config    # Better to extract the things needed
        self.release = release
        self.file_counter = -1
        self.num_output = config['num_output']
        self.nc = None   # No open netCDF file yet
         # Indicator for lon/lat output
        self.lonlat = ('lat' in self.instance_variables or
                       'lon' in self.instance_variables)


    # ----------------------------------------------
    def write(self, state: State,  grid: Grid) -> None:
        """Write the model state to NetCDF"""

        self.outcount += 1
        if self.outcount < 0:  # skip_initial == True
            return
        t = self.outcount % self.numrec   # in-file record counter

        logging.debug("Writing: timestep, timestamp = {} {}".
                      format(state.timestep, state.timestamp))

        # Create new file?
        if t == 0:
            # Close old file and open a new
            if self.nc:
                self.nc.close()
            self.file_counter += 1
            self.pstart0 = self.instance_count      # Start of data in the file
            self.nc = self._define_netcdf()
            logging.info(f"Opened output file: {self.nc.filepath()}")

        pcount = len(state)            # Present number of particles
        pstart = self.instance_count

        logging.debug(f"Writing {pcount} particles")

        tdelta = state.timestamp - self.config['reference_time']
        seconds = tdelta.astype('m8[s]').astype('int')
        self.nc.variables['time'][t] = float(seconds)

        self.nc.variables['particle_count'][t] = pcount

        # Compute lon, lat if needed
        if self.lonlat:
            lon, lat = grid.lonlat(state.X, state.Y)

        start = pstart - self.pstart0
        end = pstart + pcount - self.pstart0
        # print("start, end = ", start, end)
        for name in self.instance_variables:
            if name == 'lon':
                self.nc.variables['lon'][start:end] = lon
            elif name == 'lat':
                self.nc.variables['lat'][start:end] = lat
            else:
                self.nc.variables[name][start:end] = state[name]


        # Update counters
        # self.outcount += 1
        self.instance_count += pcount

        # Flush the data to the file
        self.nc.sync()

        # Close final file
        if self.outcount == self.num_output - 1:
            self.nc.close()

    # -----------------------------------------------
    def _define_netcdf(self) -> Dataset:
        """Define a NetCDF output file"""

        # Generate file name
        fname = self.config['output_file']
        if self.multi_file:
            # fname = fname0.nc -> fname0_xxxx.nc
            fname0, ext = os.path.splitext(fname)
            fname = f'{fname0}_{self.file_counter:04d}{ext}'

        logging.debug(f"Defining output netCDF file: {fname}")
        nc = Dataset(fname, mode='w',
                     format=self.config['output_format'])
        # --- Dimensions
        nc.createDimension('particle', self.release.total_particle_count)
        nc.createDimension('particle_instance', None)  # unlimited
        # Sett output-period i config (bruk naturlig enhet)
        # regne om til antall tidsteg og få inn under
        outcount0 = self.outcount
        outcount1 = min(outcount0+self.numrec, self.num_output)
        nc.createDimension('time', outcount1-outcount0)

        # ---- Coordinate variable for time
        v = nc.createVariable('time', 'f8', ('time',))
        v.long_name = 'time'
        v.standard_name = 'time'
        timeref = str(self.config['reference_time']).replace('T', ' ')
        v.units = f'seconds since {timeref}'

        # instance_offset
        v = nc.createVariable('instance_offset', 'i', ())
        v.long_name = "particle instance offset for file"

        # Particle count
        v = nc.createVariable('particle_count', 'i4', ('time',))
        v.long_name = "number of particles in a given timestep"
        v.ragged_row_count = "particle count at nth timestep"

        # Particle variables
        for name in self.config['output_particle']:
            confname = self.config['nc_attributes'][name]
            if confname['ncformat'][0] == 'S':   # text
                length = int(confname['ncformat'][1:])
                lendimname = 'len_' + name
                nc.createDimension(lendimname, length)
                v = nc.createVariable(
                    varname=name,
                    datatype='S1',
                    dimensions=('particle', lendimname),
                    zlib=True)
            else:   # Numeric
                v = nc.createVariable(
                    varname=name,
                    datatype=self.config['nc_attributes'][name]['ncformat'],
                    dimensions=('particle',),
                    zlib=True)
            for attr, value in self.config['nc_attributes'][name].items():
                if attr != 'ncformat':
                    setattr(v, attr, value)

        # Instance variables
        for name in self.config['output_instance']:
            v = nc.createVariable(
                varname=name,
                datatype=self.config['nc_attributes'][name]['ncformat'],
                dimensions=('particle_instance',),
                zlib=True)

            for attr, value in self.config['nc_attributes'][name].items():
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
        for name in self.config['output_particle']:
            var = nc.variables[name]
            if var.datatype == np.dtype('S1'):   # Text
                n = len(nc.dimensions[var.dimensions[-1]])
                A = [list(s[:n].ljust(n))
                     for s in self.release.particle_variables[name][:]]
                var[:] = np.array(A)
            else:    # Numeric
                nc.variables[name][:] = \
                    self.release.particle_variables[name][:]

        # Set instance offset
        var = nc.variables['instance_offset']
        var[:] = self.instance_count

        return nc
