from io import StringIO
import numpy as np
import yaml

import pytest
from ladim.configuration import configure_release


def test_missing():
    """Test that missing keywords are handled properly"""
    raw = StringIO(
        """
        particle_release:
            particle_release_file : line.rls
            variables: [X, Y, Z]
            release_time: time
            particle_variables: [release_time]
    """
    )
    conf0 = yaml.safe_load(raw)

    # Missing file name
    A = dict(conf0["particle_release"])
    A.pop("particle_release_file")
    conf = dict(particle_release=A)
    with pytest.raises(SystemExit):
        D = configure_release(conf)

    # Missing variables
    A = dict(conf0["particle_release"])
    A.pop("variables")
    conf = dict(particle_release=A)
    with pytest.raises(SystemExit):
        D = configure_release(conf)


def test_discrete():
    """Test a discrete release configuration"""
    raw = StringIO(
        """
        files:
            particle_release_file : line.rls
        particle_release:
            variables: [X, Y, Z]
            release_time: time
            #particle_variables: [release_time]
    """
    )
    conf = yaml.safe_load(raw)
    D = configure_release(conf)
    assert D["release_file"] == "line.rls"
    assert D["release_type"] == "discrete"
    assert D["release_format"] == ["X", "Y", "Z"]
    assert D["release_dtype"] == dict(X=float, Y=float, Z=float)
    assert D["particle_variables"] == []


def test_continuous():
    """Test a continuous release configuratio"""
    raw = StringIO(
        """
        particle_release:
            particle_release_file : streak.rls
            release_type: 'continuous'
            release_frequency: [1800, s]
            variables: [release_time, X, Y, Z]
            release_time: time
            particle_variables: [release_time]
    """
    )
    conf = yaml.safe_load(raw)
    D = configure_release(conf)
    assert D["release_file"] == "streak.rls"
    assert D["release_type"] == "continuous"
    assert D["release_frequency"] == np.timedelta64(30, "m")
    assert D["release_format"] == ["release_time", "X", "Y", "Z"]
    assert D["release_dtype"] == dict(
        release_time=np.datetime64, X=float, Y=float, Z=float
    )
    assert D["particle_variables"] == ["release_time"]
