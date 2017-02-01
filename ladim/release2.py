# Particle release class

# Fjern avhengighet av pandas
# Få kontinuerlig kilde -
# konstant med frekvens til ny info.
# Sjekk om dette er lett i pandas => kan spare litt koding



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
import pandas as pd

# ------------------------

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ParticleReleaser:
    """Particle Release Class"""

    def __init__(self, config, loglevel=logging.INFO):

        # print("loglevel = ", loglevel)
        # raise SystemExit
        logger.setLevel(loglevel)
        # logger.setLevel(logging.INFO)

        # Store the data in a pandas dataframe
        #self._df = pd.read_csv(
        #    config.particle_release_file,
        #    names=config.release_format,
        #    dtype=config.release_dtype,
        #    parse_dates=['release_time'],
        #    delim_whitespace=True)

        # Time control
        if self._df.release_time[0] < config.start_time:
            logger.warning('Ignoring particles release before start')
            self._df = self._df[self._df.release_time >= config.start_time]
        if self._df.release_time.iloc[-1] >= config.stop_time:
            logger.warning('Ignoring particles release after stop')
            self._df = self._df[self._df.release_time < config.stop_time]
        # May be modified with restart
        if self._df.release_time[0] > config.start_time:
            logger.warning('No particles at start time')

        logger.info('First particle release at {}'.
                    format(str(self._df.release_time[0])))
        logger.info('Last particle release at  {}'.
                    format(self._df.release_time.iloc[-1]))
        logger.info('Number of particle releases = {}'.format(len(self._df)))

        # Relative time
        rel_time = self._df['release_time'] - config.start_time
        # Convert to seconds
        rel_time = rel_time.astype('m8[s]').astype('int')
        # Get model time steps and remove duplicates
        self._release_steps = rel_time // config.dt
        self.release_steps = list(self._release_steps.drop_duplicates())
        self.release_times = list(self._df['release_time'].drop_duplicates())

        # The total number of particles released during the simulation
        # config['total_particle_count'] = self._df['mult'].sum()
        config.total_particle_count = self._df['mult'].sum()
        logger.info('Total number of particles in simulation: {}'.
                    format(config.total_particle_count))

        self._npids = 0    # Number of particles released
        self._release_index = 0

        # Save all particle variables
        self.particle_variables = dict()
        # print(config.particle_variables)
        for name in config.particle_variables:
            self.particle_variables[name] = []
        for row in self._df.itertuples():
            # print(type(row), row)
            mult = row.mult
            for key, value in self.particle_variables.items():
                if key == 'release_time':
                    rtime = getattr(row, key)
                    rtime = rtime - config.reference_time
                    rtime = np.timedelta64(rtime, 's').astype('int')
                    value.extend(mult*[rtime])
                else:
                    value.extend(mult*[getattr(row, key)])

    def __iter__(self):
        return self

    def __next__(self):
        timestep = self.release_steps[self._release_index]
        logger.info('release: timestep, time = {}, {}'.
                    format(timestep, self.release_times[self._release_index]))
        # print(type(timestep))
        self._release_index += 1

        # All entries at the correct time step
        A = self._df[self._release_steps == timestep]

        # State variables
        V = dict()
        V['pid'] = []
        # Skip mult (always first)
        release_keys = list(self._df.columns[1:])
        for key in release_keys:
            V[key] = []
        for i, entry in A.iterrows():
            mult = entry.mult
            V['pid'].extend(list(range(self._npids, self._npids+mult)))
            self._npids += mult
            for key in release_keys:
                V[key].extend(mult*[entry[key]])
        return V


# --------------------------------

if __name__ == "__main__":

    # Improvements, fjern fil - bruk inline string

    from datetime import datetime

    # Make a minimal config object
    class Container(object):
        pass
    config = Container()
    config.start_time = datetime(1989, 6, 1, 12)
    config.reference_time = datetime(1989, 6, 1, 12)
    config.stop_time = datetime(1989, 6, 6, 0)
    config.dt = 3600
    config.particle_release_file = '../models/lakselus/release.in'
    config.release_format = ['mult', 'release_time',
                             'X', 'Y', 'Z',
                             'farmid', 'super']
    config.release_dtype = dict(mult=int, release_time=str,
                                X=float, Y=float, Z=float,
                                farmid=int, super=float)
    config.particle_variables = ['release_time', 'farmid']

    release = ParticleReleaser(config)
    # release = p.release()

    for step in range(10):
        print('step = ', step)
        if step in release.release_steps:
            V = next(release)
            print(V)

    print()
    print(release.particle_variables)
