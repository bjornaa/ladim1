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

import logging
# import numpy as np
import pandas as pd

# ------------------------


class ParticleReleaser:
    """Particle Release Class"""

    def __init__(self, config):

        logging.info('Initalizing the particle releaser')

        release_variables = config.release_format
        conv = config.release_dtype

        A = pd.read_csv(config.particle_release_file, names=release_variables,
                        delim_whitespace=True, converters=conv)

        release_type = config.release_type
        times0 = A['release_time']
        if release_type == 'continuous':
            self.times = pd.date_range(start=times0[0], end=config.stop_time,
                                       freq=config.release_frequency)

        # print(times)

        self.A = A

        times = A['release_time']
        unique_times = times.unique()
        self.release_times = unique_times

        # total_particles = A.mult.sum()
        # Feil med kontinuerlig
        print("total_particles = ", total_particles)


# For next
# if t0 <= t (t0 max slik)
# Ta verdiene fra t0
# Bruk mult til å multiplisere (repeat)

    def release(self, dtime):

        n = self.time.index   # index in file-times
        if dtime < self.file_time[n]:
            pass   # Should not happen
        if dtime > self.file_time[n+1]:
            n += 1
        # Bruk list(A.groupby('release_time'))[n]
        # Få V['X'] med multiplisitet
