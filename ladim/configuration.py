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
from netCDF4 import Dataset, num2date

Config = Dict[str, Any]   # type of the config dictionary


def configure(config_file: str) -> Config:

    config: Config = dict()

    # --- Read the configuration file ---
    # TODO: use logging.ERROR instead of print
    try:
        with open(config_file, encoding='utf8') as fp:
            conf = yaml.safe_load(fp)
    except FileNotFoundError:
        print('ERROR: ',
              f'Configuration file {config_file} not found')
        raise SystemExit(1)
    except yaml.parser.ParserError:
        print('ERROR: ',
              f'Can not parse configuration file {config_file}')
        raise SystemExit(2)

    # ----------------
    # Time control
    # ----------------
    logging.info('Configuration: Time Control')
    for name in ['start_time', 'stop_time']:
        config[name] = np.datetime64(
            conf['time_control'][name]).astype('M8[s]')
        logging.info(f'    {name:15s}: {config[name]}')
    try:
        config['reference_time'] = np.datetime64(
            conf['time_control']['reference_time']).astype('M8[s]')
    except KeyError:
        config['reference_time'] = config['start_time']
    logging.info(f'    {"reference_time":15s}: {config["reference_time"]}')

    # -------------
    # --- Files ---
    # -------------
    logging.info('Configuration: Files')
    logging.info(f'    {"config_file":15s}: {config_file}')
    for name in ['grid_file', 'input_file',
                 'particle_release_file', 'output_file']:
        config[name] = conf['files'][name]
        logging.info(f'    {name:15s}: {config[name]}')

    try:
        config['warm_start_file'] = conf['files']['warm_start_file']
        config['start'] = 'warm'
        logging.info(f'    {"Warm start from":15s}: {config["warm_start_file"]}')
    except KeyError:
        config['start'] = 'cold'
        config['warm_start_file'] = ''

    # Override start time for warm start
    if config['start'] == 'warm':
        try:
            nc = Dataset(config['warm_start_file'])
        except (FileNotFoundError, OSError):
            logging.error(
                f"Could not open warm start file,{config['warm_start_file']}")
            raise SystemExit(1)
        tvar = nc.variables['time']
        # Use last record in restart file
        warm_start_time = np.datetime64(num2date(tvar[-1], tvar.units))
        warm_start_time = warm_start_time.astype('M8[s]')
        config['start_time'] = warm_start_time
        logging.info(f'warm start at {warm_start_time}')

        # Variables needed by restart, might be changed
        # default should be instance variables among release variables
        try:
            warm_start_variables = conf['warm_start_variables']
        except KeyError:
            warm_start_variables = ['X', 'Y', 'Z']
        config['warm_start_variables'] = warm_start_variables

    # --- Time stepping ---
    logging.info('Configuration: Time Stepping')
    # Read time step and convert to seconds
    dt = np.timedelta64(*tuple(conf['numerics']['dt']))
    config['dt'] = int(dt.astype('m8[s]').astype('int'))
    config['simulation_time'] = np.timedelta64(
        config['stop_time'] - config['start_time'], 's').astype('int')
    config['numsteps'] = config['simulation_time'] // config['dt']
    logging.info(f'    {"dt":15s}: {config["dt"]} seconds')
    logging.info(
        f'    {"simulation time":15s}: {config["simulation_time"] // 3600} hours')
    logging.info(f'    {"number of time steps":15s}: {config["numsteps"]}')

    #  --- Grid ---
    logging.info('Configuration: gridforce')
    config['gridforce_module'] = conf['gridforce']['module']
    logging.info(f'    {"module":15s}: {config["gridforce_module"]}')
    # Grid arguments
    try:
        config['grid_args'] = conf['gridforce']['grid']
    except KeyError:
        config['grid_args'] = dict()
    logging.info(
        f'    {"grid arguments":15s}: {config["grid_args"]}')
    config['Vinfo'] = dict()

    # --- Forcing ---
    try:
        config['ibm_forcing'] = conf['gridforce']['ibm_forcing']
    except (KeyError, TypeError):
        config['ibm_forcing'] = []
    logging.info(f'    {"ibm_forcing":15s}: {config["ibm_forcing"]}')

    # --- IBM ---
    try:
        config['ibm_module'] = conf['ibm']['ibm_module']
        logging.info('Configuration: IBM')
        logging.info(f'    {"ibm_module":15s}: {config["ibm_module"]}')
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
        f'    {"release_type":15s}: {config["release_type"]}')
    if config['release_type'] == 'continuous':
        config['release_frequency'] = np.timedelta64(
            *tuple(prelease['release_frequency']))
        logging.info(f'        {"release_frequency":11s}: {str(config["release_frequency"])}')
    config['release_format'] = conf['particle_release']['variables']
    config['release_dtype'] = dict()
    # Map from str to converter
    type_mapping = dict(int=int, float=float, time=np.datetime64, str=str)
    for name in config['release_format']:
        config['release_dtype'][name] = type_mapping[
            conf['particle_release'].get(name, 'float')]
        logging.info(
            f'    {name:15s}: {config["release_dtype"][name]}')
    config['particle_variables'] = prelease['particle_variables']

    # --- Model state ---
    logging.info('Configuration: Model State Variables')
    state = conf['state']
    if state:
        config['ibm_variables'] = state['ibm_variables']
    else:
        config['ibm_variables'] = []
    logging.info(f'    ibm_variables: {config["ibm_variables"]}')

    # -----------------
    # Output control
    # -----------------
    logging.info('Configuration: Output Control')
    try:
        output_format = conf['output_variables']['format']
    except KeyError:
        output_format = 'NETCDF3_64BIT_OFFSET'
    config['output_format'] = output_format
    logging.info(f'    {"output_format":15s}: {config["output_format"]}')

    # Skip output of initial state, useful for restart
    # with cold start the default is False
    # with warm start, the default is true
    try:
        skip_initial = conf['output_variables']['skip_initial']
    except KeyError:
        if config['start'] == 'warm':
            skip_initial = True
        else:
            skip_initial = False
    config['skip_initial'] = skip_initial
    logging.info(f"    {'skip_inital':15s}: {skip_initial}")

    try:
        numrec = conf['output_variables']['numrec']
    except KeyError:
        numrec = 0
    config['output_numrec'] = numrec
    logging.info(f'    {"output_numrec":15s}: {config["output_numrec"]}')

    outper = np.timedelta64(*tuple(conf['output_variables']['outper']))
    outper = outper.astype('m8[s]').astype('int') // config['dt']
    config['output_period'] = outper
    logging.info(f'    {"output_period":15s}: {config["output_period"]} timesteps')
    config['num_output'] = 1 + config['numsteps'] // config['output_period']
    logging.info(f'    {"numsteps":15s}: {config["numsteps"]}')
    config['output_particle'] = conf['output_variables']['particle']
    config['output_instance'] = conf['output_variables']['instance']
    config['nc_attributes'] = dict()
    for name in config['output_particle'] + config['output_instance']:
        value = conf['output_variables'][name]
        if 'units' in value:
            if value['units'] == 'seconds since reference_time':
                timeref = str(config['reference_time']).replace('T', ' ')
                value['units'] = f'seconds since {timeref}'
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
    logging.info(f'    {"advection":15s}: {config["advection"]}')
    try:
        diffusion = conf['numerics']['diffusion']
    except KeyError:
        diffusion = 0.0
    if diffusion > 0:
        config['diffusion'] = True
        config['diffusion_coefficient'] = diffusion
        logging.info(f'    {"diffusion coefficient":15s}: {config["diffusion_coefficient"]}')
    else:
        config['diffusion'] = False
        logging.info('    no diffusion')

    return config
