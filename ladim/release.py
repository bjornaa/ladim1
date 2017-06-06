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
from typing import Iterator, List
from .utilities import ingrid
from .configuration import Config


class ParticleReleaser(Iterator):
    """Particle Release Class"""

    def __init__(self, config: Config) -> None:

        start_time = config['start_time']
        stop_time = config['stop_time']

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

        # Remove everything after simulation stop time
        A = A[A['release_time'] <= stop_time]   # Use < ?
        if len(A) == 0:  # All release after simulation time
            logging.error("All particles released after similation stop")
            raise SystemExit

        # Find first effective release
        # Remove too early releases
        n = np.sum(A['release_time'] <= start_time)
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

        file_times = A['release_time'].unique()

        # Fill out if continuous release
        if config['release_type'] == 'continuous':
            time0 = file_times[0]
            time1 = max(file_times[1], stop_time)
            times = np.arange(time0, time1, config['release_frequency'])
            # A = A.reindex(times, method='pad')
            # A['release_time'] = A.index
            # Reindex does not work with non-unique index
            print(A)
            I = A.index.unique()
            J = pd.Series(I, index=I).reindex(times, method='pad')
            # Number of releases with given time
            i = I[0]
            print('---', i, len(A.loc[i]))
            # print(A.loc[i])
            print('XXX', A.loc[i].shape)
            i = I[1]
            print('---', i, len(A.loc[i]))
            # print(A.loc[i])
            print('XXX', A.loc[i].shape)

            # Får antall kolonner her = 3, få bedre grep på lengden
            M = {i: len(A.loc[i]) for i in I}
            print(M)
            1/0
            A = A.loc[J]
            print(A)
            # Correct time index
            print("I =", I)
            print("J = ", J)
            print("M = ", M)
            S: List[int] = []
            for t in times:
                print(t, J[t], M[J[t]], t)
                print('len(S) =', len(S))
                S.extend(M[J[t]]*[t])
            A.index = S

            # Remove any new instances before start time
            n = np.sum(A['release_time'] <= start_time)
            if n == 0:
                n = 1
            A = A.iloc[n-1:]

        # If first release is early set it to start time
        A['release_time'] = np.maximum(A['release_time'], start_time)

        # Release times
        self.times = A['release_time'].unique()

        logging.info("Number of release times = {}".format(len(self.times)))

        # Compute the release time steps
        rel_time = self.times - config['start_time']
        rel_time = rel_time.astype('m8[s]').astype('int')
        self.steps = rel_time // config['dt']

        # Make dataframes for each timeframe
        self._B = [x[1] for x in A.groupby('release_time')]

        # Read the particle variables
        self._index = 0            # Index of next release
        self._particle_count = 0   # Particle counter

        # Handle the particle variables initially
        # TODO: Need a test to check that this iw working properly
        pvars = dict()
        for name in config['particle_variables']:
            dtype = config['release_dtype'][name]
            if dtype == np.datetime64:
                dtype = np.float64
            pvars[name] = np.array([], dtype=dtype)

        # Loop through the releases, collect particle variable data
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

        # Export total particle count
        # Ugly to write back to config
        # Easier way to give this piece of information to the
        #     output initialization?
        config['total_particle_count'] = self.total_particle_count

        # Reset the counter after the particle counting
        self._index = 0    # Index of next release
        self._particle_count = 0

    def __next__(self) -> pd.DataFrame:
        """Perform the next particle release

           Return a DataFrame with the release info,
           repeating mult times

        """

        # This should not happen
        if self._index >= len(self.times):
            raise StopIteration

        # rel_time = self.times[self._index]
        # file_time = self._file_times[self._file_index]

        V = self._B[self._index]
        nnew = V.mult.sum()
        # Workaround, missing repeat method for pandas DataFrame
        V0 = V.to_records(index=False)
        V0 = V0.repeat(V.mult)
        V = pd.DataFrame(V0)
        # Do not need the mult column any more
        V.drop('mult', axis=1, inplace=True)
        # Buffer the new values
        # self.V = V
        # self._file_index += 1

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
