import os
import pytest

import datetime

import numpy as np

# import xarray as xr
# from pathlib import Path
from netCDF4 import Dataset
from postladim import ParticleFile

# Should not have to repeat this from test_particlefile.py
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
    pfile = "qtest.nc"
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


def test_values(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(X.values == X.da.values)

def test_array(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(np.array(X) == X.da.values)
        assert all(np.array(X[1]) == X[1])
        assert all(np.array(X[0:2]) == X[0:2])


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
        with pytest.raises(TypeError):
            # Need an argument
            X.isel()
        with pytest.raises(TypeError):
            # Only keyword arguments
            X.isel(2)


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
        with pytest.raises(KeyError):
            X.sel(time="1980-01-01")
        with pytest.raises(KeyError):
            X.sel(pid=-1)
        with pytest.raises(ValueError):
            X.sel()
        with pytest.raises(TypeError):
            X.sel("1970-01-01 02")


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
        X, Y = pf.position(time=1)
        assert all(X == pf.X[1])
        assert all(Y == pf.Y[1])
        X, Y = pf.position(2)
        assert all(X == pf.X[2])
        assert all(Y == pf.Y[2])


def test_particle_variable(particle_file):
    """Two particle variables, start_time and location_id"""
    with ParticleFile(particle_file) as pf:
        assert pf.start_time[0] == np.datetime64("1970-01-01")
        assert pf["start_time"][1] == np.datetime64("1970-01-01 01")
        assert all(pf.location_id == np.array([10000, 10001, 10002]))
        assert all(pf.location_id == pf["location_id"][:])
        # Not working (but should?)
        # assert all(pf.location_id == pf["location_id"])