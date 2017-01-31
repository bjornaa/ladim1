
import numpy as np


class TrackPart:

    def __init__(self, config):
        self.dt = config.dt
        if config.advection:
            self.advect = getattr(self, config.advection)
        else:
            self.advect = None
        # Read from config:
        self.diffusion = config.diffusion
        if self.diffusion:
            self.D = config.diffusion_coefficient  # [m2.s-1]

    def move_particles(self, grid, forcing, state):

        X, Y = state.X, state.Y
        self.pm, self.pn = grid.sample_metric(X, Y)
        dt = self.dt
        self.num_particles = len(X)

        U = np.zeros(self.num_particles, dtype=float)
        V = np.zeros(self.num_particles, dtype=float)

        # --- Advection ---
        if self.advect:
            Uadv, Vadv = self.advect(grid, forcing, state)
            U = U + Uadv
            V = V + Vadv

        # --- Diffusion ---
        if self.diffusion:
            Udiff, Vdiff = self.diffuse()
            U = U + Udiff
            V = V + Vdiff

        # --- Move the particles

        # New position, untested
        X1 = X + U * self.pm * dt
        Y1 = Y + V * self.pn * dt

        # Land, boundary treatment. Do not move the particles
        # Consider a sequence of different actions
        # I = (grid.ingrid(X1, Y1)) & (grid.atsea(X1, Y1))
        I = grid.atsea(X1, Y1)
        # I = True
        X[I] = X1[I]
        Y[I] = Y1[I]
        # X, Y = X1, Y1
        # Må ha blitt laget en kopi et sted
        state.X = X
        state.Y = Y

    def EF(self, grid, forcing, state):
        """Euler-Forward advection"""

        X, Y, Z = state['X'], state['Y'], state['Z']
        # dt = self.dt
        # pm, pn = grid.sample_metric(X, Y)

        U, V = forcing.sample_velocity(X, Y, Z)

        return U, V
        # X += U * pm * dt
        # Y += V * pm * dt

    def RK2(self, grid, forcing, state):
        """Runge-Kutta second order = Heun scheme"""

        X, Y, Z = state['X'], state['Y'], state['Z']
        dt = self.dt
        pm, pn = grid.sample_metric(X, Y)

        U, V = forcing.sample_velocity(X, Y, Z)
        X1 = X + 0.5 * U * pm * dt
        Y1 = Y + 0.5 * V * pn * dt

        U, V = forcing.sample_velocity(X1, Y1, Z, tstep=0.5)
        # X += U * pm * dt
        # Y += V * pn * dt
        return U, V

    def RK4(self, grid, forcing, state):
        """Runge-Kutta fourth order"""

        X, Y, Z = state['X'], state['Y'], state['Z']
        dt = self.dt
        pm, pn = grid.sample_metric(X, Y)

        U1, V1 = forcing.sample_velocity(X, Y, Z, tstep=0.0)
        X1 = X + 0.5 * U1 * pm * dt
        Y1 = Y + 0.5 * V1 * pn * dt

        U2, V2 = forcing.sample_velocity(X1, Y1, Z, tstep=0.5)
        X2 = X + 0.5 * U2 * pm * dt
        Y2 = Y + 0.5 * V2 * pn * dt

        U3, V3 = forcing.sample_velocity(X2, Y2, Z, tstep=0.5)
        X3 = X + U3 * pm * dt
        Y3 = Y + V3 * pn * dt

        U4, V4 = forcing.sample_velocity(X3, Y3, Z, tstep=1.0)

        # X += (U1 + 2*U2 + 2*U3 + U4) * pm * dt / 6.0
        # Y += (V1 + 2*V2 + 2*V3 + V4) * pn * dt / 6.0
        U = (U1 + 2*U2 + 2*U3 + U4) / 6.0
        V = (V1 + 2*V2 + 2*V3 + V4) / 6.0

        return U, V

    def diffuse(self):
        """Random walk diffusion"""

        # Diffusive velocity
        stddev = (2*self.D/self.dt)**0.5
        U = stddev * np.random.normal(size=self.num_particles)
        V = stddev * np.random.normal(size=self.num_particles)

        return U, V
