import numpy as np
from ladim1.ibms import light


class IBM:
    def __init__(self, config):

        # Constants
        mortality = 0.17  # [days-1]

        # mm2m = 0.001
        # g = 9.81
        # tempB = 7.0  # set default temperature

        self.k = 0.2  # Light extinction coefficient
        self.swim_vel = 5e-4  # m/s
        self.vertical_diffusion = True
        self.D = 1e-3  # Vertical mixing [m*2/s]

        self.dt = config["dt"]
        self.mortality_factor = np.exp(-mortality * self.dt / 86400)

    def update_ibm(self, grid, state, forcing):

        # Mortality
        state.super *= self.mortality_factor

        # Update forcing
        state.temp = forcing.field(state.X, state.Y, state.Z, "temp")
        state.salt = forcing.field(state.X, state.Y, state.Z, "salt")

        # Age in degree-days
        state.age += state.temp * state.dt / 86400

        # Light at depth
        lon, lat = grid.lonlat(state.X, state.Y, method="nearest")
        light0 = light.surface_light(state.timestamp, lon, lat)
        Eb = light0 * np.exp(-self.k * state.Z)

        # Swimming velocity
        W = np.zeros_like(state.X)
        # Upwards if light enough (decreasing depth)
        W[Eb >= 0.01] = -self.swim_vel
        # Downwards if salinity < 20
        W[state.salt < 20] = self.swim_vel

        # Random diffusion velocity
        if self.vertical_diffusion:
            rand = np.random.normal(size=len(W))
            W += rand * (2 * self.D / self.dt) ** 0.5

        # Update vertical position, using reflexive boundary condition
        state.Z += W * self.dt

        # For z-version, do not go below 20 m
        state.Z[state.Z >= 20.0] = 19.0

        # Mark particles older than 200 degree days as dead
        state.alive = state.alive & (state.age < 200)
