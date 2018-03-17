import numpy as np
from ladim.state import State
# from ladim.tracker import Tracker


class Grid:

    def __init__(self):
        self.imax = 100
        self.jmax = 100
        self.xmin = 0.0
        self.xmax = self.imax-1.0
        self.ymin = 0.0
        self.ymax = self.jmax-1.0

    def sample_metric(self, X, Y):
        return 100*np.ones_like(X), 100*np.ones_like(Y)

    def sample_depth(self, X, Y):
        return 50.0*np.ones_like(X)

    def ingrid(self, X, Y):
        return ((1 <= X) & (X <= self.imax-2) &
                (1 <= Y) & (Y <= self.jmax-2))

    def atsea(self, X, Y):
        return np.ones(len(X), dtype='bool')

    def lonlat(self, X, Y):
        return 5.0*np.ones(len(X)), 60.0*np.ones(len(X))


class Forcing:

    def __init__(self):
        pass

    def velocity(self, X, Y, Z):
        return np.ones_like(X), np.zeros_like(Y)

    def field(self, X, Y, Z, name):
        return 8.0*np.ones_like(X)


def test_out_of_area():
    """Particles moving out of the area should be killed

       Check for bug where the IBM woke them up again

    """

    config = dict(
        warm_start_file='',
        start_time=np.datetime64('2017-02-10 20'),
        dt=600,
        particle_variables=[],
        ibm_module='ladim.ibms.ibm_salmon_lice',
        ibm_variables=['super', 'age'],
        advection='EF',
        diffusion=False,
    )
    grid = Grid()
    state = State(config)
    forcing = Forcing()

    state.pid = np.array([0, 1, 2])
    state.X = np.array([30, grid.imax-2.1, 11.1])
    state.Y = np.array([30, grid.jmax-2.1, 22.2])
    state.Z = 5.0*np.ones(len(state.pid))
    state['super'] = np.array([1001.0, 1002.0, 1003.0])
    state['age'] = np.zeros(len(state.pid))

    state.update(grid, forcing)

    # Killed particle out-of-area
    assert len(state.pid) == 2
    assert state.pid[0] == 0
    assert state.pid[1] == 2


if __name__ == '__main__':
    test_out_of_area()
