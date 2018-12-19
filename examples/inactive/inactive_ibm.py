import numpy as np

# Minimal IBM to demonstrate inactive particles

DAY = 24*60*60   # Number of seconds in a day


class IBM:

    def __init__(self, config):
        print("Initializing killer feature")
        pass

    def update_ibm(self, grid, state, forcing):
        # Make all active at certain time
        if state.timestamp > np.datetime64('1989-06-01'):
            state.active = np.ones_like(state.pid)
