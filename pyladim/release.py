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

        # Pandas dataframe
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

        # self.release_steps = release_steps.drop_duplicates()
        # self.release_steps = release_steps.drop_duplicates()

        # Flyttes til state ???
        self._npids = 0    # Number of particles released

    def release(self):

        # Forutsetter at begynner med null
        for n, timestep in enumerate(self.release_steps):
            print('tstep = ', timestep)

            # All entries at the correct time step
            A = self._df[self._release_steps == timestep]

            V = dict()
            V['pid'] = []
            # Skip mult and release_time (always two first)
            release_keys = list(self._df.columns[2:])
            for key in release_keys:
                V[key] = []
            for i, entry in A.iterrows():
                mult = entry.mult
                V['pid'].extend(
                    list(range(self._npids, self._npids+mult)))
                self._npids += mult
                for key in release_keys:
                    V[key].extend(mult*[entry[key]])

            yield V

# --------------------------------

if __name__ == "__main__":

    from ladim_config import read_config
    config = read_config('../ladim.yaml')

    config.particle_release_file = '../input/lice.in'

    # Bedre: ParticleReleaser blir en generator
    p = ParticleReleaser(config)

    release = p.release()

    # Får bare en release (og det er den første)
    V0 = next(release)
    V1 = next(release)
