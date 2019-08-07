import os
import pytest

# import numpy as np
from pathlib import Path
from netCDF4 import Dataset
from postladim import ParticleFile


@pytest.fixture(scope="module")
def particle_file():
    # set up
    # Return a small particle file
    pfile = "test.nc"
    with Dataset(pfile, mode="w") as pf:
        # Dimensions
        pf.createDimension("particle", 2)
        pf.createDimension("particle_instance", None)
        pf.createDimension("time", 4)
        # Variables
        v = pf.createVariable("time", "f8", ("time",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = pf.createVariable("particle_count", "i", ("time",))
        v = pf.createVariable("start_time", "f8", ("particle",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = pf.createVariable("position", "i", ("particle",))
        v = pf.createVariable("pid", "i", ("particle_instance",))
        v = pf.createVariable("X", "f4", ("particle_instance"))
        v = pf.createVariable("Y", "f4", ("particle_instance"))
        # Data
        pf.variables["time"][:] = [0, 3600, 7200, 10800]
        pf.variables["particle_count"][:] = [1, 2, 2, 1]
        pf.variables["start_time"][:] = [0, 3600]
        pf.variables["position"][:] = [1000, 2000]
        pf.variables["pid"][:] = [0, 0, 1, 0, 1, 1]
        pf.variables["X"][:] = [5, 6, 10, 7, 11, 12]
        pf.variables["Y"][:] = [2, 3, 8, 4, 9, 10]

    yield pfile

    # tear down
    os.remove(pfile)


def test_count(particle_file):
    """Alignment of time slices"""
    with ParticleFile(particle_file) as pf:
        assert pf.num_times == 4
        assert list(pf.start) == [0, 1, 3, 5]
        assert list(pf.count) == [1, 2, 2, 1]
        assert list(pf.end) == [1, 3, 5, 6]


def test_variables(particle_file):
    """Variable types"""
    with ParticleFile(particle_file) as pf:
        assert pf.instance_variables == ["pid", "X", "Y"]
        assert pf.particle_variables == ["start_time", "position"]
        assert pf.start_time[0] == 0
        assert pf.start_time[1] == 3600


def test_time(particle_file):
    """Time handled correctly"""
    with ParticleFile(particle_file) as pf:
        assert str(pf.time(3)) == "1970-01-01 03:00:00"


def test_pid(particle_file):
    """The pid is correct"""
    with ParticleFile(particle_file) as pf:
        assert pf.pid[0] == 0
        assert all(pf.pid[1] == [0, 1])
        assert list(pf.pid[2]) == [0, 1]
        assert pf.pid[3] == 1
        assert pf["pid"][3] == 1
        assert pf.variables["pid"][3] == 1


def test_get_X(particle_file):
    with ParticleFile(particle_file) as pf:
        assert pf.X[0] == 5
        assert all(pf.X[1] == [6, 10])
        assert all(pf.X[2] == [7, 11])
        assert pf.X[3] == 12
        assert all(pf["X"][2] == [7, 11])
        assert all(pf.variables["X"][2] == [7, 11])
        assert all(pf.nc.variables["X"][pf.start[2] : pf.end[2]] == [7, 11])


def test_X_slice(particle_file):
    """Can read variables with slices"""
    with ParticleFile(particle_file) as pf:
        assert list(pf.X[:2]) == [5, 6, 10]
        assert list(pf["X"][:2]) == [5, 6, 10]
        assert list(pf.X[1:3]) == [6, 10, 7, 11]
        assert all(pf.X[1:3] == pf.nc.variables["X"][pf.start[1] : pf.end[2]])
        assert list(pf.X[:]) == [5, 6, 10, 7, 11, 12]
        assert all(pf.X[:] == pf.nc.variables["X"][:])
        with pytest.raises(IndexError):
            pf.X[::2]  # Do not accept strides != 1


def test_slice_advanced(particle_file):
    """More advanced slicing"""
    with ParticleFile(particle_file) as pf:
        I = [True, True, False, True, False, False]
        assert list(pf.X[I] == [5, 6, 7])
        assert list(pf.X[[0, 1, 3]] == [5, 6, 7])
        # Accept only integer or boolean sequences
        with pytest.raises(IndexError):
            pf.X["abc"]  # Not a sequence of integers
        with pytest.raises(IndexError):
            pf.X[3.14]  # Not integer, slice, or sequence
        with pytest.raises(IndexError):  # Not a sequence
            pf.X[{"a": 1}]  # Not integer, slice, or sequence
        # Strange feature, inherited from NetCDF4
        assert pf.X[[3.14]] == pf.X[[3]]


def test_isel(particle_file):
    """Indexing in xarray style"""
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert X.isel() == X
        assert all(X.isel(time=2) == X[2])




def test_position(particle_file):
    with ParticleFile(particle_file) as pf:
        X, Y = pf.position(2)
        assert all(X == pf.X[2])
        assert all(Y == pf.Y[2])
        # pf['position'] exists for this file and is something different
        assert list(pf["position"]) == [1000, 2000]
