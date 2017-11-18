"""
Configuration class for ladim
"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2017-01-17
# ----------------------------------

# import datetime
import logging
from typing import Dict, Any
import numpy as np
import yaml
import yaml.parser

Config = Dict[str, Any]   # type of the config dictionary

# config should be a dictionary - items
#
# start_time: np.datetime64
# stop_time: np.datetime64
# reference_time: np.datetime64, optional, default = start_time
#
# grid_file
# input_file
# release_file
# output_file
#
# dt: int, number of seconds
# simulation_time: computed
# numsteps: int, computed
#
# gridforce_module:
# grid_args: dictionary, optional, default = {}
# !!ibm_forcing: list, default = []
#    replace with below
# forcing_variables: (U, V may not be listed)
#
# ibm_module: optional, default = ''
#
# release_type: continuous/discrete, default='discrete'
# release_frequency: mandatory if continuous
# release_format: liste med navn på variable
#  -- gjør optional, overstyre med første linje i rls
# release_dtype: dict
# particle_variables: liste med navn
#
# ibm_variables:  (Flytte til IBM-seksjon)
# extra_variables: [temp, lon, ...]
#
# output_format: netcdf-versjon, default='NETCDF3_64BIT_OFFSET'
# output_perions: np.timedelta64
# num_output: Computed
# output_particle:
# output_instances:
# output_variables: dictionary med attributter
# -- Legg inn default for vanlige typer
#
# advection: method_string, '' for no advection
# diffusion: value, 0 for no diffusion


def configure(config_file: str) -> Config:

    config: Config = dict()

    # --- Read the configuration file ---
    # TODO: use logging.ERROR instead of print
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

    # --- Time control ---
    logging.info('Configuration: Time Control')
    for name in ['start_time', 'stop_time', 'reference_time']:
        config[name] = np.datetime64(conf['time_control'][name])
        logging.info('    {:15s}: {}'.format(name, config[name]))

    # --- Files ---
    logging.info('Configuration: Files')
    logging.info('    {:15s}: {}'.format('config_file', config_file))
    for name in ['grid_file', 'input_file',
                 'particle_release_file', 'output_file']:
        config[name] = conf['files'][name]
        logging.info('    {:15s}: {}'.format(name, config[name]))

    # --- Time stepping ---
    logging.info('Configuration: Time Stepping')
    # Read time step and convert to seconds
    dt = np.timedelta64(*tuple(conf['numerics']['dt']))
    config['dt'] = int(dt.astype('m8[s]').astype('int'))
    config['simulation_time'] = np.timedelta64(
        config['stop_time'] - config['start_time'], 's').astype('int')
    config['numsteps'] = config['simulation_time'] // config['dt']
    logging.info('    {:15s}: {} seconds'.format('dt', config['dt']))
    logging.info(
        '    {:15s}: {} hours'.format(
            'simulation time', config['simulation_time'] // 3600))
    logging.info(
        '    {:15s}: {}'.format('number of time steps', config['numsteps']))

    #  --- Grid ---
    logging.info('Configuration: gridforce')
    config['gridforce_module'] = conf['gridforce']['module']
    logging.info('    {:15s}: {}'.format('module', config['gridforce_module']))
    # Grid arguments
    try:
        config['grid_args'] = conf['gridforce']['grid']
    except KeyError:
        config['grid_args'] = dict()
    logging.info(
        '    {:15s}: {}'.format(
            'grid arguments', config['grid_args']))
    config['Vinfo'] = dict()

    # --- Forcing ---
    try:
        config['ibm_forcing'] = conf['gridforce']['ibm_forcing']
    except (KeyError, TypeError):
        config['ibm_forcing'] = []
    logging.info('    {:15s}: {}'.format('ibm_forcing', config['ibm_forcing']))

    # --- IBM ---
    try:
        config['ibm_module'] = conf['ibm']['ibm_module']
        logging.info('Configuration: IBM')
        logging.info(
            '    {:15s}: {}'.format('ibm_module', config['ibm_module']))
    # Skille på om ikke gitt, eller om navnet er feil
    except KeyError:
        config['ibm_module'] = ''

    # --- Particle release ---
    logging.info('Configuration: Particle Releaser')
    prelease = conf['particle_release']
    try:
        config['release_type'] = prelease['release_type']
    except KeyError:
        config['release_type'] = 'discrete'
    logging.info(
        '    {:15s}: {}'.format(
            'release_type', config['release_type']))
    if config['release_type'] == 'continuous':
        config['release_frequency'] = np.timedelta64(
            *tuple(prelease['release_frequency']))
        logging.info('        {:11s}: {}'.format(
            'release_frequency', str(config['release_frequency'])))
    config['release_format'] = conf['particle_release']['variables']
    config['release_dtype'] = dict()
    # Map from str to converter
    type_mapping = dict(int=int, float=float, time=np.datetime64, str=str)
    for name in config['release_format']:
        config['release_dtype'][name] = type_mapping[
            conf['particle_release'].get(name, 'float')]
        logging.info(
            '    {:15s}: {}'.format(name, config['release_dtype'][name]))
    config['particle_variables'] = prelease['particle_variables']

    # --- Model state ---
    logging.info('Configuration: Model State Variables')
    state = conf['state']
    config['state_variables'] = ['pid', 'X', 'Y', 'Z']  # Mandatory
    if state:
        # print('state = ', state)
        # print(type(config['state_variables']))
        # print(type(state['variables']))
        config['state_variables'].extend(state['variables'])
    config['ibm_variables'] = []  # Deprecated
    # else:
    #    config['ibm_variables'] = []
    # logging.info('    ibm_variables: {}'.format(config['ibm_variables']))
    logging.info('    state_variables: {}'.format(config['state_variables']))

    # --- Output control ---
    logging.info('Configuration: Output Control')
    try:
        output_format = conf['output_variables']['format']
    except KeyError:
        output_format = 'NETCDF3_64BIT_OFFSET'
    config['output_format'] = output_format
    outper = np.timedelta64(*tuple(conf['output_variables']['outper']))
    outper = outper.astype('m8[s]').astype('int') // config['dt']
    config['output_period'] = outper
    logging.info('    {:15s}: {} timesteps'.format(
        'output_period', config['output_period']))
    config['num_output'] = 1 + config['numsteps'] // config['output_period']
    logging.info('    {:15s}: {}'.format('numsteps', config['numsteps']))
    config['output_particle'] = conf['output_variables']['particle']
    config['output_instance'] = conf['output_variables']['instance']
    config['nc_attributes'] = dict()
    for name in config['output_particle'] + config['output_instance']:
        value = conf['output_variables'][name]
        if 'units' in value:
            if value['units'] == 'seconds since reference_time':
                value['units'] = 'seconds since {:s}'.format(
                    str(config['reference_time']))
        config['nc_attributes'][name] = conf['output_variables'][name]
    logging.info('    particle variables')
    for name in config['output_particle']:
        logging.info(8 * ' ' + name)
        for item in config['nc_attributes'][name].items():
            logging.info(12 * ' ' + '{:11s}: {:s}'.format(*item))
    logging.info('    particle instance variables')
    for name in config['output_instance']:
        logging.info(8 * ' ' + name)
        for item in config['nc_attributes'][name].items():
            logging.info(12 * ' ' + '{:11s}: {:s}'.format(*item))

    # --- Numerics ---
    # dt belongs here, but is already read
    logging.info('Configuration: Numerics')
    try:
        config['advection'] = conf['numerics']['advection']
    except KeyError:
        config['advection'] = 'RK4'
    logging.info('    {:15s}: {}'.format('advection', config['advection']))
    try:
        diffusion = conf['numerics']['diffusion']
    except KeyError:
        diffusion = 0.0
    if diffusion > 0:
        config['diffusion'] = True
        config['diffusion_coefficient'] = diffusion
        logging.info('    {:15s}: {}'.format(
            'diffusion coefficient',
            config['diffusion_coefficient']))
    else:
        config['diffusion'] = False
        logging.info('    no diffusion')

    return config
