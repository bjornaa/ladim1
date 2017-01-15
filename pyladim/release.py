# -*- coding: utf-8 -*-

# Particle release class


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

# import numpy as np
import pandas as pd

# ------------------------

# Skal ha public:
# release_steps, slik at en kan sjekke om release_step
# i så fall kalle generator prel.release()
# som returnerer dictionary med release_variablene
# evt, legger de selv til i state


class ParticleReleaser(object):

    def __init__(self, config):

        # Store the data in a pandas dataframe
        self._df = pd.read_csv(
            config.particle_release_file,
            names=config.release_format,
            dtype=config.release_dtype,
            parse_dates=['release_time'],
            delim_whitespace=True)

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

        self._npids = 0    # Number of particles released
        self._release_index = 0

        self.particle_variables = dict()
        print(config.particle_variables)
        for name in config.particle_variables:
            self.particle_variables[name] = []

    def __iter__(self):
        return self

    def __next__(self):
        timestep = self.release_steps[self._release_index]
        print('release: timestep, time = ', timestep,
              self.release_times[self._release_index])
        print(type(timestep))
        self._release_index += 1

        # All entries at the correct time step
        A = self._df[self._release_steps == timestep]

        # Particle variables
        # for name in self.particle_variables:
        #    self.particle_variables[name] = A[name]

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
    config.dt = 3600
    config.particle_release_file = '../input/lice.in'
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
