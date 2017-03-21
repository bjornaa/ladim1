# from ladim.configuration import Configure
import numpy as np
from ladim.state import State


class Container:
    pass


config = Container()
config.dt = 600
config.start_time = np.datetime64('2017-02-10 20')
config.ibm_variables = ['super', 'age']
config.particle_variables = []
config.advection = 'RK4'
config.diffusion = False
config.ibm_module = 'ladim.ibms.luseibm'

state = State(config)
state.pid = np.array([0])
state.X = np.array([10.2])
state.Y = np.array([100.5])
state.Z = np.array([5.0])
state.super = np.array([1001.0])
state.age = np.array([0.0])


def test_state():

    assert(len(state) == 1)
    assert(state.ibm_variables == ['super', 'age'])
    assert(state.X == state['X'])


def test_append():

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
