from io import StringIO
import numpy as np
import yaml

import pytest
from ladim.configuration import configure_release

# Ha en del sjekk på ting som mangler


def test_discrete():
    raw = StringIO(
        """
        files:
            particle_release_file : line.rls
        particle_release:
            variables: [X, Y, Z]
            release_time: time
            particle_variables: [release_time]
    """
    )
    conf = yaml.safe_load(raw)
    D = configure_release(conf)
    assert D["release_file"] == "line.rls"
    assert D["release_type"] == "discrete"
    assert D["release_format"] == ["X", "Y", "Z"]
    assert D["release_dtype"] == {"X": float, "Y": float, "Z": float}
    assert D["particle_variables"] == ["release_time"]


def test_continuous():
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
    assert D["release_dtype"] == {
        "release_time": np.datetime64,
        "X": float,
        "Y": float,
        "Z": float,
    }
    assert D["particle_variables"] == ["release_time"]
