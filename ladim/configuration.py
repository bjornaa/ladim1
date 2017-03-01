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


class Configure:
    def __init__(self, config_file, loglevel=logging.WARNING):

        # --- Read the configuration file ---
        try:
            with open(config_file) as fp:
                conf = yaml.safe_load(fp)
        except FileNotFoundError:
            print('ERROR: ',
                  'Configuration file {} not found'.format(config_file))
            raise SystemExit(1)
        except yaml.parser.ParserError:
            print('ERROR: ',
                  'Can not parse configuration file {}'.format(config_file))
            raise SystemExit(2)

        # --- Logging control ---
        try:
            loglevel = conf['logging'][loglevel]
        except KeyError:
            loglevel = logging.INFO
        logging.basicConfig(
            level=loglevel,
            format='%(levelname)s %(module)s - %(message)s')
        level2str = {0: 'NOTSET',
                     10: 'DEBUG',
                     20: 'INFO',
                     30: 'WARNING',
                     40: 'ERROR',
                     50: 'CRITICAL'}
        logging.info('Configuration: Logging')
        logging.info('    {:15s}: {}'.format('loglevel', level2str[loglevel]))
        logging.debug('AAAA')

        # --- Time control ---
        logging.info('Configuration: Time Control')
        for name in ['start_time', 'stop_time', 'reference_time']:
            self[name] = np.datetime64(conf['time_control'][name])
            logging.info('    {:15s}: {}'.format(name, self[name]))

        # --- Files ---
        logging.info('Configuration: Files')
        logging.info('    {:15s}: {}'.format('config_file', config_file))
        for name in ['grid_file', 'input_file',
                     'particle_release_file', 'output_file']:
            self[name] = conf['files'][name]
            logging.info('    {:15s}: {}'.format(name, self[name]))

        # --- Time steping ---
        logging.info('Configuration: Time Stepping')
        # Read time step and convert to seconds
        dt = np.timedelta64(*tuple(conf['numerics']['dt']))
        self.dt = int(dt.astype('m8[s]').astype('int'))
        self.simulation_time = np.timedelta64(
            self.stop_time - self.start_time, 's').astype('int')
        self.numsteps = self.simulation_time // self.dt
        logging.info('    {:15s}: {} seconds'.format('dt', self.dt))
        logging.info('    {:15s}: {} hours'.
                     format('simulation time', self.simulation_time // 3600))
        logging.info('    {:15s}: {}'.
                     format('number of time steps', self.numsteps))

        # --- Grid ---
        logging.info('Configuration: gridforce')
        self.gridforce_module = conf['gridforce']['module']
        logging.info('    {:15s}: {}'.format('module', self.gridforce_module))
        # Grid arguments
        try:
            self.grid_args = conf['gridforce']['grid']
        except KeyError:
            self.grid_args = {}
        logging.info('    {:15s}: {}'.format('grid arguments', self.grid_args))
        self.Vinfo = {}

        # --- Forcing ---
        # self.velocity = conf['gridforce']['velocity']
        # logging.info('    {:15s}: {}'.format('velocity', self.velocity))
        try:
            self.ibm_forcing = conf['gridforce']['ibm_forcing']
        except (KeyError, TypeError):
            self.ibm_forcing = []
        logging.info('    {:15s}: {}'.format('ibm_forcing', self.ibm_forcing))

        # --- IBM ---
        try:
            self.ibm_module = conf['ibm']['ibm_module']
            logging.info('Configuration: IBM')
            logging.info('    {:15s}: {}'.format('ibm_module',
                                                 self.ibm_module))
        # Skille på om ikke gitt, eller om navnet er feil
        except KeyError:
            self.ibm_module = ''

        # --- Particle release ---
        logging.info('Configuration: Particle Releaser')
        prelease = conf['particle_release']
        try:
            self.release_type = prelease['release_type']
        except KeyError:
            self.release_type = 'discrete'
        logging.info('    {:15s}: {}'.format('release_type',
                                             self.release_type))
        if self.release_type == 'continuous':
            self.release_frequency = np.timedelta64(
                *tuple(prelease['release_frequency']))
            logging.info('        {:11s}: {}'.format(
                'release_frequency', str(self.release_frequency)))
        self.release_format = conf['particle_release']['variables']
        self.release_dtype = dict()
        # Map from str to converter
        type_mapping = dict(int=int, float=float, time=np.datetime64)
        for name in self.release_format:
            self.release_dtype[name] = type_mapping[
                conf['particle_release'].get(name, 'float')]
            logging.info('    {:15s}: {}'.
                         format(name, self.release_dtype[name]))
        self.particle_variables = prelease['particle_variables']

        # --- Model state ---
        logging.info('Configuration: Model State Variables')
        state = conf['state']
        if state:
            self.ibm_variables = state['ibm_variables']
        else:
            self.ibm_variables = []
        logging.info('    ibm_variables: {}'.format(self.ibm_variables))

        # --- Output control ---
        logging.info('Configuration: Output Control')
        outper = np.timedelta64(*tuple(conf['output_variables']['outper']))
        outper = outper.astype('m8[s]').astype('int') // self['dt']
        self.output_period = outper
        logging.info('    {:15s}: {} timesteps'.format(
            'output_period', self.output_period))
        self.num_output = 1 + self.numsteps // self.output_period
        logging.info('    {:15s}: {}'.format('numsteps', self.numsteps))
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
        logging.info('    particle variables')
        for name in self.output_particle:
            logging.info(8 * ' ' + name)
            for item in self.nc_attributes[name].items():
                logging.info(12 * ' ' + '{:11s}: {:s}'.format(*item))
        logging.info('    particle instance variables')
        for name in self.output_instance:
            logging.info(8 * ' ' + name)
            for item in self.nc_attributes[name].items():
                logging.info(12 * ' ' + '{:11s}: {:s}'.format(*item))

        # --- Numerics ---
        # dt belongs here, but is already read
        logging.info('Configuration: Numerics')
        try:
            self.advection = conf['numerics']['advection']
        except KeyError:
            self.advection = 'RK4'
        logging.info('    {:15s}: {}'.format('advection', self.advection))
        try:
            diffusion = conf['numerics']['diffusion']
        except KeyError:
            diffusion = 0.0
        if diffusion > 0:
            self.diffusion = True
            self.diffusion_coefficient = diffusion
            logging.info('    {:15s}: {}'.format(
                'diffusion coefficient',
                self.diffusion_coefficient))
        else:
            self.diffusion = False
            logging.info('    no diffusion')

    # -------------------------------------

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
