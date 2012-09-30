# -*- coding: utf-8 -*-

import datetime
import ConfigParser

def readsup(supfile):

    defaults = dict(
        dt = '3600',        # one hour
        stop_time = None,   # compute from nsteps
        nsteps = None,      # compute from stop_time
        )

    config = ConfigParser.ConfigParser(defaults)

    config.read(supfile)

    setup = {}

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

    start_time = config.get('time', 'start_time')
    setup['start_time'] = datetime.datetime.strptime(start_time, 
                                   "%Y-%m-%d %H:%M:%S")

    stop_time = config.get('time', 'stop_time')
    nsteps = config.get('time', 'nsteps')

    if not stop_time in ["", "None", None]:
        setup['stop_time'] = datetime.datetime.strptime(stop_time, 
                                   "%Y-%m-%d %H:%M:%S")
        total_time = setup['stop_time'] - setup['start_time']
        setup['nsteps'] = ( (total_time.days*86400 + total_time.seconds) 
                             // setup['dt'] )
    elif not nsteps in ["", "None", None]:
        setup['nsteps'] = int(nsteps)
        setup['stop_time'] = setup['start_time']    \
            + datetime.timedelta(seconds=setup['dt']*setup['nsteps'])
    else:
        # Raise exception instead
        print "***Error in setup: must have nsteps or stop_time"
        import sys; sys.exit(1)
        
    return setup

# ---
# Ha en write-sup method ??
# Får penere utskrift når kjører test


# -------------
# Simple test
# -------------

if __name__ == '__main__':
    supfile = 'ladim.sup'
    setup = readsup(supfile)
    for key in setup:
        print "%20s " % key, setup[key]  # Få til venstrjustering

                 

