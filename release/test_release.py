import os
import numpy as np
import pytest
import pandas as pd
from release_pandas import ParticleReleaser

# Testing the ParticleReleaser class
# Usage: py.test test_release.py

# TODO: Implement and test that we get error if no release in the
# time window
# TODO: Implement and test that input and description matches


class Container(object):
    """A simple class for emulating the Configuration"""
    pass


def test_discrete():

    # Make a minimal config object
    config = Container()
    config.start_time = np.datetime64('2015-03-31 12')
    # config.reference_time = config.start_time
    config.stop_time = np.datetime64('2015-04-04')
    config.dt = 3600
    config.particle_release_file = 'test.rls'
    config.release_format = ['mult', 'release_time', 'X']
    config.release_dtype = dict(mult=int, release_time=np.datetime64,
                                X=float)
    config.release_type = 'discrete'
    config.particle_variables = []

    # Make a release file
    A = ['2 2015-04-01 100',
         '1 2015-04-01T00 111',
         '3 "2015-04-03 12" 200']
    with open('test.rls', mode='w') as f:
        for a in A:
            f.write(a + '\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    # os.remove('test.rls')

    assert(len(release.release_times) == 2)
    assert(release.total_particle_count == 6)

    # First release
    S = next(release)
    assert(np.all(S['pid'] == pd.Series([0, 1, 2])))
    assert(S['release_time'][0] == np.datetime64('2015-04-01'))
    assert(np.all(S['X'] == pd.Series([100, 100, 111])))

    # Second release
    S = next(release)
    assert(np.all(S['pid'] == [3, 4, 5]))
    assert(S['release_time'][0] == np.datetime64('2015-04-03T12:00:00'))
    assert(np.all(S['X'] == [200, 200, 200]))

    # No more releases
    with pytest.raises(StopIteration):
        S = next(release)


def rest_continuous():

    # Make a minimal config object
    config = Container()
    config.start_time = np.datetime64('2015-03-31 12')
    # config.reference_time = config.start_time
    config.stop_time = np.datetime64('2015-04-02 12')
    config.dt = 3600
    config.particle_release_file = 'test.rst'
    config.release_format = ['mult', 'release_time', 'X']
    config.release_dtype = dict(mult=int, release_time=np.datetime64,
                                X=float)
    config.release_type = 'continuous'
    config.release_frequency = np.timedelta64(6, 'h')
    config.particle_variables = []

    # Make a release file
    A = ['2 2015-04-01 100',
         '1 2015-04-01 111',
         '3 2015-04-01 12 200']
    with open('test.rst', mode='w') as f:
        for a in A:
            f.write(a + '\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    # Clean out the release file
    os.remove('test.rst')

    # Check some overall sizes
    assert(len(release.times) == 8)
    assert(len(release.unique_times) == 6)
    assert(config.total_particle_count == 18)

    # --- Check the releases
    # First entry
    S = next(release)
    assert(np.all(S['pid'] == [0, 1, 2]))
    assert(S['release_time'][0] == np.datetime64('2015-04-01'))
    assert(S['X'] == [100, 100, 111])

    # Second entry
    S = next(release)
    assert(S['pid'] == [3, 4, 5])
    assert(S['release_time'][0] == np.datetime64('2015-04-01 06'))
    assert(S['X'] == [100, 100, 111])

    # Entries 3-6
    for t in range(4):
        S = next(release)
    assert(S['pid'] == [6+3*t, 7+3*t, 8+3*t])
    assert(S['release_time'][0] ==
           np.datetime64('2015-04-01T12:00:00') + t*config.release_frequency)
    assert(S['X'] == [200, 200, 200])

    # No more releases
    with pytest.raises(StopIteration):
        S = next(release)
