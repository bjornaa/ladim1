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
        v = nc.createVariable("position", "i", ("particle",))
        v = nc.createVariable("pid", "i", ("particle_instance",))
        v = nc.createVariable("X", "f4", ("particle_instance"))
        v = nc.createVariable("Y", "f4", ("particle_instance"))
        # Data
        nc.variables["time"][:] = time
        nc.variables["particle_count"][:] = count
        nc.variables["start_time"][:] = time[:nparticles]
        nc.variables["position"][:] = [10000, 10001, 10002]
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
        assert pf.particle_variables == ["start_time", "position"]


def test_pid(particle_file):
    """The pid is correct"""
    with ParticleFile(particle_file) as pf:
        assert pf.pid.isel(time=0) == 0
        assert pf["pid"][0] == 0
        assert pf.pid[0] == 0
        assert all(pf.pid[1] == [0, 1])
        assert list(pf.pid[2]) == [0, 2]
        assert pf.pid[3] == 2


# --- InstanceVariable tests ---

# Detemine how this should work
def test_pid2(particle_file):
    """The pid from an instance variable"""
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(X.pid == pf.ds.pid)
        for i in range(4):
            assert all(X[i].pid == pf.pid[i])
        # X.pid[3] is not the same as X[3].pid
        assert not all(X.pid[3] == X[3].pid)


def test_getX(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert X == pf["X"]
        assert X == pf.variables["X"]  # Obsolete
        assert X.isel(time=0) == 0
        assert X[0] == 0
        assert X[0] == 0
        assert all(X[1] == [1, 11])
        assert all(X[2] == [2, 22])
        assert X[3] == 23


def test_X_slice(particle_file):
    """Can read variables with time slices"""
    with ParticleFile(particle_file) as pf:
        X = pf.X
        V = pf.X[1:3]
        assert len(V) == 2
        assert all(V[0] == X[1])
        assert all(V[1] == X[2])
        assert all(V.da == [1, 11, 2, 22])
        assert all(V.count == X.count[1:3])
        assert all(V.time == X.time[1:3])
        assert all(V.pid == [0, 1, 0, 2])
        V = X[:]
        assert (V.da == X.da).all()
        with pytest.raises(IndexError):
            pf.X[::2]  # Do not accept strides != 1


def test_isel(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(X.isel(time=2) == X[2])


# Ta med noen tester med feil input
def test_sel(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(X.sel(pid=0) == [0, 1, 2])
        assert all(X.sel(pid=1) == [11])
        assert all(X.sel(pid=2) == [22, 23])

        assert all(X.sel(time=X.time[2]) == X[2])
        assert all(X.sel(time="1970-01-01 02") == X[2])
        assert all(X.sel(time=np.datetime64("1970-01-01 02")) == X[2])
        assert all(X.sel(time=datetime.datetime(1970, 1, 1, 2)) == X[2])

        assert X.sel(time="1970-01-01 02", pid=0) == X[2, 0]
        assert X.sel(pid=2, time="1970-01-01 03") == X[3, 2]
        # Determine what to do
        # assert np.isnan(X.sel(pid=1, time="1970-01-01 03"))


def test_full(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        V = X.full()
        assert V[0, 0] == 0
        assert np.isnan(V[0, 1])
        assert np.isnan(V[0, 2])
        assert V[1, 0] == 1
        assert V[1, 1] == 11
        assert np.isnan(V[1, 2])
        assert V[2, 0] == 2
        assert np.isnan(V[2, 1])
        assert V[2, 2] == 22
        assert np.isnan(V[3, 0])
        assert np.isnan(V[3, 1])
        assert V[3, 2] == 23


def test_position(particle_file):
    with ParticleFile(particle_file) as pf:
        pos = pf.position(1)
        assert all(pos.X == pf.X[1])
        assert all(pos.Y == pf.Y[1])
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


def test_particle_variable(particle_file):
    """Two particle variables, start_time and position"""
    with ParticleFile(particle_file) as pf:
        assert pf.start_time[0] == np.datetime64("1970-01-01")
        assert pf["start_time"][1] == np.datetime64("1970-01-01 01")
        assert pf["position"][0] == 10000
        assert pf["position"][1] == 10001
        assert pf["position"][2] == 10002
        # pf.position is a method, therefore not a particle variable
        with pytest.raises(TypeError):
            pf.position[2]
