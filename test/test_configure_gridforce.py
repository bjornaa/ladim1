from io import StringIO
import yaml

import pytest
from ladim.configuration import configure_gridforce


def test_no_gridforce():
    """gridforce section is mandatory"""
    input = StringIO("")
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_gridforce(conf)


def test_no_content():
    input = StringIO(
        """
        gridforce:
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_gridforce(conf)


def test_no_module():
    input = StringIO(
        """
        grid_file: grid.nc
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_gridforce(conf)


def test_OK():
    input = StringIO(
        """
        gridforce:
            module: mygridforce.py
            extra: 42
    """
    )
    conf = yaml.safe_load(input)
    config = {"gridforce": configure_gridforce(conf)}
    assert config["gridforce"]["module"] == "mygridforce.py"
    assert config["gridforce"]["extra"] == 42


def test_backwards_grid_file():
    """Accept grid and input file in files section
       For backwards compability for the ROMS gridforce module
    """
    input = StringIO(
        """
        gridforce:
            module: ladim.gridforce.ROMS.py
        files:
            grid_file: grid.nc
            input_file: history.nc
    """
    )
    conf = yaml.safe_load(input)
    config = {"gridforce": configure_gridforce(conf)}
    assert config["gridforce"]["grid_file"] == "grid.nc"
    assert config["gridforce"]["input_file"] == "history.nc"
