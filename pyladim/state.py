# -*- coding: utf-8 -*-

# Classes for Particle and State variables

import numpy as np

# ------------------------


class ParticleVariables(object):
    """Class holding the particle variables"""

    def __init__(self, setup):
        self.names = ['release_time']
        self.converter = {'release_time': np.datetime64}
        for name, dtype in setup.particle_variables:
            self.names.append(name)
            self.converter[name] = dtype
        for name in self.names:
            setattr(self, name, np.array([], dtype=self.converter[name]))

    # Shorthand to use self[name] for getattr(self, name)
    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)


class State(object):
    """Class holding model state variables"""

    def __init__(self, setup):
        self.names = ['pid', 'X', 'Y', 'Z']
        self.converter = {
            'pid': int,
            'X': float,
            'Y': float,
            'Z': float}
        for name, dtype in setup.state_variables:
            self.names.append(name)
            if dtype == 'int':
                self.converter[name] = int
            else:
                self.converter[name] = float
        for name in self.names:
            setattr(self, name, np.array([], dtype=self.converter[name]))

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __len__(self):
        return len(getattr(self, 'X'))

    # Sjekk om denne må forbedres
    def addstate(self, other):
        """Concatenate states"""
        # Bør ha kontroll, samme navn, ellers udefinert
        for v in self.names:
            setattr(self, v,
                    np.concatenate((getattr(self, v), getattr(other, v))))

# --------------------------------

#        # Add to overall state
#        for name in self.state.names:
#            self.state[name] = np.concatenate(
#                (self.state[name], more_state[name]))
#        for name in self.particle_variables.names:
#            self.particle_variables[name] = np.concatenate(
#                (self.particle_variables[name], more_particles[name]))

#
#    def close(self):
#        self.fid.close()


# ==================================================


if __name__ == "__main__":

    # Lag et lite test-script uavhengig av hele modellen

    #    import sys
    from config import read_config

    configuration = read_config('../ladim.sup')
    pvar = ParticleVariables(configuration)
    print('\nParticle variables:')
    print(pvar.names)
    state = State(configuration)
    print('\nState variables:')
    print(state.names)
