from io import StringIO
import yaml

import pytest
from ladim.configuration import *


def test_no_ibm():
    """No IBM info"""
    input = StringIO("")
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"] == {}


def test_empty_ibm():
    """Empty IBM string"""
    input = StringIO(
        """
        ibm:
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"] == {}


def test_no_ibm_module():
    """Active IBM, but no IBM module"""
    input = StringIO(
        """
        ibm:
            variables: [temp]
    """
    )
    conf = yaml.safe_load(input)
    with pytest.raises(SystemExit):
        configure_ibm(conf)


def test_module_and_no_variables():
    """IBM module OK, but no variables specified"""
    input = StringIO(
        """
        ibm:
            module: myibm
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["module"] == "myibm"
    assert config["ibm"]["variables"] == []


def test_variables():
    """The variables key is handled properly"""
    input = StringIO(
        """
        ibm:
            module: myibm
            variables: [temp]
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["variables"] == ["temp"]


def test_extra_keys():
    """Extra keys are passed on to config["ibm"]"""
    input = StringIO(
        """
        ibm:
            module: myibm
            variables: [temp]
            lifetime: 4  # days
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["lifetime"] == 4


def test_old_module():
    """Obsolete way of specifying IBM-module is still working"""
    input = StringIO(
        """
        ibm:
            ibm_module: myibm
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["module"] == "myibm"
    # The ibm_module key is deleted
    with pytest.raises(KeyError):
        config["ibm"]["ibm_module"]


def test_old_variables():
    """Obsolete way of specifying IBM variables is still working"""
    input = StringIO(
        """
        ibm:
            ibm_module: myibm
        state:
            ibm_variables: [temp]
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["variables"] == ["temp"]


def test_empty_state():
    """Should work with empty state field, this  was a bug"""
    input = StringIO(
        """
        ibm:
            ibm_module: myibm
        state:
    """
    )
    conf = yaml.safe_load(input)
    config = {"ibm": configure_ibm(conf)}
    assert config["ibm"]["variables"] == []
