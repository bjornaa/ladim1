# from ladim1.configuration import Configure
# from typing import List
import numpy as np
from ladim1.state import State


config = dict(
    warm_start_file="",
    start_time=np.datetime64("2017-02-10 20"),
    dt=600,
    ibm_module="ladim1.ibms.ibm_salmon_lice",
    ibm_variables=["super", "age"],
    particle_variables=[],
    advection="RK4",
    diffusion=False,
)

grid = None

state = State(config, grid)

state["pid"] = np.array([0])
state["X"] = np.array([10.2])
state["Y"] = np.array([100.5])
state["Z"] = np.array([5.0])
state["super"] = np.array([1001.0])
state["age"] = np.array([0.0])


def test_state() -> None:
    """Test state initiation"""
    assert len(state) == 1
    assert state.ibm_variables == ["super", "age"]
    assert state.X == state["X"]


def test_append() -> None:
    """Append to the state"""
    new = dict(pid=[1], X=[2.0], Y=[222.2], Z=[5], super=[1002], age=[0])

    state.append(new, forcing=None)
    assert len(state) == 2
    assert np.all(state.pid == np.array([0, 1]))
    assert np.all(state["X"] == np.array([10.2, 2.0]))

# Make a test where new particles get initial temperature
# from a forcing file