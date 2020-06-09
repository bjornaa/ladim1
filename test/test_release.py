import os
import numpy as np
import pandas as pd
import pytest
from ladim.release import ParticleReleaser


def releaser(conf, grid, text):
    fname = conf['particle_release_file']
    try:
        with open(fname, 'w', encoding='utf-8-sig') as file:
            file.write(text)
        pr = ParticleReleaser(conf, grid)
    finally:
        os.remove(fname)
    return pr


@pytest.fixture()
def minimal_config():
    return dict(
        start="cold",
        dt=3600,
        start_time=np.datetime64("2015-03-31 12"),
        stop_time=np.datetime64("2015-04-04"),
        particle_release_file="release.rls",
        release_format=["release_time", "X", "Y"],
        release_dtype=dict(release_time=np.datetime64, X=float, Y=float),
        release_type="discrete",
        particle_variables=[],
    )


@pytest.fixture()
def mult_config(minimal_config):
    c = minimal_config.copy()
    c['release_format'] = ["mult"] + c['release_format']
    c['release_dtype']['mult'] = int
    return c


class Test_Releaser:
    def test_attr_total_particle_count_correct_when_simple_config(self, minimal_config):
        release_text = (
            "2015-04-01T00 0 0\n"
            "2015-04-01T01 0 0\n"
            "2015-04-01T02 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)
        assert pr.total_particle_count == 3

    def test_attr_times_correct_when_simple_config(self, minimal_config):
        release_text = (
            "2015-04-01T00 0 0\n"
            "2015-04-01T01 0 0\n"
            "2015-04-01T02 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)

        assert pr.times.astype(str).tolist() == [
            '2015-04-01T00:00:00.000000000',
            '2015-04-01T01:00:00.000000000',
            '2015-04-01T02:00:00.000000000',
        ]

    def test_attr_steps_correct_when_simple_config(self, minimal_config):
        release_text = (
            "2015-04-01T00 0 0\n"
            "2015-04-01T01 0 0\n"
            "2015-04-01T02 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)

        assert pr.steps.tolist() == [12, 13, 14]

    def test_accepts_multiple_date_formats(self, minimal_config):
        release_text = (
            "2015-04-01T00 0 0\n"
            '"2015-04-01 01" 0 0\n'
            "2015-04-01 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)
        assert pr.total_particle_count == 3

    def test_correct_particle_count_when_mult(self, mult_config):
        release_text = (
            "1 2015-04-01T00 0 0\n"
            "4 2015-04-01T01 0 0\n"
            "2 2015-04-01T02 0 0\n"
        )
        pr = releaser(mult_config, grid=None, text=release_text)
        assert pr.total_particle_count == 7

    def test_is_iterator_of_dataframes(self, minimal_config):
        release_text = (
            "2015-04-01T00 0 0\n"
            "2015-04-01T01 0 0\n"
            "2015-04-01T02 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)
        pr_list = list(pr)
        assert len(pr_list) == 3
        assert isinstance(pr_list[0], pd.DataFrame)
        assert list(pr_list[0].columns) == ['release_time', 'X', 'Y', 'pid']
        assert list(pr_list[0].release_time) == [pd.Timestamp('2015-04-01 00')]

    def notest_returns_one_dataframe_per_timestep(self, minimal_config):
        release_text = (
            "2015-04-01T00:00 0 0\n"
            "2015-04-01T00:30 0 0\n"
            "2015-04-01T00:45 0 0\n"
            "2015-04-01T02:00 0 0\n"
        )
        pr = releaser(minimal_config, grid=None, text=release_text)
        list_pr = list(pr)

        assert pr.total_particle_count == 4
        assert len(list_pr) == 2


def test_discrete() -> None:

    # Make a minimal config object
    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-03-31 12"),
        "stop_time": np.datetime64("2015-04-04"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "discrete",
        "particle_variables": [],
    }

    # Make a release file
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 200\n")
        f.write("1 2015-04-01T00 111 220\n")
        f.write('3 "2015-04-03 12" 200 300\n')
    # Make the ParticleReleaser object
    release = ParticleReleaser(config, grid=None)
    # Clean up the release file
    os.remove("release.rls")

    assert len(release.times) == 2
    assert release.total_particle_count == 6

    # First release
    S = next(release)
    assert np.all(S["pid"] == [0, 1, 2])
    assert S["release_time"][0] == np.datetime64("2015-04-01")
    assert np.all(S["X"] == [100, 100, 111])
    assert np.all(S["Y"] == [200, 200, 220])

    # Second release
    S = next(release)
    assert np.all(S["pid"] == [3, 4, 5])
    assert S["release_time"][0] == np.datetime64("2015-04-03T12:00:00")
    assert np.all(S["X"] == [200, 200, 200])

    # No more releases
    with pytest.raises(StopIteration):
        next(release)


#
# ------------------------------------------------------
#
def test_continuous() -> None:

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-03-31 12"),
        "stop_time": np.datetime64("2015-04-04"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "continuous",
        "release_frequency": np.timedelta64(12, "h"),
        "particle_variables": [],
    }

    # Make a release file
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 200\n")
        f.write("1 2015-04-01T00 111 220\n")
        f.write('3 "2015-04-02" 200 300\n')

    # Make the ParticleReleaser object
    release = ParticleReleaser(config, grid=None)
    # Clean out the release file
    os.remove("release.rls")

    # Check some overall sizes
    assert len(release.times) == 6
    assert config["total_particle_count"] == 18

    # --- Check the releases
    for t, S in enumerate(release):
        assert np.all(S["pid"] == [3 * t, 1 + 3 * t, 2 + 3 * t])
        assert (
            S["release_time"][0]
            == np.datetime64("2015-04-01") + t * config["release_frequency"]
        )
        if t < 2:
            assert np.all(S["X"] == [100, 100, 111])
        else:
            assert np.all(S["X"] == [200, 200, 200])


#
# --------------------------------------------------
#
def test_late_start() -> None:
    """Model start after first release in file"""

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-04-03 00"),
        "stop_time": np.datetime64("2015-04-05 13"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "continuous",
        "release_frequency": np.timedelta64(12, "h"),
        "particle_variables": [],
    }

    # Release file: create, read and remove
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 200\n")
        f.write("1 2015-04-01 150 200\n")
        f.write("4 2015-04-02 200 200\n")
        f.write("3 2015-04-02 250 200\n")
        f.write("4 2015-04-03 300 200\n")
        f.write("1 2015-04-03 350 200\n")
        f.write("2 2015-04-04 400 200\n")
        f.write("1 2015-04-04 450 200\n")
        f.write("2 2015-04-05 500 200\n")
        f.write("2 2015-04-05 550 200\n")
        f.write("3 2015-04-06 600 200\n")
        f.write("2 2015-04-06 650 200.0\n")
    release = ParticleReleaser(config, grid=None)
    os.remove("release.rls")

    # Correct release times
    release_times = [
        "2015-04-03",
        "2015-04-03 12",
        "2015-04-04",
        "2015-04-04 12",
        "2015-04-05",
        "2015-04-05 12",
    ]
    release_times = np.array(release_times, dtype=np.datetime64)
    # Number of particles per release time
    counts = [5, 5, 3, 3, 4, 4]
    cumcount = [0] + list(np.cumsum(counts))

    print(release.times)
    # Check the release times
    assert len(release.times) == len(release_times)
    assert np.all(release.times == release_times)

    # Total particle count
    assert config["total_particle_count"] == sum(counts)

    for i, S in enumerate(release):
        assert np.all(S["pid"] == range(cumcount[i], cumcount[i + 1]))
        j = i // 2
        assert S["X"][0] == (j + 3) * 100
        assert S["X"].iloc[-1] == (j + 3) * 100 + 50


def test_too_late_start() -> None:
    """Model start after last release in file"""

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-05-02 12"),
        "stop_time": np.datetime64("2015-05-03 12"),
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "discrete",
        "dt": 3600,
        "particle_variables": [],
    }

    # Make a release file
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 200\n")

    # Release should quit with SystemExit
    with pytest.raises(SystemExit):
        ParticleReleaser(config, grid=None)

    # Clean up
    os.remove("release.rls")


def test_early_stop() -> None:
    """Model stop before last release in release file"""

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-04-02"),
        "stop_time": np.datetime64("2015-04-05"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "continuous",
        "release_frequency": np.timedelta64(12, "h"),
        "particle_variables": [],
    }

    # Release file: create, read and remove
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 201\n")
        f.write("3 2015-04-03 200 202\n")
        f.write("1 2015-04-08 300 203\n")
    release = ParticleReleaser(config, grid=None)
    os.remove("release.rls")

    # Correct release times
    # First release neglected since before start
    release_times = [
        "2015-04-02",
        "2015-04-02 12",
        "2015-04-03",
        "2015-04-03 12",
        "2015-04-04",
        "2015-04-04 12",
    ]
    release_times = np.array(release_times, dtype=np.datetime64)

    assert len(release.times) == len(release_times)
    assert np.all(release.times == release_times)

    # The entries have the correct information
    for t, S in enumerate(release):
        assert np.all(S["release_time"] == pd.to_datetime(release_times[t]))
        if t < 2:
            assert np.all(S["pid"] == [2 * t, 2 * t + 1])
            # assert(np.all(S['X'] == 100.0))
        if t > 2:
            assert np.all(S["pid"] == np.array([3 * t, 3 * t + 1, 3 * t + 2]) - 2)
            # assert(np.all(S['X'] == 200.0))


def test_too_early_stop() -> None:
    """Model stop before first release in release file"""

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-03-02"),
        "stop_time": np.datetime64("2015-03-05"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "continuous",
        "release_frequency": np.timedelta64(12, "h"),
        "particle_variables": [],
    }

    # Release file: create, read and remove
    with open("release.rls", mode="w") as f:
        f.write("2 2015-04-01 100 200\n")
        f.write("3 2015-04-03 200 300\n")

    # Should exit
    with pytest.raises(SystemExit):
        ParticleReleaser(config, grid=None)

    # Clean up
    os.remove("release.rls")


def test_subgrid() -> None:
    """Particle release outside subgrid should be ignored"""

    config = {
        "start": "cold",
        "start_time": np.datetime64("2015-03-01"),
        "stop_time": np.datetime64("2015-03-03"),
        "dt": 3600,
        "particle_release_file": "release.rls",
        "release_format": ["mult", "release_time", "X", "Y"],
        "release_dtype": dict(mult=int, release_time=np.datetime64, X=float, Y=float),
        "release_type": "continuous",
        "release_frequency": np.timedelta64(12, "h"),
        "particle_variables": [],
        "grid_args": dict(subgrid=[100, 120, 10, 20]),
    }

    # Release file: create, read and remove
    with open("release.rls", mode="w") as f:
        f.write("2 2015-03-01 110 15\n")  # Inside
        f.write("3 2015-03-01 200 30\n")  # Outside

    # Make the ParticleReleaser object
    release = ParticleReleaser(config, grid=None)
    # Clean out the release file
    os.remove("release.rls")

    # Check some overall sizes
    assert len(release.times) == 4
    assert config["total_particle_count"] == 2 * 4

    for t, S in enumerate(release):
        assert np.all(S["pid"] == [2 * t, 2 * t + 1])
        assert np.all(S["X"] == [110, 110])
        assert np.all(S["Y"] == [15, 15])


if __name__ == "__main__":
    pass
    # test_discrete()
    # git pustest_continuous()
    # test_late_start()
    # test_too_late_start()
    # test_early_stop()
