# -*- coding: utf-8 -*-

import datetime
import configparser


class Container(object):
    """A simple container object, for the setup object"""

    # def __init__(self):
    #    pass

    def __setitem__(self, key, value):
        setattr(self, key, value)
    # def __getitem__(self, key):
    #    getattr(self, key)

# ----------------------


def readsup(supfile):

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

    config.read(supfile)

    setup = Container()
#    setup = dict()

    # ---------------
    # Section [time]
    # ---------------

    # Mangler: sjekk: både stop_time og nsteps finnes
    #           gi warning dersom ikke stemmer overens
    # Dersom total_time ikke delelig med dt
    #    Reduser stop_time tilsvarende.
    #   => tidsteg 1 dag, gjør ikke noe for total_time = 3 hours
    #    Ta med å gi warning

    setup['dt'] = int(config.get('time', 'dt'))
    print(setup.dt)

    start_time = config.get('time', 'start_time')
    setup['start_time'] = datetime.datetime.strptime(
        start_time, "%Y-%m-%d %H:%M:%S")

    stop_time = config.get('time', 'stop_time')
    nsteps = config.get('time', 'nsteps')

    # nsteps overrides stop_time
    if nsteps not in ["", "None", None]:
        setup['nsteps'] = int(nsteps)
        # print setup['dt']
        # print setup['nsteps']
        setup['stop_time'] = setup.start_time    \
            + datetime.timedelta(seconds=setup.dt*setup.nsteps)

    elif stop_time not in ["", "None", None]:
        setup['stop_time'] = datetime.datetime.strptime(
            stop_time, "%Y-%m-%d %H:%M:%S")
        total_time = setup.stop_time - setup.start_time
        setup['nsteps'] = ((total_time.days*86400 + total_time.seconds)
                           // setup.dt)

    else:
        # Raise exception instead
        print("***Error in setup: must have nsteps or stop_time")
        import sys; sys.exit(1)

    # ----------
    # Input
    # ----------

    setup['grid_file'] = config.get('time', 'grid_file')
    setup['input_file'] = config.get('time', 'input_file')
    setup['particle_release_file'] =        \
        config.get('time', 'particle_release_file')

    # ----------
    # Output
    # ----------

    # Lage seksjon [output] i sup-fil ??

    setup['output_filename'] = config.get('time', 'output_filename')

    outper = config.get('time', 'output_period')
    outper_s = config.get('time', 'output_period_seconds')
    outper_h = config.get('time', 'output_period_hours')

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
    w = config.get('time', 'output_variables')
    w = w.replace(",", " ")  # replace commas with blanks
    setup['output_variables'] = w.split()

    return setup


# --------------
def writesup(setup):
    # Make an explicit sequence of keys
    # Can be improved with ordered_dict (from python 2.7)
    time_keys = ['start_time', 'stop_time', 'dt', 'nsteps']
    input_keys = ['grid_file', 'input_file', 'particle_release_file']
    output_keys = ['output_filename', 'output_period',
                   'Nout', 'output_variables']

    for keylist in [time_keys, input_keys, output_keys]:
        print(50*"-")
        for key in keylist:
            print("%24s :" % key, getattr(setup, key))

    print(50*"-")


# -------------
# Simple test
# -------------

if __name__ == '__main__':
    supfile = '../ladim.sup'
    setup = readsup(supfile)
    writesup(setup)
