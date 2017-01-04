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
from ladim_state import ParticleVariables, State

# ------------------------


def time_step(setup, dtime):
    return (np.timedelta64(dtime - setup.start_time, 's').astype(int) //
            setup.dt)


class ParticleReleaser(object):

    def __init__(self, setup):
        # Missing control that fields add upp
        # Init state e.t.c. separately

        # Open the file and init counters
        self.fid = open(setup.particle_release_file)
        self.particle_counter = 0
        self.release_step = 0

        # Initiate empty state
        self.particle_variables = ParticleVariables(setup)
        self.state = State(setup)
        # TODO: Ikke gjenta eksplisitt her
        self.read_variables = (
            list(zip(['release_time', 'mult', 'X', 'Y', 'Z'],
                     [np.datetime64, int, float, float, float])) +
            setup.particle_variables + setup.state_variables)

        # print(self.variables)

        # Read first line
        line = next(self.fid)

        # dtime = np.datetime64(line.split()[0])
        # tdelta = np.timedelta64(dtime - setup.start_time, 's')
        # self.next_release = tdelta.astype(int) / setup.dt

        self.next_release = time_step(setup, np.datetime64(line.split()[0]))
        self.next_line = line
        # print(line, self.next_release)

        self.dt = setup.dt
        self.start_time = setup.start_time

    # ------
    def release_particles(self, setup, timestep):

        more_particles = dict()
        for name in self.particle_variables.names:
            more_particles[name] = []
        more_state = dict()
        for name in self.state.names:
            more_state[name] = []
        while True:
            line = self.next_line
            try:
                line1 = next(self.fid)  # Read one line aheaad
                self.next_line = line1
                self.next_release = time_step(
                    setup, np.datetime64(line1.split()[0]))
            except StopIteration:  # End of file
                self.next_release = -999
            # print("release: next = ", self.next_release)

            w = line.split()
            parsed_line = dict()
            for i, (name, converter) in enumerate(self.read_variables):
                parsed_line[name] = converter(w[i])
            # print(parsed_line)

            mult = parsed_line['mult']

            for name in self.particle_variables.names:
                more_particles[name].extend(mult*[parsed_line[name]])

            for name in self.state.names[1:]:   # excluding pid
                more_state[name].extend(mult*[parsed_line[name]])

            # Skal pid starte med null (eller 1 som her)
            for m in range(mult):
                self.particle_counter += 1
                more_state['pid'].append(self.particle_counter)

            if self.next_release != timestep:  # Finished this time step
                break

            # print(more_state)

        # Add to overall state
        for name in self.state.names:
            self.state[name] = np.concatenate(
                (self.state[name], more_state[name]))
        for name in self.particle_variables.names:
            self.particle_variables[name] = np.concatenate(
                (self.particle_variables[name], more_particles[name]))

    def close(self):
        self.fid.close()


# ==================================================

if __name__ == "__main__":

    # Få referanse til input/*in via ladim.sup
    # Virker ikke med relative adresser fordi feil katalog

    import sys
    from config import read_config

    setup = read_config('../ladim.sup')
    setup.particle_release_file = '../input/lice.in'

    # Take optional release file from command line
    if len(sys.argv) > 1:
        setup.particle_release_file = sys.argv[1]

    p = ParticleReleaser(setup)

    while p.next_release >= 0:

        print('time_step, number of particles = ', p.next_release, end=', ')
        p.release_particles(setup, p.next_release)
        print(p.particle_counter)
        print

    p.close()

    print(p.particle_counter)
    print(p.state.pid)
    print(p.state.X)
    print(p.particle_variables.farmid)
    print(p.particle_variables.release_time)
    print(p.state)
