# -*- coding: utf-8 -*-

# import datetime
import numpy as np
import yaml


class Container(object):
    """A simple container class, for the config object

       Can use both dictionary and attribute notation
    """

    # def __init__(self):
    #    pass

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

# ----------------------


def read_config(config_file):

    config = Container()

    with open(config_file) as fp:
        conf = yaml.safe_load(fp)

    for name in ['start_time', 'stop_time', 'reference_time']:
        config[name] = conf['time_control'][name]
    # config['start_time'] = conf['time_control']['start_time']
    # config['stop_time'] = conf['time_control']['stop_time']
    # config['reference_time'] = conf['time_control']['reference_time']

    for name in ['grid_file', 'input_file',
                 'particle_release_file', 'output_file']:
        config[name] = conf['files'][name]

    config['release_format'] = conf['particle_release']['variables']
    print(config.release_format)
    config['release_dtype'] = dict()
    for name in config['release_format']:
        config['release_dtype'][name] = conf['particle_release'].get(
            name, 'float')

    # Output
    config['output_particles'] = conf['output_variables']['particle']
    config['output_instances'] = conf['output_variables']['instance']
    config['nc_attributes'] = dict()
    for name in config.output_particles + config.output_instances:
        config['nc_attributes'][name] = conf['output_variables'][name]

    # Various
    config['dt'] = conf['ymse']['dt']

    simulation_time = np.timedelta64(
        config['stop_time'] - config['start_time'], 's').astype('int')
    config['nsteps'] = simulation_time / config['dt']
    print("Number of time steps = ", config['nsteps'])

    outper = np.timedelta64(*tuple(conf['ymse']['outper']))
    print(outper)
    config['outper'] = outper.astype('m8[s]').astype('int')
    print(config['outper'])

#     setup['dt'] = int(config.get('time', 'dt'))
#
#
#     total_time = setup.stop_time - setup.start_time
#     total_time = np.timedelta64(total_time, 's').astype('i')
#     setup['nsteps'] = total_time // setup.dt
#
#     # ---------------------
#     # State variables
#     # ---------------------
#
#     # Få bedre hva som
#     pvars = config.get('variables', 'particle_variables')
#     setup['particle_variables'] = []
#     for v in pvars.split():
#         converter = float
#         n = v.find(':')
#         if n < 0:  # default = float
#             name = v
#         else:
#             name = v[:n]
#             dtype = v[n+1:]
#             if dtype == 'int':
#                 converter = int
#         setup.particle_variables.append((name, converter))
#
#     svars = config.get('variables', 'extra_state_variables')
#     setup['extra_state_variables'] = []
#     for v in svars.split():
#         converter = float
#         n = v.find(':')
#         if n < 0:  # default = float
#             name = v
#         else:
#             name = v[:n]
#             dtype = v[n+1:]
#             if dtype == 'int':
#                 converter = int
#         setup.extra_state_variables.append((name, converter))
#
#     # ----------
#     # Output
#     # ----------
#
#     # Lage seksjon [output] i sup-fil ??
#     setup['output_filename'] = config.get('output', 'output_filename')
#
#     ref_time = config.get('output', 'reference_time')
#     if not ref_time:
#         ref_time = setup.start_time
#     setup['reference_time'] = np.datetime64(ref_time)
#
#     outper = config.get('output', 'output_period')
#     outper_s = config.get('output', 'output_period_seconds')
#     outper_h = config.get('output', 'output_period_hours')
#
#     if outper not in ["", None, "None"]:
#         outper = int(outper)
#     elif outper_s not in ["", None, "None"]:
#         outper = int(outper_s) // setup.dt
#     elif outper_h not in ["", None, "None"]:
#         outper = int(outper_h) * 3600 // setup.dt
#     setup['output_period'] = outper
#
#     # Number of time frames in output, add one for initial distribution
#     setup['Nout'] = 1 + setup.nsteps // outper
#
#     # Output variables
#     w = config.get('output', 'output_variables')
#     w = w.replace(",", " ")  # replace commas with blanks
#     setup['output_variables'] = w.split()
#
    return config
#
#
# # --------------


def write_config(config):

    time_keys = ['start_time', 'stop_time', 'reference_time']
    file_keys = ['grid_file', 'input_file', 'particle_release_file',
                 'output_file']

    for key in time_keys:
        print('{:24s}:'.format(key), getattr(config, key))

    print("---")

    for key in file_keys:
        print('{:24s}:'.format(key), getattr(config, key))

    print("---")

    print('particle release format')
    for key in config.release_format:
        print('    {:20s}:'.format(key), config.release_dtype[key])

    print("---")
    # Kan skrives penere
    print("Output variables")
    print("  Particle variables")
    for name in config.output_particles:
        print('    {:20s}:'.format(name), config.nc_attributes[name])
    print("  Particle instance variables")
    for name in config.output_instances:
        print('    {:20s}:'.format(name), config.nc_attributes[name])


# def write_config(setup):
#     # Make an explicit sequence of keys
#     # Can be improved with ordered_dict (from python 2.7)
#     time_keys = ['start_time', 'stop_time', 'dt', 'nsteps']
#     input_keys = ['grid_file', 'input_file', 'particle_release_file']
#     variable_keys = ['particle_variables', 'extra_state_variables']
#     output_keys = ['output_filename', 'output_period',
#                    'Nout', 'output_variables']
#
#     for keylist in [time_keys, input_keys, variable_keys, output_keys]:
#         print(50*"-")
#         for key in keylist:
#             print("%24s :" % key, getattr(setup, key))
#
#     print(50*"-")
#
# # -------------
# # Simple test
# # -------------
#
if __name__ == '__main__':
    config_file = '../ladim.yaml'
    config = read_config(config_file)
    write_config(config)
