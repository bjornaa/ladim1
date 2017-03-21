import os
import numpy as np
import pytest
from ladim.release import ParticleReleaser

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
    config.particle_release_file = 'release.rls'
    config.release_format = ['mult', 'release_time', 'X']
    config.release_dtype = dict(mult=int, release_time=np.datetime64,
                                X=float)
    config.release_type = 'discrete'
    config.particle_variables = []

    # Make a release file
    A = ['2 2015-04-01 100',
         '1 2015-04-01T00 111',
         '3 "2015-04-03 12" 200']
    with open('release.rls', mode='w') as f:
        for a in A:
            f.write(a + '\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    os.remove('release.rls')

    assert(len(release.times) == 2)
    assert(release.total_particle_count == 6)

    # First release
    S = next(release)
    assert(np.all(S['pid'] == [0, 1, 2]))
    assert(S['release_time'][0] == np.datetime64('2015-04-01'))
    assert(np.all(S['X'] == [100, 100, 111]))

    # Second release
    S = next(release)
    assert(np.all(S['pid'] == [3, 4, 5]))
    assert(S['release_time'][0] == np.datetime64('2015-04-03T12:00:00'))
    assert(np.all(S['X'] == [200, 200, 200]))

    # No more releases
    with pytest.raises(StopIteration):
        S = next(release)


def test_continuous():

    # Make a minimal config object
    config = Container()
    config.start_time = np.datetime64('2015-03-31 12')
    # config.reference_time = config.start_time
    config.stop_time = np.datetime64('2015-04-02 12')
    config.dt = 3600
    config.particle_release_file = 'release.rls'
    config.release_format = ['mult', 'release_time', 'X']
    config.release_dtype = dict(mult=int, release_time=np.datetime64,
                                X=float)
    config.release_type = 'continuous'
    config.release_frequency = np.timedelta64(6, 'h')
    config.particle_variables = []

    # Make a release file
    A = ['2 2015-04-01 100',
         '1 2015-04-01T00 111',
         '3 "2015-04-01 12" 200']
    with open('release.rls', mode='w') as f:
        for a in A:
            f.write(a + '\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    # Clean out the release file
    os.remove('release.rls')

    # Check some overall sizes
    assert(len(release.times) == 6)
    assert(config.total_particle_count == 18)

    # --- Check the releases
    # Entries 1-2
    for t in range(2):
        S = next(release)
        assert(np.all(S['pid'] == [3*t, 1+3*t, 2+3*t]))
        assert(S['release_time'][0] ==
               np.datetime64('2015-04-01T00') + t*config.release_frequency)
        assert(np.all(S['X'] == [100, 100, 111]))

    # Entries 3-6
    t = 2
    for S in release:
        assert(np.all(S['pid'] == [3*t, 1+3*t, 2+3*t]))
        assert(S['release_time'][0] ==
               np.datetime64('2015-04-01') + t*config.release_frequency)
        assert(np.all(S['X'] == [200, 200, 200]))
        t += 1
