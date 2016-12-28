# -*- coding: utf-8 -*-

# Particle release class

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

    def __getitem__(self, name):
        return getattr(self, name)


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

    def __len__(self):
        return len(getattr(self, self.X))

    def addstate(self, other):
        """Concatenate states"""
        # Bør ha kontroll, samme navn, ellers udefinert
        for v in self.names:
            setattr(self, v,
                    np.concatenate((getattr(self, v), getattr(other, v))))

# --------------------------------


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

        # Read first line
        line = next(self.fid)
        next_time = np.datetime64('T'.join(line.split()[1:3]))
        tdelta = np.timedelta64(next_time - setup.start_time, 's').astype(int)
        self.next_time = tdelta / setup.dt
        self.next_line = line

        self.dt = setup.dt
        self.start_time = setup.start_time

    # ------
    def release_particles(self, timestep):  # Leser til neste "T"

        append = dict()
        for name in self.state.names:
            append[name] = []
        while True:
            line = self.next_line
            self.next_line = next(self.fid)  # Read one line aheaad
            w = line.split()
            timestamp = np.datetime64('T'.join(w[1:3]))
            release_step = np.timedelta64(timestamp-self.start_time, 's')
            release_step = release_step.astype(int) / self.dt
            if release_step > timestep:
                # Append to state
                for name in self.state.names:
                    np.concatenate((self.state[name], append[name]))
                self.next_time = release_step
                break
            mult = int(w[0])
            self.particle_counter += 1
            append['pid'].extend(list(
                range(self.particle_counter, self.particle_counter+mult)))
            self.particle_counter += mult - 1
            for i, name in enumerate(self.state.names[1:]):
                print(i, name, w[i+3])
                append[name].extend(mult*[self.state.converter[name](w[3+i])])
            print(append)

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

    while 1:

        # print "==> ", p.release_step, p.particle_counter
        p.release_particles(0)
        q = p.state
        # print p.X
        for i in range(len(q)):
            print("%8d %8.2f %8.2f %8.2f %6d" % (
                q.pid[i], q.X[i], q.Y[i], q.Z[i], q.start[i]))
        if p.release_step < 0:
            break

    p.close()

    # print p.X
