import os
import pytest

import datetime

import numpy as np

# import xarray as xr
# from pathlib import Path
from netCDF4 import Dataset
from postladim import ParticleFile


@pytest.fixture(scope="module")
def particle_file():
    # set up
    # Return a small particle file
    #
    #  0   -   -
    #  1  11   -
    #  2   -  22
    #  -   -  23
    #
    pfile = "test.nc"
    nparticles = 3
    X = np.array(
        [[0, np.nan, np.nan], [1, 11, np.nan], [2, np.nan, 22], [np.nan, np.nan, 23]]
    )
    Y = np.array(
        [[2, np.nan, np.nan], [3, 8, np.nan], [4, np.nan, 9], [np.nan, np.nan, 10]]
    )
    ntimes = X.shape[0]
    pid = np.multiply.outer(ntimes * [1], list(range(nparticles)))
    pid[np.isnan(X)] = -99  # Undefined integer
    time = 3600 * np.arange(ntimes)  # hourly timesteps
    count = (np.ones(np.shape(X)) - np.isnan(X)).sum(axis=1)
    with Dataset(pfile, mode="w") as nc:
        # Dimensions
        nc.createDimension("particle", nparticles)
        nc.createDimension("particle_instance", None)
        nc.createDimension("time", ntimes)
        # Variables
        v = nc.createVariable("time", "f8", ("time",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = nc.createVariable("particle_count", "i", ("time",))
        v = nc.createVariable("start_time", "f8", ("particle",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = nc.createVariable("location_id", "i", ("particle",))
        v = nc.createVariable("pid", "i", ("particle_instance",))
        v = nc.createVariable("X", "f4", ("particle_instance",))
        v = nc.createVariable("Y", "f4", ("particle_instance",))
        # Data
        nc.variables["time"][:] = time
        nc.variables["particle_count"][:] = count
        nc.variables["start_time"][:] = time[:nparticles]
        nc.variables["location_id"][:] = [10000, 10001, 10002]
        nc.variables["pid"][:] = [v for v in pid.flat if v >= 0]
        nc.variables["X"][:] = [v for v in X.flat if not np.isnan(v)]
        nc.variables["Y"][:] = [v for v in Y.flat if not np.isnan(v)]

    yield pfile

    # tear down
    os.remove(pfile)


def test_open():
    with pytest.raises(FileNotFoundError):
        pf = ParticleFile("no_such_file.nc")


def test_count(particle_file):
    """Alignment of time frames in the particle file."""
    with ParticleFile(particle_file) as pf:
        assert pf.num_times == 4
        assert all(pf.start == [0, 1, 3, 5])
        assert list(pf.count) == [1, 2, 2, 1]
        assert list(pf.end) == [1, 3, 5, 6]
        assert len(pf) == 4
        assert pf.num_particles == 3


def test_time(particle_file):
    """Time handled correctly"""
    with ParticleFile(particle_file) as pf:
        assert pf.time[3] == np.datetime64("1970-01-01 03")
        times2 = [np.datetime64(t) for t in ["1970-01-01", "1970-01-01 01"]]
        assert all(pf.time[:2] == times2)
        # Old callable notation still works
        assert pf.time(3) == pf.time[3]
        assert str(pf.time(3)) == "1970-01-01T03:00:00"


def test_variables(particle_file):
    """Indentifies the variables to correct category"""
    with ParticleFile(particle_file) as pf:
        assert pf.instance_variables == ["pid", "X", "Y"]
        assert pf.particle_variables == ["start_time", "location_id"]


def test_pid(particle_file):
    """The pid is correct"""
    with ParticleFile(particle_file) as pf:
        assert pf.pid.isel(time=0) == 0
        assert pf["pid"][0] == 0
        assert pf.pid[0] == 0
        assert all(pf.pid[1] == [0, 1])
        assert list(pf.pid[2]) == [0, 2]
        assert pf.pid[3] == 2


def test_position(particle_file):
    with ParticleFile(particle_file) as pf:
        X, Y = pf.position(time=1)
        assert all(X == pf.X[1])
        assert all(Y == pf.Y[1])
        X, Y = pf.position(2)
        assert all(X == pf.X[2])
        assert all(Y == pf.Y[2])


def test_trajectory(particle_file):
    with ParticleFile(particle_file) as pf:
        X, Y = pf.trajectory(2)
        assert all(X == [22, 23])
        assert all(Y == [9, 10])
        traj = pf.trajectory(0)
        assert len(traj) == 3
        assert all(traj.time == pf.time[:-1])
        assert all(traj.X == pf.X.sel(pid=0))
        assert all(traj.Y == pf.Y.sel(pid=0))
