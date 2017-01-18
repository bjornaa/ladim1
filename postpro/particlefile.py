# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset, num2date

# Methods:
#  get_positions : all positions at time n (flag for lon, lat?)
#  get_variable_distribution : all variables at time n
#
#  active(p, n) : 1  if p is active at time n
#                 0  if p is not released (yet)
#                 -1 if p is deactivated
# Bedre navn: status?, activity_status
#  first_time(p) : First time times it is active
#  last_time(p)  : Last time it is active
#


class ParticleFile(object):

    def __init__(self, filename):
        self.nc = Dataset(filename)
        # Change Time to time (or allow both)
        self.ntimes = len(self.nc.dimensions['time'])
        self.particle_count = self.nc.variables['particle_count'][:]

    def get_time(self, n):
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)

    def get_position(self, n):
        """Get particle positions at n-th time times"""
        f = self.nc
        start = self.particle_count[:n-1].sum()
        count = self.particle_count[n]
        X = f.variables['X'][start:start+count]
        Y = f.variables['Y'][start:start+count]
        return X, Y

    def get_variable(self, n, vname):
        """Get values of a particle variable"""
        f = self.nc
        start = self.particle_count[:n].sum()
        count = self.particle_count[n]
        # print('start, count =', start, count)
        # put in some error control
        return f.variables[vname][start:start+count]

    # Alternativ: gi en default verdi om ikke aktiv
    #    Evt. raise exception
    # ha en separat sjekk på aktivitet
    def get_particle_variable(self, p, n, vname):
        """Get variable vname at time step n at particle p

        Returns value, active
        where: active = 0  if particle is not released (yet)
                      = -1 if particle has been active but is now closed
                      = 1  if particle is active
               value = value at particle at time n, if active
                     = ha en fill value if not active

        """

        pid = self.get_variable(n, 'pid')

        if pid[-1] < p:  # particle not released yet
            pass
            # active = 0

        index = pid.searchsorted(p)
        if pid[index] < p:      # p is missing, but has been active
            pass
            # active = -1

        # A = self.get_variable(n, vname)

# ------------------------------

    def read_track(self, p):
        """Get particle positions along a single track"""

        f = self.nc
        X, Y = [], []
        first_time = None
        last_time = None

        # After loop
        # particle is alive for n in [first_time:last_time]
        # or to the end if last_time == 0

        for n in range(self.ntimes):
            # Kan speede opp, trenger ikke summere alt hver gang
            start = self.particle_count[:n].sum()
            count = self.particle_count[n]
            pid = f.variables['pid'][start:start+count]

            if pid[-1] < p:  # particle not released yet
                continue

            if first_time is not None:
                first_time = n

            # index = sum(pid < p) # eller lignende
            index = pid.searchsorted(p)
            if pid[index] < p:  # p is missing
                last_time = n     #
                break             # No need for more cycles

            X.append(f.variables['X'][start + index])
            Y.append(f.variables['Y'][start + index])

        return X, Y, first_time, last_time

# ----------------------------------

# Ikke testet nok for udefinerte partikler
# f.eks. for store => I[J] blir upassende

    def read_tracks(self, P):
        """Get particle positions along tracks

        Returns an array of shape (len(P),ntimes)
        with NaN where particles are undefined

        """

        P = np.asarray(P)
        nP = len(P)

        f = self.nc

        X = np.nan + np.zeros((self.ntimes, nP))
        Y = np.nan + np.zeros((self.ntimes, nP))

        for n in range(self.ntimes):
            # Kan speede opp, trenger ikke summere alt hver gang
            start = self.particle_count[:n].sum()
            count = self.particle_count[n]
            tslice = slice(start, start+count)   # time slice
            pid = f.variables['pid'][tslice]

            I = pid.searchsorted(P+1)
            J, = np.nonzero(I == pid[I-1])

            Xn = f.variables['X'][tslice]
            Yn = f.variables['Y'][tslice]

            X[n, J] = Xn[I[J]]
            Y[n, J] = Yn[I[J]]

        return X, Y

    def close(self):
        self.nc.close()
