# Minimal IBM to kill old particles

DAY = 24 * 60 * 60  # Number of seconds in a day


class IBM:
    def __init__(self, config):
        print("Initializing killer feature")
        pass

    def update_ibm(self, grid, state, forcing):

        # Update the particle age
        state.age += state.dt  # Update the age

        # Mark particles older than 2 days as dead
        state.alive = state.age < 2 * DAY
