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
import numpy as np
import pandas as pd

# ------------------------


class ParticleReleaser:
    """Particle Release Class"""

    def __init__(self):

        logging.info('Initalizing the particle releaser')

        release_file = 'test.rst'
        # dtype = dict(mult=int, X=float)
        # conv = dict(mult=int, release_time=pd.to_datetime, X=float)
        conv = dict(mult=int, release_time=np.datetime64, X=float)
        release_variables = ['mult', 'release_time', 'X']
        release_type = "continuous"
        release_frequency = '3600S'
        stop_time = np.datetime64('2015-04-03T15')

        A = pd.read_csv(release_file, names=release_variables,
                        delim_whitespace=True, converters=conv)

        # if not mult, set default value = 1

        times0 = A['release_time']
        if release_type == 'continuous':
            self.times = pd.date_range(start=times0[0], end=stop_time,
                                       freq=release_frequency)

        # print(times)

        self.A = A

        times = A['release_time']
        unique_times = times.unique()
        self.release_times = unique_times

        total_particles = A.mult.sum()
        # Feil med kontinuerlig
        print("total_particles = ", total_particles)


# For next
# if t0 <= t (t0 max slik)
# Ta verdiene fra t0
# Bruk mult til å multiplisere (repeat)

    def release(self, dtime):

        n = self.time.index   # index in file-times
        if dtime < file_time[n]:
            pass   # Should not happen
        if dtime > file_time[n+1]:
            n += 1
        # Bruk list(A.groupby('release_time'))[n]
        # Få V['X'] med multiplisitet









if __name__ == '__main__':

    P = ParticleReleaser()
    A = P.A
    times = P.times
    B = A.groupby('release_time')
    list(B)
