from pathlib import Path
from datetime import datetime
import numpy as np
from netCDF4 import Dataset
import pytest
from ladim1.gridforce.ROMS import Forcing


@pytest.fixture
def nc_files():
    # Setup, make netCDF files with time records
    for i in range(10):
        fname = f"test_file{i:02d}.nc"
        ncid = Dataset(fname, mode="w")
        ncid.createDimension("time", size=3)
        v = ncid.createVariable("ocean_time", "float64", ("time",))
        v.units = "seconds since 2015-01-01 00:00:00"
        v[:] = [i * 86400, i * 86400 + 3600, i * 86400 + 7200]
        ncid.close()
    yield
    # Remove the files
    for i in range(10):
        Path(f"test_file{i:02d}.nc").unlink()


def test_find_files(nc_files):
    """Finding correct forcing files"""
    config = dict(input_file="test_file*.nc")
    files = Forcing.find_files(config)
    assert len(files) == 10
    # Limit from front
    config = dict(input_file="test_file*.nc", first_file="test_file02.nc")
    files = Forcing.find_files(config)
    assert files[0] == "test_file02.nc"
    assert len(files) == 8
    # Limit from back
    config = dict(input_file="test_file*.nc", last_file="test_file02.nc")
    files = Forcing.find_files(config)
    assert files[-1] == "test_file02.nc"
    assert len(files) == 3
    # Last file after all
    config = dict(input_file="test_file*.nc", last_file="xxx.nc")
    files = Forcing.find_files(config)
    assert len(files) == 10
    # First file after all
    config = dict(input_file="test_file*.nc", first_file="xxx.nc")
    files = Forcing.find_files(config)
    assert files == []
    # Test single file
    config = dict(input_file="test_file03.nc")
    files = Forcing.find_files(config)
    assert files == ["test_file03.nc"]


def test_scan_times(nc_files):

    # Everything is OK
    files = [f"test_file{i:02d}.nc" for i in range(10)]
    all_frames, num_frames = Forcing.scan_file_times(files)
    assert len(all_frames) == 30
    assert all_frames[4] == np.datetime64("2015-01-02 01")
    assert all(np.unique(all_frames) == all_frames)
    assert len(num_frames) == 10
    assert num_frames["test_file05.nc"] == 3

    # Time frames not ordered
    files = ["test_file05.nc", "test_file03.nc"]
    with pytest.raises(SystemExit):
        all_frames, time_frames = Forcing.scan_file_times(files)

    # Duplicate time frames
    files = ["test_file05.nc", "test_file05.nc"]
    with pytest.raises(SystemExit):
        all_frames, time_frames = Forcing.scan_file_times(files)


def test_forcing_steps(nc_files):
    # Test OK
    start = np.datetime64("2015-01-03 13:00:00")
    stop = np.datetime64("2015-01-04 19:00:00")
    dt = 1800
    config = dict(start_time=start, stop_time=stop, dt=dt)
    files = [f"test_file{i:02d}.nc" for i in range(10)]
    all_frames, num_frames = Forcing.scan_file_times(files)
    steps, file_idx, frame_idx = Forcing.forcing_steps(
        config, files, all_frames, num_frames
    )

    assert len(steps) == len(all_frames)
    dstart = start - np.datetime64("2015-01-01")
    k = int(dstart / np.timedelta64(dt, "s"))
    assert steps[0] == -k
    assert steps[1] - steps[0] == 3600 / dt
    assert steps[3] - steps[0] == 24 * 3600 / dt

    d = 5  # file number = day number
    f = 1  # time frame = hour, 0 <= f < 3
    k = d * 3 + f  # forcing index
    # time step from first file,
    #   1 file per day, 1 hour per time frame, 2 steps per hour
    v = steps[0] + (d * 24 + f) * 2
    assert all_frames[k] == np.datetime64(f"2015-01-{1+d:02d} {f:02d}")
    assert steps[k] == v
    assert file_idx[v] == f"test_file{d:02d}.nc"
    assert frame_idx[v] == f  # second time frame in file
