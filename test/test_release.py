import os
import numpy as np
import pytest
from ladim.release import ParticleReleaser


def test_discrete() -> None:

    # Make a minimal config object
    config = {
        'start_time': np.datetime64('2015-03-31 12'),
        'stop_time': np.datetime64('2015-04-04'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'discrete',
        'particle_variables': [],
        }

    # Make a release file
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-01 100\n')
        f.write('1 2015-04-01T00 111\n')
        f.write('3 "2015-04-03 12" 200\n')
    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    os.remove('release.rls')

    print("times = ", release.times)
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
        next(release)


def test_continuous() -> None:

    config = {
        'start_time': np.datetime64('2015-03-31 12'),
        'stop_time': np.datetime64('2015-04-04'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'continuous',
        'release_frequency': np.timedelta64(12, 'h'),
        'particle_variables': [],
        }

    # Make a release file
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-01 100\n')
        f.write('1 2015-04-01T00 111\n')
        f.write('3 "2015-04-02" 200\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    # Clean out the release file
    os.remove('release.rls')

    # Check some overall sizes
    assert(len(release.times) == 6)
    assert(config['total_particle_count'] == 18)

    # --- Check the releases
    for t, S in enumerate(release):
        assert(np.all(S['pid'] == [3*t, 1+3*t, 2+3*t]))
        assert(S['release_time'][0] ==
               np.datetime64('2015-04-01') + t*config['release_frequency'])
        if t < 2:
            assert(np.all(S['X'] == [100, 100, 111]))
        else:
            assert(np.all(S['X'] == [200, 200, 200]))


# This does not work as expected
def test_late_start() -> None:
    """Model start after first release in file"""

    config = {
        'start_time': np.datetime64('2015-04-03 09'),
        'stop_time': np.datetime64('2015-04-05 13'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'continuous',
        'release_frequency': np.timedelta64(12, 'h'),
        'particle_variables': [],
        }

    # Release file: create, read and remove
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-02 100\n')
        f.write('1 2015-04-03T18 150\n')
        f.write('3 2015-04-05 200\n')
    release = ParticleReleaser(config)
    os.remove('release.rls')

    # Correct release times
    release_times = ['2015-04-03 09', '2015-04-03 12', '2015-04-04',
                     '2015-04-04 12', '2015-04-05', '2015-04-05 12']
    release_times = np.array(release_times, dtype=np.datetime64)

    assert(len(release.times) == len(release_times))
    assert(np.all(release.times == release_times))

    # Total particle count: 2+2+1+1+1+3+3 = 12
    assert(config['total_particle_count'] == 12)

    # The entries have the correct information
    for t, S in enumerate(release):
        assert(np.all(S['release_time'][0] == release_times[t]))
        if t < 2:
            assert(np.all(S['pid'] == [2*t, 2*t+1]))
            assert(np.all(S['X'] == 100))
        if 2 <= t < 4:
            assert(np.all(S['pid'] == [2+t]))
            assert(np.all(S['X'] == 150))
        if 4 <= t:
            assert(np.all(S['pid'] == 3*(t-2) + np.array([0, 1, 2])))
            assert(np.all(S['X'] == 200))


def rest_too_late_start() -> None:
    """Model start after last release in file"""

    config = {
        'start_time': np.datetime64('2015-05-02 12'),
        'stop_time': np.datetime64('2015-05-03 12'),
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        }

    # Make a release file
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-01 100\n')

    # Release should quit with SystemExit
    with pytest.raises(SystemExit):
        ParticleReleaser(config)

    # Clean up
    os.remove('release.rls')


def rest_early_stop() -> None:
    """Model stop before last release in release file"""

    config = {
        'start_time': np.datetime64('2015-04-02'),
        'stop_time': np.datetime64('2015-04-05'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'continuous',
        'release_frequency': np.timedelta64(12, 'h'),
        'particle_variables': [],
        }

    # Release file: create, read and remove
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-01 100\n')
        f.write('3 2015-04-03 200\n')
        f.write('1 2015-04-08 300\n')
    release = ParticleReleaser(config)
    os.remove('release.rls')

    # Correct release times
    # First release neglected since before start
    release_times = ['2015-04-03', '2015-04-03 12',
                     '2015-04-04', '2015-04-04 12']
    release_times = np.array(release_times, dtype=np.datetime64)

    assert(len(release.times) == len(release_times))
    assert(np.all(release.times == release_times))

    # The entries have the correct information
    for t, S in enumerate(release):
        assert(np.all(S['pid'] == [3*t, 3*t+1, 3*t+2]))
        assert(np.all(S['release_time'] == release_times[t]))
        assert(np.all(S['X'] == 200.0))


def rest_too_early_stop() -> None:
    """Model stop before first release in release file"""

    config = {
        'start_time': np.datetime64('2015-03-02'),
        'stop_time': np.datetime64('2015-03-05'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'continuous',
        'release_frequency': np.timedelta64(12, 'h'),
        'particle_variables': [],
        }

    # Release file: create, read and remove
    with open('release.rls', mode='w') as f:
        f.write('2 2015-04-01 100\n')
        f.write('3 2015-04-03 200\n')

    # Should exit
    with pytest.raises(SystemExit):
        ParticleReleaser(config)

    # Clean up
    os.remove('release.rls')


def rest_subgrid() -> None:
    """Particle release outside subgrid should be ignored"""

    config = {
        'start_time': np.datetime64('2015-03-01'),
        'stop_time': np.datetime64('2015-03-03'),
        'dt': 3600,
        'particle_release_file': 'release.rls',
        'release_format': ['mult', 'release_time', 'X', 'Y'],
        'release_dtype': dict(mult=int, release_time=np.datetime64, X=float),
        'release_type': 'continuous',
        'release_frequency': np.timedelta64(12, 'h'),
        'particle_variables': [],
        'grid_args': dict(subgrid=[100, 120, 10, 20])
        }

    # Release file: create, read and remove
    with open('release.rls', mode='w') as f:
        f.write('2 2015-03-01 110 15\n')   # Inside
        f.write('3 2015-03-01 200 30\n')   # Outside

    # Make the ParticleReleaser object
    release = ParticleReleaser(config)
    # Clean out the release file
    os.remove('release.rls')

    # Check some overall sizes
    assert(len(release.times) == 4)
    assert(config['total_particle_count'] == 2*4)

    for t, S in enumerate(release):
        assert(np.all(S['pid'] == [2*t, 2*t+1]))
        assert(np.all(S['X'] == [110, 110]))
        assert(np.all(S['Y'] == [15, 15]))


if __name__ == '__main__':
    # test_discrete()
    test_continuous()
    # test_late_start()
