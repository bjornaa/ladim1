# -*- coding: utf-8 -*-

# Particle release class


# Sequence:
# date clock mult X Y Z [particle_variables] [state_variables]
# date must have format yyyy-mm-dd
# clock can have hh:mm:ss, hh:mm or simply 0-23 for hour only
# The number and order of particle_variables and state_variables
# are given by the names attribute in the ParticleVariables and State
# instances

# Example: salmon lice
# date clock mult X Y Z farm_id age super
# 2016-03-11 6 3 366 464 5 10147 0 1000

import numpy as np
# from ladim_state import ParticleVariables, State

# ------------------------


def time_step(config, dtime):
    return (np.timedelta64(dtime - config.start_time, 's').astype(int) //
            config.dt)


class ParticleReleaser(object):

    def __init__(self, config, particle_vars, state):
        # Missing control that fields add upp
        # Init state e.t.c. separately

        # Open the file and init counters
        self.fid = open(config.particle_release_file)
        self.particle_count = 0
        self.release_step = 0

        # Initiate empty state
        # self.particle_variables = ParticleVariables(config)
        # self.state = State(config)
        # TODO: Ikke gjenta eksplisitt her
        self.release_names = (
            ['release_time', 'mult'] +
            ['X', 'Y', 'Z'] +
            particle_vars.names[1:] +    # Exclude release_time here
            state.extra_names)

        self.converter = dict(mult=int)
        for name in state.names:
            self.converter[name] = state.converter[name]
        for name in particle_vars.names:
            self.converter[name] = particle_vars.converter[name]

        # Read first line
        line = next(self.fid)

        # dtime = np.datetime64(line.split()[0])
        # tdelta = np.timedelta64(dtime - config.start_time, 's')
        # self.next_release = tdelta.astype(int) / config.dt

        self.next_release = time_step(config, np.datetime64(line.split()[0]))
        self.next_line = line
        # print(line, self.next_release)

        self.config = config
        self.dt = config.dt
        self.start_time = config.start_time

    # ------
    def release_particles(self, particle_vars, state, timestep):

        release_data = dict()
        release_data['pid'] = []
        for name in self.release_names:
            release_data[name] = []

        # Read all lines at this time step + next line
        while True:
            line = self.next_line    # From previous
            try:
                self.next_line = next(self.fid)   # Read one line aheaad
                self.next_release = time_step(
                    self.config, np.datetime64(self.next_line.split()[0]))
            except StopIteration:  # End of file
                self.next_release = -999

            # Parse the line
            w = line.split()
            parsed_line = dict()
            for i, name in enumerate(self.release_names):
                parsed_line[name] = self.converter[name](w[i])
            mult = parsed_line['mult']

            for i in range(mult):
                self.particle_count += 1
                # pid is zero-based
                release_data['pid'].append(self.particle_count - 1)

            for name in set(self.release_names):
                release_data[name].extend(mult*[parsed_line[name]])

            break

        # Append to the state
        for name in particle_vars.names:
            particle_vars[name] = np.concatenate(
                (particle_vars[name], release_data[name]))
        for name in state.names:
            state[name] = np.concatenate(
                (state[name], release_data[name]))

    def close(self):
        self.fid.close()


# ==================================================

if __name__ == "__main__":

    # Få referanse til input/*in via ladim.sup
    # Virker ikke med relative adresser fordi feil katalog

    import sys
    from config import read_config
    from ladim_state import ParticleVariables, State

    config = read_config('../ladim.sup')
    config.particle_release_file = '../input/lice.in'

    pvars = ParticleVariables(config)
    state = State(config)

    # Take optional release file from command line
    if len(sys.argv) > 1:
        config.particle_release_file = sys.argv[1]

    p = ParticleReleaser(config, pvars, state)

    while p.next_release >= 0:

        print('time_step, number of particles = ', p.next_release, end=', ')
        p.release_particles(pvars, state, p.next_release)
        print(p.particle_count)
        print

    p.close()

    print(p.particle_count)
    print(state.pid)
    print(state.X)
    print(pvars.farmid)
    print(pvars.release_time)
