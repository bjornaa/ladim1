# -*- coding: utf-8 -*-

# Placeholder for behaviour
# important: removes inactive particles


# import numpy as np


def behaviour(state):

    pass

    # pid = state['pid']
    # X   = state['X']
    # Y   = state['Y']

    # pcount = len(pid)

    # print "pcount = ", pcount

    # active = np.array(pcount*[True])   # all particles are active

    #  Stupid criterium for testing
    # active = np.logical_and(active, Y < 120)

    # Remove inactive particles
    # Better than copy, find something that copies
    # if non-contiguos

    # Loop over alle state-variable

    # state['pid'] = np.ascontiguousarray(pid[active])
    # state['X'] = X[active].copy()
    # state['Y'] = Y[active].copy()
    # state['Z'] = state['Z'][active].copy()

    # Sjekk om partikkel innenfor området
