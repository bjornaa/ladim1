"""
Configuration class for ladim
"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institue of Marine Research
# 2017-01-17
# ----------------------------------

# import datetime
import logging
import numpy as np
import yaml

# Loggng set-up
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Configure():

    def __init__(self, config_file, loglevel=logging.WARNING):

        logger.setLevel(loglevel)

        # --- Read the configuration file ---
        with open(config_file) as fp:
            conf = yaml.safe_load(fp)

        # --- Time control ---
        logger.info('Configuration: Time Control')
        for name in ['start_time', 'stop_time', 'reference_time']:
            self[name] = conf['time_control'][name]
            logger.info('    {:15s}: {}'.format(name, self[name]))

        # --- Files ---
        logger.info('Configuration: Files')
        for name in ['grid_file', 'input_file',
                     'particle_release_file', 'output_file']:
            self[name] = conf['files'][name]
            logger.info('    {:15s}: {}'.format(name, self[name]))

        # --- Time steping ---
        logger.info('Configuration: Time Stepping')
        # Read time step and convert to seconds
        dt = np.timedelta64(*tuple(conf['ymse']['dt']))
        self.dt = dt.astype('m8[s]').astype('int')
        self.simulation_time = np.timedelta64(
            self.stop_time - self.start_time, 's').astype('int')
        self.numsteps = self.simulation_time // self.dt
        logger.info('    {:15s}: {} seconds'.format('dt', self.dt))
        logger.info('    {:15s}: {} hours'.format('simulation time',
                    self.simulation_time // 3600))
        logger.info('    {:15s}: {}'.format('number of time steps',
                    self.numsteps))

        # --- Particle release ---
        logger.info('Configuration: Particle Releaser')
        prelease = conf['particle_release']
        self.release_format = conf['particle_release']['variables']
        self.release_dtype = dict()
        for name in self.release_format:
            self.release_dtype[name] = (
                conf['particle_release'].get(name, 'float'))
            logger.info('    {:15s}: {}'.
                        format(name, self.release_dtype[name]))
        self.particle_variables = prelease['particle_variables']

        # --- Model state ---
        logger.info('Configuration: Model State Variables')
        state = conf['state']
        if state:
            v = state['ibm_variables']
            if v:
                self.ibm_variables = v
        else:
            self.ibm_variables = []
        logger.info('    ibm_variables: {}'.format(self.ibm_variables))

        # --- Forcing ---
        logger.info('Configuration: Forcing')
        self.velocity = conf['forcing']['velocity']
        logger.info('    {:15s}: {}'.format('velocity', self.velocity))
        self.ibm_forcing = conf['forcing']['ibm_forcing']
        logger.info('    {:15s}: {}'.format('ibm_forcing', self.ibm_forcing))

        # --- Output control ---
        logger.info('Configuration: Output Control')
        outper = np.timedelta64(*tuple(conf['output_variables']['outper']))
        outper = outper.astype('m8[s]').astype('int') // self['dt']
        self.output_period = outper
        logger.info('    {:15s}: {} timesteps'.format(
                    'output_period', self.output_period))
        self.num_output = 1 + self.numsteps // self.output_period
        logger.info('    {:15s}: {}'.format('numsteps', self.numsteps))
        self.output_particle = conf['output_variables']['particle']
        self.output_instance = conf['output_variables']['instance']
        self.nc_attributes = dict()
        for name in self.output_particle + self.output_instance:
            value = conf['output_variables'][name]
            if 'units' in value:
                if value['units'] == 'seconds since reference_time':
                    value['units'] = 'seconds since {:s}'.format(
                        str(self.reference_time))
            self.nc_attributes[name] = conf['output_variables'][name]
        logger.info('    particle variables')
        for name in self.output_particle:
            logger.info(8*' ' + name)
            for item in self.nc_attributes[name].items():
                logger.info(12*' ' + '{:11s}: {:s}'.format(*item))
        logger.info('    particle instance variables')
        for name in self.output_instance:
            logger.info(8*' ' + name)
            for item in self.nc_attributes[name].items():
                logger.info(12*' ' + '{:11s}: {:s}'.format(*item))

    # Allow item notation
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

# # -------------
# # Simple test
# # -------------
#
if __name__ == '__main__':
    config = Configure('../ladim.yaml', loglevel='INFO')
