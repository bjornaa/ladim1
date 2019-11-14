from io import StringIO
import yaml
import numpy as np

import pytest
from ladim.configuration import configure_output

# Should go further, test for obligatory elements


def test_no_output():
    """No output section in configuration file"""
    raw = StringIO(
        """
        gridforce:
    """
    )
    conf = yaml.safe_load(raw)
    with pytest.raises(SystemExit):
        configure_output(conf, {})


def test_empty_output():
    """Test for empty output section"""
    raw = StringIO(
        """
        output:
    """
    )
    conf = yaml.safe_load(raw)
    with pytest.raises(SystemExit):
        configure_output(conf, {})


def test_divible_by_timestep():
    """Output period should be divisible by time step"""
    raw = StringIO(
        """

        output:
            outper: [1, h]
        numerics:
            dt: [1000, s]
    """
    )
    time_control = {
        "start_time": np.datetime64("2015-04-02"),
        "stop_time": np.datetime64("2015-04-05"),
    }
    conf = yaml.safe_load(raw)
    with pytest.raises(SystemExit):
        configure_output(conf, time_control)


def test_OK():
    raw = StringIO(
        """
        output:
            # Output format, default = NETCDF3_64BIT = NETCDF3_64BIT_OFFSET
            format: NETCDF3_64BIT_DATA
            # Output period, format [value, unit], unit = s, m, h, or d
            outper: [1, h]
            # Variable names
            particle: [release_time]
            instance: [pid, X, Y, Z]
            # NetCDF arguments
            release_time:
                ncformat: f8
                long_name: particle release time
                units: seconds since reference_time
            pid: {ncformat: i4, long_name: particle identifier}
            X: {ncformat: f4, long_name: particle X-coordinate}
            Y: {ncformat: f4, long_name: particle Y-coordinate}
            Z:
                ncformat: f4
                long_name: particle depth
                standard_name: depth_below_surface
                units: m
                positive: down
        numerics:
            dt: [600, s]

    """
    )
    conf = yaml.safe_load(raw)
    time_config = {
        "start_time": np.datetime64("2019-01-01 00:00:00"),
        "stop_time": np.datetime64("2019-09-30 23:00:00"),
        "reference_time": np.datetime64("2019-01-01 00:00:00"),
    }
    D = configure_output(conf, time_config)
    assert D["format"] == "NETCDF3_64BIT_DATA"
    assert D["skip_initial"] == False
    assert D["numrec"] == 0
    assert D["output_period"] == 6  # units = time steps
    assert D["particle"] == ["release_time"]
    assert D["instance"] == ["pid", "X", "Y", "Z"]
    print(D)
    V = D["variables"]
    assert V["pid"] == {"ncformat": "i4", "long_name": "particle identifier"}
    assert V["X"]["long_name"] == "particle X-coordinate"
    assert (
        V["release_time"]["units"] == f"seconds since {time_config['reference_time']}"
    )


def rest_accept_output_variables():
    """Accept obsolete section output_control"""
    input = StringIO(
        """
        output_variables:
            format: NETCDF3_CLASSIC
    """
    )
    conf = yaml.safe_load(input)
    D = configure_output(conf)
    assert D["format"] == "NETCDF3_CLASSIC"
