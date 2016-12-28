# -*- coding: utf-8 -*-

# import datetime
import numpy as np
try:
    import configparser   # python3
except ImportError:       # python2
    import ConfigParser as configparser


class Container(object):
    """A simple container object, for the setup object"""

    # def __init__(self):
    #    pass

    def __setitem__(self, key, value):
        setattr(self, key, value)
    # def __getitem__(self, key):
    #    getattr(self, key)

# ----------------------


def read_config(config_file):

    # Default values for optional setup elements
    defaults = dict(
        dt='3600',        # one hour
        stop_time="",     # compute from nsteps
        nsteps="",        # compute from stop_time
        output_period="",
        output_period_seconds="",
        output_period_hours="",
        )

    config = configparser.ConfigParser(defaults)

    config.read(config_file)

    setup = Container()

    setup['dt'] = int(config.get('time', 'dt'))
    print(setup.dt)

    start_time = config.get('time', 'start_time')
    setup['start_time'] = np.datetime64(start_time)

    stop_time = config.get('time', 'stop_time')
    setup['stop_time'] = np.datetime64(stop_time)

    total_time = setup.stop_time - setup.start_time
    total_time = np.timedelta64(total_time, 's').astype('i')
    setup['nsteps'] = total_time // setup.dt

    # ----------
    # Input
    # ----------

    setup['grid_file'] = config.get('time', 'grid_file')
    setup['input_file'] = config.get('time', 'input_file')
    setup['particle_release_file'] =        \
        config.get('time', 'particle_release_file')

    # ---------------------
    # State variables
    # ---------------------

    pvars = config.get('variables', 'particle_variables')
    setup['particle_variables'] = []
    for v in pvars.split():
        n = v.find(':')
        setup.particle_variables.append((v[:n], v[n+1:]))

    svars = config.get('variables', 'state_variables')
    setup['state_variables'] = []
    for v in svars.split():
        n = v.find(':')
        setup.state_variables.append((v[:n], v[n+1:]))

    # ----------
    # Output
    # ----------

    # Lage seksjon [output] i sup-fil ??
    setup['output_filename'] = config.get('output', 'output_filename')

    outper = config.get('output', 'output_period')
    outper_s = config.get('output', 'output_period_seconds')
    outper_h = config.get('output', 'output_period_hours')

    if outper not in ["", None, "None"]:
        outper = int(outper)
    elif outper_s not in ["", None, "None"]:
        outper = int(outper_s) // setup.dt
    elif outper_h not in ["", None, "None"]:
        outper = int(outper_h) * 3600 // setup.dt
    setup['output_period'] = outper

    # Number of time frames in output, add one for initial distribution
    setup['Nout'] = 1 + setup.nsteps // outper

    # Output variables
    w = config.get('output', 'output_variables')
    w = w.replace(",", " ")  # replace commas with blanks
    setup['output_variables'] = w.split()

    return setup


# --------------
def write_config(setup):
    # Make an explicit sequence of keys
    # Can be improved with ordered_dict (from python 2.7)
    time_keys = ['start_time', 'stop_time', 'dt', 'nsteps']
    input_keys = ['grid_file', 'input_file', 'particle_release_file']
    variable_keys = ['particle_variables', 'state_variables']
    output_keys = ['output_filename', 'output_period',
                   'Nout', 'output_variables']

    for keylist in [time_keys, input_keys, variable_keys, output_keys]:
        print(50*"-")
        for key in keylist:
            print("%24s :" % key, getattr(setup, key))

    print(50*"-")

# -------------
# Simple test
# -------------

if __name__ == '__main__':
    config_file = '../ladim.sup'
    setup = read_config(config_file)
    write_config(setup)
