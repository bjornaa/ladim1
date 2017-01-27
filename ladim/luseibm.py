# luseibm


def update_ibm(state, forcing):

    # Reduce super with mortality (correct later)
    state.super *= 0.99

    temp = forcing.sample_field(state.X, state.Y, state.Z, 'temp')
    state.age += temp * state.dt / 86400.0
