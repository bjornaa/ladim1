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

    def __init__(self, config):

        logging.info('Initializing the particle releaser')

        # Read the particle release file
        A = pd.read_table(config.particle_release_file,
                          names=config.release_format,
                          converters=config.release_dtype,
                          delim_whitespace=True)

        # If no mult column, add a column of ones
        if 'mult' not in config.release_format:
            A['mult'] = 1

        # self.A = A

        # The timeframes present in the release file
        self._file_times = A['release_time'].unique()

        # Handle continuous release
        if config.release_type == 'continuous':
            time0 = A['release_time'][0]
            self.times = np.arange(
                time0, config.stop_time, config.release_frequency)
            # Append stop_time to allow releases after last file time
            if config.stop_time > self._file_times[-1]:
                self._file_times = np.concatenate(
                    (self._file_times, [config.stop_time]))
        else:
            self.times = A['release_time'].unique()

        logging.info("Number of release times = {}".format(len(self.times)))

        # Make dataframes for each timeframe
        self._B = [x[1] for x in A.groupby('release_time')]

        # Read the particle variables
        self._index = 0            # Index of next release
        self._file_index = 0       # Index of next data from release file
        self._particle_count = 0   # Particle counter
        pvars = dict()
        for name in config.particle_variables:
            dtype = config.release_dtype[name]
            if dtype == np.datetime64:
                dtype = np.float64
            pvars[name] = np.array([], dtype=dtype)

        for t in self.times:
            V = next(self)
            for name in config.particle_variables:
                dtype = config.release_dtype[name]
                if dtype == np.datetime64:
                    rtimes = V[name] - config.reference_time
                    rtimes = rtimes.astype('timedelta64[s]').astype(np.float64)
                    pvars[name] = np.concatenate((pvars[name], rtimes))
                else:
                    pvars[name] = np.concatenate((pvars[name], V[name]))

        self.total_particle_count = self._particle_count
        self.particle_variables = pvars
        logging.info("Total particle count = {}".format(
            self.total_particle_count))

        rel_time = self.times - config.start_time
        rel_time = rel_time.astype('m8[s]').astype('int')  # Convert to seconds
        self.steps = rel_time // config.dt

        # Export total particle count
        # config.total_particle_count = self.total_particle_count

        # Reset the counters after the particle count
        self._index = 0    # Index of next release
        self._file_index = 0      # Index of next data from release file
        self._particle_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        """Perform the next particle release"""

        # This should not happen
        if self._index >= len(self.times):
            raise StopIteration

        rel_time = self.times[self._index]
        file_time = self._file_times[self._file_index]

        if rel_time < file_time:
            # Use previous file release data
            V = self.V
            V.release_time = rel_time
        else:
            # rel_time >= file_time, get new release data
            V = self._B[self._file_index]
            nnew = V.mult.sum()
            # Workaround, missing repeat method for pandas DataFrame
            V0 = V.to_records(index=False)
            V0 = V0.repeat(V.mult)
            V = pd.DataFrame(V0)
            # Do not need the mult column any more
            V.drop('mult', axis=1, inplace=True)
            # Buffer the new values
            self.V = V
            self._file_index += 1

        # Add the new pids
        nnew = len(V)
        pids = pd.Series(range(self._particle_count,
                         self._particle_count + nnew),
                         name='pid')
        V = V.join(pids)

        # Update the counters
        self._index += 1
        self._particle_count += len(V)

        return V
