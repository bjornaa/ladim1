import numpy as np
from ladim1.utilities import timestep2stamp, timestamp2step

config = dict(dt=600, start_time=np.datetime64("2017-02-10 20"))


def test_step2stamp() -> None:
    n = 24 * 3600 // config["dt"]  # 24 hours
    answer = np.datetime64("2017-02-11T20:00:00")
    timestamp = timestep2stamp(config, n)
    assert timestamp == answer


def test_stamp2step() -> None:
    # time step 5 i.e. + 50 min
    answer = 5
    timestamp = np.datetime64("2017-02-10 20:50")
    step = timestamp2step(config, timestamp)
    assert step == answer
