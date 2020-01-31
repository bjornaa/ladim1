from pathlib import Path
from datetime import datetime
import numpy as np
from netCDF4 import Dataset
import pytest
from ladim.gridforce.ROMS import Forcing

@pytest.fixture
def nc_files():
    # Setup, make netCDF files with time records
    for i in range(10):
        fname = f'file{i:02d}.nc'
        ncid = Dataset(fname, mode='w')
        ncid.createDimension('time', size=3)
        v = ncid.createVariable('ocean_time', 'float64', ('time',))
        v.units = "seconds since 2015-01-01 00:00:00"
        v[:] = [i*86400, i*86400+3600, i*86400+7200]
        ncid.close()
    yield
    # Remove the files
    for i in range(3):
        Path(f"file{i:02d}.nc").unlink()


def test_find_files(nc_files):
    """Finding correct forcing files"""
    config = dict(input_file='file*.nc')
    files = Forcing.find_files(config)
    assert len(files) == 10
    # Limit from front
    config = dict(input_file='file*.nc', first_file="file02.nc")
    files = Forcing.find_files(config)
    assert files[0] == "file02.nc"
    assert len(files) == 8
    # Limit from back
    config = dict(input_file='file*.nc', last_file="file02.nc")
    files = Forcing.find_files(config)
    assert files[-1] == "file02.nc"
    assert len(files) == 3
    # Last file after all
    config = dict(input_file='file*.nc', last_file="kake.nc")
    files = Forcing.find_files(config)
    assert len(files) == 10
    # First file after all
    config = dict(input_file='file*.nc', first_file="kake.nc")
    files = Forcing.find_files(config)
    assert files == []
    # Test single file
    config = dict(input_file='file03.nc')
    files = Forcing.find_files(config)
    assert files == ['file03.nc']


def test_scan_times(nc_files):
    # Everything is OK
    files = [f"file{i:02d}.nc" for i in range(10)]
    #print(files)
    all_frames, time_frames = Forcing.scan_file_times(files)
    assert len(all_frames) == 30
    assert all_frames[4] == np.datetime64("2015-01-02 01")
    assert all(np.unique(all_frames) == all_frames)
    assert len(time_frames) == 10
    assert len(time_frames["file05.nc"]) == 3
    assert time_frames["file05.nc"][2] == np.datetime64("2015-01-06 02")

    # Time frames not ordered
    files = ["file05.nc", "file03.nc"]
    with pytest.raises(SystemExit):
       all_frames, time_frames = Forcing.scan_file_times(files)

    # Duplicate time frames
    files = ["file05.nc", "file05.nc"]
    with pytest.raises(SystemExit):
       all_frames, time_frames = Forcing.scan_file_times(files)
