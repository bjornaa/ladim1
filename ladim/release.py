# Particle release class

# -------------------
# release.py
# part of LADiM
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

from netCDF4 import Dataset

from .utilities import ingrid
from .configuration import Config
# from .gridforce import Grid


def mylen(df: pd.DataFrame) -> int:
    """Number of rows in a DataFrame,

    A workaround for len() which does not
    have the expected behaviour with itemizing,
    """
    if df.ndim == 1:
        return 1
    else:
        return df.shape[0]


class ParticleReleaser(Iterator):
    """Particle Release Class"""

    def __init__(self, config: Config, grid) -> None:

        start_time = pd.to_datetime(config['start_time'])
        stop_time = pd.to_datetime(config['stop_time'])

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

        # Conversion from longitude, latitude to grid coordinates
        if 'X'  not in A.columns or 'Y' not in A.columns:
            if 'lon' not in A.columns or 'lat' not in A.columns:
                logging.error("Particle release mush have position")
                raise SystemExit
            else:
                X, Y = grid.ll2xy(A['lon'], A['lat'])
                A['lon'] = X
                A['lat'] = Y
                A.rename(columns={'lon': 'X', 'lat': 'Y'}, inplace=True)

        # Remove everything after simulation stop time
        # A = A[A['release_time'] <= stop_time]   # Use < ?
        A = A[A.index <= stop_time]   # Use < ?
        if len(A) == 0:  # All release after simulation time
            logging.error("All particles released after similation stop")
            raise SystemExit

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

        # file_times = A['release_time'].unique()

        # TODO: Make a function of continuous -> discrete
        # Fill out if continuous release
        if config['release_type'] == 'continuous':

            # Find first effective release time
            # i.e. the last time <= start_time
            #   and remove too early releases
            # Can be moved out of if-block?
            n = np.sum(A.index <= start_time)
            if n == 0:
                logging.warning("No particles released at simulation start")
                n = 1
            # First effective release:
            # release_time0 = A.iloc[n-1].release_time

            # TODO: Check pandas, better way to delete rows?
            times = A['release_time']
            try:
                release_time0 = times[times <= pd.to_datetime(start_time)][-1]
            except IndexError:
                release_time0 = times[0]
            A = A[A.index >= release_time0]

            # time0 = file_times[0]
            # time1 = max(file_times[-1], stop_time)
            time0 = A.index[0]
            time1 = max(A.index[-1], pd.Timestamp(stop_time))
            # time1 = max(A['release_time'][-1], stop_time)
            times = np.arange(time0, time1, config['release_frequency'])
            # A = A.reindex(times, method='pad')
            # A['release_time'] = A.index
            # Reindex does not work with non-unique index
            I = A.index.unique()
            J = pd.Series(I, index=I).reindex(times, method='pad')
            M = {i: mylen(A.loc[i]) for i in I}
            A = A.loc[J]
            # Correct time index
            S: List[int] = []
            for t in times:
                S.extend(M[J[t]]*[t])
            A['release_time'] = S
            A.index = S

            # Remove any new instances before start time
            # n = np.sum(A['release_time'] <= start_time)
            # if n == 0:
            #     n = 1
            # A = A.iloc[n-1:]

            # If first release is early set it to start time
            # A['release_time'] = np.maximum(A['release_time'], # tart_time)

        # If discrete, there is an error to have only early releases
        # OK if warm start
        else:   # Discrete
            if A.index[-1] < start_time and config['start'] == 'cold':
                logging.error("All particles released before similation start")
                raise SystemExit

        # We are now discrete,
        # remove everything before start time
        A = A[A.index >= start_time]

        # If warm start, no new release at start time (already accounted for)
        if config['start'] == 'warm':
            A = A[A.index > start_time]

        # Release times
        self.times = A['release_time'].unique()

        logging.info("Number of release times = {}".format(len(self.times)))

        # Compute the release time steps
        rel_time = self.times - config['start_time']
        rel_time = rel_time.astype('m8[s]').astype('int')
        self.steps = rel_time // config['dt']

        # Make dataframes for each timeframe
        # self._B = [x[1] for x in A.groupby('release_time')]
        self._B = [x[1] for x in A.groupby(A.index)]

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

        # Get particle data from  warm start
        if config['start'] == 'warm':
            with Dataset(config['warm_start_file']) as f:
                # warm_particle_count = len(f.dimensions['particle'])
                warm_particle_count = np.max(f.variables['pid'][:]) + 1
                for name in config['particle_variables']:
                    pvars[name] = f.variables[name][:warm_particle_count]
        else:
            warm_particle_count = 0

        # initital number of particles
        if config['start'] == 'warm':
            particles_released = [warm_particle_count]
        else:
            particles_released = [0]

        # Loop through the releases, collect particle variable data
        for t in self.times:
            V = next(self)
            particles_released.append(particles_released[-1] + len(V))
            for name in config['particle_variables']:
                dtype = config['release_dtype'][name]
                if dtype == np.datetime64:
                    g = np.array(V[name]).astype('M8[s]')
                    rtimes = g - config['reference_time']
                    rtimes = rtimes.astype(np.float64)
                    pvars[name] = np.concatenate((pvars[name], rtimes))
                else:
                    pvars[name] = np.concatenate((pvars[name], V[name]))

        self.total_particle_count = warm_particle_count + self._particle_count
        self.particle_variables = pvars
        logging.info("Total particle count = {}".format(
            self.total_particle_count))
        self.particles_released = particles_released

        # Export total particle count
        # Ugly to write back to config
        # Easier way to give this piece of information to the
        #     output initialization?
        config['total_particle_count'] = self.total_particle_count

        # Reset the counter after the particle counting
        self._index = 0    # Index of next release
        self._particle_count = warm_particle_count

    def __next__(self) -> pd.DataFrame:
        """Perform the next particle release

           Return a DataFrame with the release info,
           repeating mult times

        """

        # This should not happen
        if self._index >= len(self.times):
            raise StopIteration

        # Skip first release if warm start (should be present in start file)
        # Not always, make better test
        # Moving test to state.py
        # if self._index == 0 and self._particle_count > 0:  # Warm start
        #    return

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
