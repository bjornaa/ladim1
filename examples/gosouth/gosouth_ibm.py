import numpy as np


class IBM:
    """Adding a constant horizontal velocity to the particle tracking"""

    def __init__(self, config):
        # Can not initialize here, as grid is not available

        # Azimuthal direction, 0 = N, 90 = E, 180 = S, 270 = W
        self.direction = 180  # [clockwise degree from North]
        self.speed = 0.02  # [m/s]
        self.first = True  # Flag for first time

    def update_ibm(self, grid, state, forcing):

        # Initialize on first call
        if self.first:
            angle = grid.grid.angle
            azim = self.direction * np.pi / 180.0
            # (self.Xs, self.Ys) is unit vector in the direction
            self.Xs = np.sin(azim + angle)
            self.Ys = np.cos(azim + angle)
            self.first = False

        # Update position
        I = np.round(state.X).astype("int")
        J = np.round(state.Y).astype("int")
        X1 = state.X + self.speed * state.dt * self.Xs[J, I] / grid.grid.dx[J, I]
        Y1 = state.Y + self.speed * state.dt * self.Ys[J, I] / grid.grid.dy[J, I]

        # Do not move out of grid or on land
        I = grid.ingrid(X1, Y1) & grid.atsea(X1, Y1)
        state.X[I] = X1[I]
        state.Y[I] = Y1[I]
