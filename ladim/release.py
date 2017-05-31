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
from typing import Iterator
from .utilities import ingrid
from .configuration import Config


class ParticleReleaser(Iterator):
    """Particle Release Class"""

    def __init__(self, config: Config) -> None:

        logging.info('Initializing the particle releaser')

        # Read the particle release file
        A = pd.read_table(config['particle_release_file'],
                          names=config['release_format'],
                          converters=config['release_dtype'],
                          delim_whitespace=True)

        # If no mult column, add a column of ones
        if 'mult' not in config['release_format']:
            A['mult'] = 1

        # Use release_time as index
        A.index = A['release_time']

        print(A)
        print('   --- ')

        # Remove everything after simulation stop time
        A = A[A['release_time'] <= config['stop_time']]   # Use < ?
        if len(A) == 0:  # All release after simulation time
            logging.error("All particles released after similation stop")
            raise SystemExit

        # Find first effective release
        # Clip out too early releases,
        n = np.sum(A['release_time'] <= config['start_time'])
        if n == 0:
            logging.warning("No particles released at simulation start")
            n = 1
        A = A.iloc[n-1:]

        # Optionally, remove everything outside a subgrid
        try:
            subgrid: List[int] = config['grid_args']['subgrid']
        except KeyError:
            subgrid = []
        if subgrid:
            lenA = len(A)
            A = A[ingrid(A['X'], A['Y'], subgrid)]
            if len(A) < lenA:
                logging.warning('Ignoring particle release outside subgrid')


        print(A)

        file_times = A['release_time'].unique()
        print('file_times = ', file_times)

        # Fill out if continuous release
        if config['release_type'] == 'continuous':
            time0 = file_times[0]
            time1 = max(file_times[1], config['stop_time'])
            times = np.arange(time0, time1, config['release_frequency'])
            print(times)
            A = A.reindex(times, method='pad')
            A['release_time'] = A.index

        # Remove new instances before start time
        n = np.sum(A['release_time'] <= config['start_time'])
        A = A.iloc[n-1:]
        A[A['release_time'] < config['start_time']] = config['start_time']
        print(A)

        # Release times
        self.times = A['release_time'].unique()

        logging.info("Number of release times = {}".format(len(self.times)))

        # Make dataframes for each timeframe
        self._B = [x[1] for x in A.groupby('release_time')]

        # Read the particle variables
        # self.release_index = 0
        # self._index = 0            # Index of next release
        # self._file_index = 0       # Index of next data from release file
        # self._particle_count = 0   # Particle counter

        # Read the particle variables
        pvars = dict()
        for name in config['particle_variables']:
            dtype = config['release_dtype'][name]
            if dtype == np.datetime64:
                dtype = np.float64
            pvars[name] = np.array([], dtype=dtype)
        print(pvars)

        for t in self.times:
            V = next(self)
            for name in config['particle_variables']:
                dtype = config['release_dtype'][name]
                if dtype == np.datetime64:
                    rtimes = V[name] - config['reference_time']
                    rtimes = rtimes.astype('timedelta64[s]').astype(np.float64)
                    pvars[name] = np.concatenate((pvars[name], rtimes))
                else:
                    pvars[name] = np.concatenate((pvars[name], V[name]))

        self.total_particle_count = self._particle_count
        self.particle_variables = pvars
        logging.info("Total particle count = {}".format(
            self.total_particle_count))

        rel_time = self.times - config['start_time']
        rel_time = rel_time.astype('m8[s]').astype('int')  # Convert to seconds
        self.steps = rel_time // config['dt']

        # Export total particle count
        config['total_particle_count'] = self.total_particle_count

        # Reset the counters after the particle count
        self._index = 0    # Index of next release
        # Find first index in release_file, skip  before start
        # for i, ft in self._file_times:
        #    if ft >= self.times[0]:
        #        self._file_index = i
        #        break

        self._file_index = 0      # Index of next data from release file
        self._particle_count = 0
        self.V = pd.DataFrame([])

    # def __iter__(self):
    #    return self

    def __next__(self) -> pd.DataFrame:
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
