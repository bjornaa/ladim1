# Particle release class

# -------------------
# release.py
# part of LADIM
# --------------------

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# Bergen, Norway
# ----------------------------------

# Timing
# Allow release both before or after stop/start time
# A warning is issued and the particles ignored.
#
# Usage: A large release file, but running bits and pieces
# with restart
#
# particle release at start_time are considered
# particle release at stop_time is not considered?
#
# Has to think more about restart:
# start of next = last time on output file
# restart: do not write initial

# First release after start_time: issue warning
# Warning must be: ladim running with no particles

# For restart, no problem: t

# Sequence:
# date clock mult X Y Z [particle_variables] [state_variables]
# date must have format yyyy-mm-dd
# clock can have hh:mm:ss, hh:mm or simply 0-23 for hour only
# The number and order of particle_variables and state_variables
# are given by the names attribute in the ParticleVariables and State
# instances

# Example: salmon lice
# date clock mult X Y Z farm_id age super
# 2016-03-11 6 3 366 464 5 10147 0 1000

import logging
import numpy as np
# import pandas as pd

# ------------------------

logger = logging.getLogger(__name__)
# ch = logging.StreamHandler()
# formatter = logging.Formatter('%(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)


class ParticleReleaser:
    """Particle Release Class"""

    def __init__(self, config, loglevel=logging.INFO):

        # print("loglevel = ", loglevel)
        logger.setLevel(loglevel)

        # release_type = config.release_type

        # På nytt, men lager dict av arrayer/lister
        V = dict()
        for key in config.release_format:
            V[key] = []

        # --- Read the particle release file ---

        with open(config.particle_release_file) as f:
            for line in f:
                w = line.split()
                # Handle time format in two words, yyyy-mm-dd hh:mm:ss
                if len(w) == len(config.release_format) + 1:
                    w[1] = 'T'.join(w[1:3])
                    w.pop(2)
                for i, key in enumerate(config.release_format):
                    V[key].append(config.release_dtype[key](w[i]))

        for key in config.release_format:
            V[key] = np.array(V[key])

        # --- Fill in if continuous release ---

        if config.release_type == 'continuous':
            time0 = V['release_time'][0]
            cont_times = np.arange(
                time0, config.stop_time, config.release_frequency)

            B = dict()     # Block to repeat
            W = dict()
            for key in config.release_format:
                W[key] = []
                if key != 'release_time':
                    B[key] = []
            count = 0  # Number of times to repeat
            utimes = np.unique(V['release_time'])
            for t in cont_times:
                if t in utimes:
                    I = (V['release_time'] == t)
                    count = np.sum(I)
                    for key in config.release_format:
                        if key != 'release_time':
                            B[key] = list(V[key][I])
                W['release_time'].extend(count*[t])

                for key in config.release_format:
                    if key != 'release_time':
                        W[key].extend(B[key])

            for key in config.release_format:
                W[key] = np.array(W[key])
            V = W

        self.release_data = V
        self.times = V['release_time']

        # Error hvis ingen partikkelutslipp
        # Time control
        print(self.times[0], self.times[-1])
        if self.times[0] < config.start_time:
            logger.warning('Ignoring particle release before start')
        if self.times[-1] >= config.stop_time:
            logger.warning('Ignoring particle release after stop')
        valid = ((self.times >= config.start_time) &
                 (self.times < config.stop_time))
        self.times = self.times[valid]
        print(len(self.times))
        # self.unique_times = np.unique(self.times)
        self.unique_times = np.unique(self.times)

        if self.times[0] > config.start_time:
            logger.warning('No particles at start time')

        logger.info('First particle release at {}'.
                    format(str(self.times[0])))
        logger.info('Last particle release at  {}'.
                    format(self.times[-1]))
        logger.info('Number of particle releases = {}'.
                    format(len(self.unique_times)))

        print(self.unique_times.dtype)
        print(type(config.start_time))
        rel_time = self.times - config.start_time
        rel_time = rel_time.astype('m8[s]').astype('int')  # Convert to seconds
        self.steps = rel_time // config.dt
        rel_time = self.unique_times - config.start_time
        rel_time = rel_time.astype('m8[s]').astype('int')  # Convert to seconds
        self.unique_steps = rel_time // config.dt

        config.total_particle_count = self.release_data['mult'].sum()
        logger.info('Total number of particles in simulation: {}'.
                    format(config.total_particle_count))

        self._npids = 0    # Number of particles released
        self._release_index = 0

        # Save all particle variables
        self.particle_variables = dict()
        for name in config.particle_variables:
            self.particle_variables[name] = []

    # ---------------------
    # --- Update method ---
    # ---------------------

    def __next__(self):
        timestep = self.steps[self._release_index]
        logger.info('release: timestep, time = {}, {}'.
                    format(timestep, self.times[self._release_index]))
        # print(type(timestep))
        self._release_index += 1

        I = (self.steps == timestep)

        # State variables
        V = dict()

        release_keys = set(self.release_data.keys()) - {'mult'}

        mult = self.release_data['mult'][I]
        count = np.sum(mult)
        for key in release_keys:
            V[key] = duplicate(self.release_data[key][I], mult)
        V['pid'] = list(range(self._npids, self._npids+count))

        self._npids += count

        return V

# ------------------
# Utility functions
# -----------------


# Can np.repeat be used instead ??
def duplicate(A, M):
    """Repeat each element in sequence a variable number of times

    Example:
    [a0, a1, ...], [2, 3, ...] -> [a0, a0, a1, a1, a1 ...]

    """
    # Should check for same shape
    S = []
    for a, m in zip(np.asarray(A), np.asarray(M)):
        S.extend(m*[a])
    return S

# --------------------------------

if __name__ == "__main__":

    # Improvements, fjern fil - bruk inline string

    # from datetime import datetime

    # Make a minimal config object
    class Container(object):
        pass
    config = Container()
    config.start_time = np.datetime64('2015-03-31 12')
    # config.reference_time = config.start_time
    config.stop_time = np.datetime64('2015-04-04')
    config.dt = 3600
    config.particle_release_file = '../models/lakselus/release.in'
    config.release_format = ['mult', 'release_time',
                             'X', 'Y', 'Z',
                             'farmid', 'super']
    config.release_dtype = dict(mult=int, release_time=np.datetime64,
                                X=float, Y=float, Z=float,
                                farmid=int, super=float)
    config.particle_variables = ['release_time', 'farmid']

    release = ParticleReleaser(config)
    # release = p.release()

    for step in range(10):
        print('step = ', step)
        if step in release.steps:
            V = next(release)
            print(V)
