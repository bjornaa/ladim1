from io import StringIO
import yaml
import numpy as np

import pytest
from ladim.configuration import configure_time


def test_no_time():
    """No output section in configuration file"""
    input = StringIO(
        """
        gridforce:
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_time(conf)


def test_empty_time():
    """Test for empty output section"""
    input = StringIO(
        """
        time_control:
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_time(conf)


def test_missing_start():
    input = StringIO(
        """
        time_control:
            stop_time: 2019-12-31 23:00:00
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_time(conf)


def test_missing_stop():
    input = StringIO(
        """
        time_control:
            start_time: 2019-01-01 00:00:00
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_time(conf)


def test_missing_reference():
    input = StringIO(
        """
        time_control:
            start_time: 2019-01-01 00:00:00
            stop_time:  2019-12-31 23:00:00
    """
    )
    conf = yaml.safe_load(input)
    D = configure_time(conf)
    assert D["reference_time"] == D["start_time"]


def test_OK():
    input = StringIO(
        """
        time_control:
            start_time:     2019-09-01 00:00:00
            stop_time:      2019-09-30 23:00:00
            reference_time: 2019-01-01 00:00:00
    """
    )
    conf = yaml.safe_load(input)
    D = configure_time(conf)
    assert str(D["start_time"]) == "2019-09-01T00:00:00"
    assert str(D["stop_time"]) == "2019-09-30T23:00:00"
    assert str(D["reference_time"]) == "2019-01-01T00:00:00"
    assert D["start_time"].dtype == "M8[s]"
