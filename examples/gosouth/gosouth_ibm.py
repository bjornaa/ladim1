import numpy as np


class IBM:

    def __init__(self, config):
        # Do not initialize here, as grid is not available
        self.first = True   # Flag for first time
        self.speed = 0.1   # southward speed 2 cm/s

    def update_ibm(self, grid, state, forcing):

        if self.first:  # Initialize
            angle = grid.grid.angle
            # Grid cell centers
            self.Xs = -np.sin(angle)
            self.Ys = -np.cos(angle)
            self.first = False

        # Update position
        # Feil, finn grid celle
        I = np.round(state.X).astype('int')
        J = np.round(state.Y).astype('int')
        X1 = state.X + self.speed * self.Xs[J, I] * state.dt / grid.grid.dx[J, I]
        Y1 = state.Y + self.speed * self.Ys[J, I] * state.dt / grid.grid.dy[J, I]

        # Do not move out of grid or on land
        I = grid.ingrid(X1, Y1) & grid.atsea(X1, Y1)
        state.X[I] = X1[I]
        state.Y[I] = Y1[I]