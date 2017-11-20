# from ladim.configuration import Configure
# from typing import List
import numpy as np
from ladim.state import State


config = dict(
    start_time=np.datetime64('2017-02-10 20'),
    dt=600,
    state_variables=['pid', 'X', 'Y', 'Z', 'super', 'age'],
    particle_variables=[],
    advection='RK4',
    diffusion=False,
    ibm_module='ladim.ibms.ibm_salmon_lice')

state = State(config)

state['pid'] = np.array([0])
state['X'] = np.array([10.2])
state['Y'] = np.array([100.5])
state['Z'] = np.array([5.0])
state['super'] = np.array([1001.0])
state['age'] = np.array([0.0])


class Grid:

    def __init__(self):
        pass


grid = Grid()


def test_state() -> None:
    """Test state initiation"""
    assert(len(state) == 1)
    assert(state.X == state['X'])
    assert(state.X == np.array([10.2]))


def test_append() -> None:
    """Append to the state"""
    new = dict(pid=[1],
               X=[2.0],
               Y=[222.2],
               Z=[5],
               super=[1002],
               age=[0])

    print(state.X)
    state.append(new, grid)
    print(state.X)
    assert(len(state) == 2)
    assert(np.all(state.pid == np.array([0, 1])))
    assert(np.all(state['X'] == np.array([10.2, 2.0])))


if __name__ == '__main__':
    test_append()
