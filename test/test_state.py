# from ladim.configuration import Configure
from typing import List
import numpy as np
from ladim.state import State


class Container:
    dt = 600
    start_time = np.datetime64('2017-02-10 20')
    ibm_variables = ['super', 'age']
    particle_variables = []  # type: List[str]
    advection = 'RK4'
    diffusion = False
    ibm_module = 'ladim.ibms.luseibm'
    pid = np.array([0])
    X = np.array([10.2])
    Y = np.array([100.5])
    Z = np.array([5.0])
    super = np.array([1001.0])
    age = np.array([0.0])


def test_state():

    state = Container()
    assert(len(state) == 1)
    assert(state.ibm_variables == ['super', 'age'])
    assert(state.X == state['X'])


def test_append():

    state = Container()
    new = {'pid': [1],
           'X': [2.0],
           'Y': [222.2],
           'Z': [5],
           'super': [1002],
           'age': [0]}

    state.append(new)
    assert(len(state) == 2)
    assert(np.all(state.pid == np.array([0, 1])))
    assert(np.all(state['X'] == np.array([10.2, 2.0])))
