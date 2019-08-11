# import numpy as np
from ladim.configuration import configure

config_file = "../models/salmon_lice/ladim.yaml"

with open(config_file) as f:
    config = configure(f)

print(config.keys())


def test_top_level():
    # Gjør mer av dette
    # for key in ["time_control", "files", "grid_force", "ibm",
    # "particle_release", "output_variables", "numerics"]:
    for key in ["gridforce", "ibm"]:
        assert key in config


def test_gridforce():
    D = config["gridforce"]
    assert D["module"] == "ladim.gridforce.ROMS"
    assert D["input_file"] == "/scratch/Data/NK800/file_????.nc"
    assert D["subgrid"] == [200, 750, 300, 900]
    assert D["ibm_forcing"] == ["temp", "salt"]
